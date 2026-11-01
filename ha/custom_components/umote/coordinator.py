"""Reads the TV over HA's Android TV (ADB) integration and keeps names and usage."""
from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import timedelta

from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.event import async_call_later, async_track_state_change_event
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import (CMD_HDMI, CMD_PACKAGES, CMD_TV_INPUT, DOMAIN, HOME_SETTLE_S, MAX_ATTR_BYTES,
                    SCAN_INTERVAL_S, SYSTEM_PACKAGES, TV_ADB, TV_PLAYER, TV_REMOTE, USE_AFTER_S,
                    WAKE_TIMEOUT_S)
from .sources import build_sources, source_id_for_activity
from .tvparse import App, Input, parse_apps, parse_current_input, parse_inputs

_LOGGER = logging.getLogger(__name__)
OFF_STATES = ("off", "standby", "unavailable", "unknown")


PUBLISHED = ("id", "kind", "name", "port", "color", "icon")   # what the remote reads


def fit_attributes(data: dict) -> dict:
    """Keep the published JSON under MAX_ATTR_BYTES: only the fields the remote reads,
    then drop collapsed apps' details, then apps from the end."""
    data = {**data, "sources": [{k: s[k] for k in PUBLISHED} for s in data["sources"]]}
    if len(json.dumps(data)) <= MAX_ATTR_BYTES:
        return data
    more = set(data["more"])
    data = {**data, "sources": [s for s in data["sources"] if s["id"] not in more]}
    while len(json.dumps(data)) > MAX_ATTR_BYTES and data["sources"][-1]["kind"] == "app":
        data["sources"] = data["sources"][:-1]
    return data


