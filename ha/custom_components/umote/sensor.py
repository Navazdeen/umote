"""sensor.umote_sources and sensor.umote_home."""
from __future__ import annotations

import json

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import AREA
from .coordinator import UmoteCoordinator
from .home import build_tiles


def _json(value) -> str:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    async_add_entities([SourcesSensor(entry.runtime_data), HomeSensor()])


class SourcesSensor(CoordinatorEntity[UmoteCoordinator], SensorEntity):
    _attr_unique_id = "umote_sources"
    _attr_name = "umote sources"
    _attr_icon = "mdi:remote-tv"
    _unrecorded_attributes = frozenset({"sources", "quick", "more", "current", "tv_on", "updated"})

    def __init__(self, coordinator: UmoteCoordinator) -> None:
        super().__init__(coordinator)
        self.entity_id = "sensor.umote_sources"

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data["sources"])

    @property
    def extra_state_attributes(self) -> dict:
        # HA sends attributes to ESPHome as str(value), so lists go out as JSON text.
        d = self.coordinator.data
        return {"sources": _json(d["sources"]), "quick": _json(d["quick"]), "more": _json(d["more"]),
                "current": d["current"] or "", "tv_on": d["tv_on"], "updated": d["updated"]}


class HomeSensor(SensorEntity):
    """Living Room tiles; rebuilt when an area entity or the registries change."""

    _attr_unique_id = "umote_home"
    _attr_name = "umote home"
    _attr_icon = "mdi:sofa"
    _attr_should_poll = False
    _unrecorded_attributes = frozenset({"tiles"})

    def __init__(self) -> None:
        self.entity_id = "sensor.umote_home"
        self._tiles: list[dict] = []
        self._ids: set[str] = set()

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.hass.bus.async_listen(EVENT_STATE_CHANGED, self._on_state, self._watched))
        for event in (er.EVENT_ENTITY_REGISTRY_UPDATED, dr.EVENT_DEVICE_REGISTRY_UPDATED):
            self.async_on_remove(self.hass.bus.async_listen(event, self._on_registry))
        self._rebuild()

    @callback
    def _watched(self, event_data) -> bool:
        return event_data["entity_id"] in self._ids

    @callback
    def _on_state(self, _event: Event) -> None:
        self._rebuild()
        self.async_write_ha_state()

    @callback
    def _on_registry(self, _event: Event) -> None:
        self._on_state(_event)

    @callback
    def _rebuild(self) -> None:
        ents = er.async_get(self.hass)
        devs = dr.async_get(self.hass)
        entities = [{"entity_id": e.entity_id, "device_id": e.device_id, "area_id": e.area_id,
                     "entity_category": e.entity_category, "hidden_by": e.hidden_by,
                     "disabled_by": e.disabled_by} for e in ents.entities.values()]
        devices = {d.id: {"id": d.id, "name": d.name, "name_by_user": d.name_by_user, "area_id": d.area_id}
                   for d in devs.devices.values()}
        states = {s.entity_id: {"state": s.state, "attributes": dict(s.attributes)}
                  for s in self.hass.states.async_all(("fan", "light", "switch", "number"))}
        self._tiles = build_tiles(entities, devices, states, AREA)
        self._ids = {i for t in self._tiles for i in t["entities"]}

    @property
    def native_value(self) -> int:
        return len(self._tiles)

    @property
    def extra_state_attributes(self) -> dict:
        return {"tiles": _json(self._tiles)}