class UmoteCoordinator(DataUpdateCoordinator[dict]):
    """data = {sources, quick, more, current, tv_on, updated}."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, config_entry=entry,
                         update_interval=timedelta(seconds=SCAN_INTERVAL_S))
        self._names_store: Store = Store(hass, 1, "umote.names")
        self._usage_store: Store = Store(hass, 1, "umote.usage")
        self._tv_store: Store = Store(hass, 1, "umote.tv")   # last inputs/apps, for when the TV sleeps
        self.names: dict[int, str] = {}
        self.usage: dict[str, list] = {}
        self._inputs: list = []
        self._apps: list = []
        self._current_input: int | None = None
        self._pending_use = None

    async def async_load(self) -> None:
        self.names = {int(k): v for k, v in ((await self._names_store.async_load()) or {}).items()}
        self.usage = (await self._usage_store.async_load()) or {}
        tv = (await self._tv_store.async_load()) or {}
        self._inputs = [Input(**i) for i in tv.get("inputs", [])]
        self._apps = [App(a) for a in tv.get("apps", [])]

    def tv_snapshot(self) -> dict:
        return {"inputs": [vars(i) for i in self._inputs], "apps": [a.package for a in self._apps]}

    @callback
    def async_track(self) -> callback:
        unsub_remote = async_track_state_change_event(self.hass, [TV_REMOTE], self._on_remote_change)
        unsub_adb = async_track_state_change_event(self.hass, [TV_ADB], self._on_adb_change)

        def unsub() -> None:
            unsub_remote()
            unsub_adb()
        return unsub

    @callback
    def _on_adb_change(self, event: Event) -> None:
        """ADB usually comes back a little after the TV wakes: read the TV then."""
        old, new = event.data.get("old_state"), event.data.get("new_state")
        was_down = old is None or old.state in ("unavailable", "unknown", "off")
        if new is not None and new.state not in ("unavailable", "unknown", "off") and was_down:
            # not the debounced request: it usually lands inside the cooldown of the remote's refresh
            self.hass.async_create_task(self.async_refresh())

    # ---- reading the TV -------------------------------------------------------------------
    def tv_on(self) -> bool:
        st = self.hass.states.get(TV_REMOTE)
        return bool(st and st.state not in OFF_STATES)

    async def _adb(self, command: str) -> str | None:
        st = self.hass.states.get(TV_ADB)
        if not st or st.state in ("unavailable", "unknown", "off"):
            return None
        try:
            await self.hass.services.async_call("androidtv", "adb_command",
                                                {"entity_id": TV_ADB, "command": command}, blocking=True)
        except (HomeAssistantError, ValueError) as err:
            _LOGGER.debug("adb_command %s failed: %s", command, err)
            return None
        st = self.hass.states.get(TV_ADB)
        return st.attributes.get("adb_response") if st else None

    async def _async_update_data(self) -> dict:
        tv_on = self.tv_on()
        if tv_on:
            tv_input, hdmi, pkgs = [await self._adb(c) for c in (CMD_TV_INPUT, CMD_HDMI, CMD_PACKAGES)]
            if tv_input is not None and hdmi is not None and pkgs is not None:
                self._inputs = parse_inputs(tv_input, hdmi) or self._inputs
                self._apps = parse_apps(pkgs, SYSTEM_PACKAGES) or self._apps
                self._current_input = parse_current_input(hdmi)
                self._seed_usage()
                self._tv_store.async_delay_save(self.tv_snapshot, 5)
            else:
                tv_on = False    # standby closes ADB; keep the last lists
        return self._publish(tv_on)

    def _seed_usage(self) -> None:
        now = time.time()
        new = {a.package for a in self._apps} - set(self.usage)
        for p in new:
            self.usage[p] = [0, now]
        if new:
            self._usage_store.async_delay_save(lambda: self.usage, 5)

    def _current(self) -> str | None:
        st = self.hass.states.get(TV_REMOTE)
        activity = st.attributes.get("current_activity") if st and st.state == "on" else None
        return source_id_for_activity(activity, self._current_input)

    def _publish(self, tv_on: bool) -> dict:
        usage = {k: (int(v[0]), float(v[1])) for k, v in self.usage.items()}
        out = build_sources(self._inputs, self._apps, self.names, usage, time.time(),
                            self._current() if tv_on else None)
        self.all_sources = out["sources"]
        return {**fit_attributes(out), "tv_on": tv_on, "updated": dt_util.utcnow().isoformat()}

    # ---- usage ------------------------------------------------------------------------------
    @callback
    def _on_remote_change(self, event: Event) -> None:
        old, new = event.data.get("old_state"), event.data.get("new_state")
        if self._pending_use:
            self._pending_use()
            self._pending_use = None
        sid = self._current()
        if sid:
            self._pending_use = async_call_later(self.hass, USE_AFTER_S, self._count_if_still(sid))
        changed = (old is None or new is None or old.state != new.state
                   or old.attributes.get("current_activity") != new.attributes.get("current_activity"))
        if changed:
            self.hass.async_create_task(self.async_request_refresh())

    def _count_if_still(self, sid: str):
        @callback
        def _fire(_now) -> None:
            self._pending_use = None
            if self._current() == sid:
                self.count_use(sid)
        return _fire

    @callback
    def count_use(self, sid: str) -> None:
        uses = self.usage.get(sid, [0, 0])[0]
        self.usage[sid] = [uses + 1, time.time()]
        self._usage_store.async_delay_save(lambda: self.usage, 1)

    @callback
    def async_shutdown_tracking(self) -> None:
        if self._pending_use:
            self._pending_use()
            self._pending_use = None

    # ---- services ---------------------------------------------------------------------------
    async def async_launch(self, source_id: str) -> None:
        src = next((s for s in getattr(self, "all_sources", []) if s["id"] == source_id), None)
        if src is None:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="unknown_source",
                                         translation_placeholders={"source_id": source_id})
        try:
            async with asyncio.timeout(WAKE_TIMEOUT_S):
                while not self.tv_on():
                    await asyncio.sleep(0.5)
        except TimeoutError as err:
            raise HomeAssistantError("The TV did not wake up") from err
        await self.hass.services.async_call("remote", "send_command",
                                            {"entity_id": TV_REMOTE, "command": "HOME"}, blocking=True)
        await asyncio.sleep(HOME_SETTLE_S)
        kind, content = ("url", src["target"]) if src["kind"] == "input" else ("app", src["target"])
        await self.hass.services.async_call("media_player", "play_media",
                                            {"entity_id": TV_PLAYER, "media_content_type": kind,
                                             "media_content_id": content}, blocking=True)
        self.count_use(source_id)
        self.async_set_updated_data(self._publish(True))

    async def async_name_source(self, port: int, name: str) -> None:
        name = name.strip()
        if name:
            self.names[port] = name
        else:
            self.names.pop(port, None)
        await self._names_store.async_save({str(k): v for k, v in self.names.items()})
        self.async_set_updated_data(self._publish(self.tv_on()))
