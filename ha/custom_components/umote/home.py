"""Group Living Room entities into remote tiles. Pure functions."""
from __future__ import annotations

from .const import AREA_PREFIXES, SHORT_NAMES

OFFLINE = ("unavailable", "unknown")


def _short(device: dict) -> str:
    raw = device.get("name_by_user") or device.get("name") or ""
    if raw in SHORT_NAMES:
        return SHORT_NAMES[raw]
    name = raw.replace("_", " ").strip()
    for p in AREA_PREFIXES:
        if name.lower().startswith(p):
            name = name[len(p):]
    return _sentence(name)


def _sentence(name: str) -> str:
    # Sentence case, keeping acronyms such as "TV".
    words = [w if w.isupper() and len(w) > 1 else w.lower() for w in name.split()]
    return " ".join(words)[:1].upper() + " ".join(words)[1:]


def _member_name(entity: dict, device: dict, states: dict) -> str:
    """A light's or switch's own name without its device's: "TV Cabinet Light 1" -> "Light 1"."""
    eid = entity["entity_id"]
    raw = (entity.get("name") or states.get(eid, {}).get("attributes", {}).get("friendly_name")
           or eid.split(".", 1)[1])
    name = " ".join(raw.replace("_", " ").split())
    prefixes = {(device.get(k) or "").replace("_", " ").lower().strip() for k in ("name", "name_by_user")} - {""}
    stripped = True
    while stripped:
        stripped = False
        for p in sorted(prefixes, key=len, reverse=True):
            if name.lower().startswith(p + " "):
                name, stripped = name[len(p) + 1:], True
    return _sentence(name)


def _member(entity: dict, device: dict, states: dict) -> dict:
    """One row of the remote's device menu: name, state, and brightness in percent when it dims."""
    st = states.get(entity["entity_id"], {})
    state, attrs = st.get("state", "unavailable"), st.get("attributes", {})
    m = {"n": _member_name(entity, device, states), "s": "offline" if state in OFFLINE else state}
    if any(mode != "onoff" for mode in attrs.get("supported_color_modes") or ()):
        m["b"] = round((attrs.get("brightness") or 0) * 100 / 255) if state == "on" else 0
    return m


def _number_member(entity_id: str, states: dict) -> dict:
    st = states.get(entity_id, {})
    attrs = st.get("attributes", {})
    lo, hi = attrs.get("min", 0), attrs.get("max", 100)
    try:
        pct = round((float(st.get("state")) - lo) * 100 / (hi - lo))
    except (TypeError, ValueError, ZeroDivisionError):
        pct = 0
    return {"n": "Brightness", "s": "offline" if st.get("state", "unavailable") in OFFLINE else "on",
            "b": max(0, min(100, pct)), "lo": lo, "hi": hi}


def _state(ids: list[str], states: dict) -> tuple[str, int]:
    vals = [states.get(i, {}).get("state", "unavailable") for i in ids]
    if all(v in OFFLINE for v in vals):
        return "offline", 0
    on = sum(v == "on" for v in vals)
    return ("on" if on else "off"), on


def _tile(dev_id, suffix, name, kind, icon, ids, states, label_on, options):
    state, on = _state(ids, states)
    label = {"offline": "Offline", "off": "Off"}.get(state) or label_on(on)
    return {"id": f"{dev_id}_{suffix}", "name": name, "kind": kind, "icon": icon, "state": state,
            "label": label, "entities": ids, "options": options}


def build_tiles(entities: list[dict], devices: dict[str, dict], states: dict[str, dict], area: str) -> list[dict]:
    return build_home(entities, devices, states, area)[0]


def build_home(entities: list[dict], devices: dict[str, dict], states: dict[str, dict],
               area: str) -> tuple[list[dict], dict[str, list[dict]]]:
    """(tiles, members). members[tile id] lists what the tile's menu shows, in the order of the
    tile's entities: one row per light or switch, or the display's brightness."""
    by_id = {e["entity_id"]: e for e in entities}
    members: dict[str, list[dict]] = {}
    by_dev: dict[str, list[str]] = {}
    for e in entities:
        dev = devices.get(e.get("device_id") or "", {})
        if (e.get("area_id") or dev.get("area_id")) != area or e.get("hidden_by") or e.get("disabled_by"):
            continue
        # Fan timers are config entities but drive the options sheet.
        if e.get("entity_category") and not e["entity_id"].startswith("select."):
            continue
        by_dev.setdefault(e.get("device_id") or e["entity_id"], []).append(e["entity_id"])

    tiles = []
    for dev_id, ids in by_dev.items():
        ids.sort()
        dom = lambda d: [i for i in ids if i.startswith(d + ".")]  # noqa: E731
        fans, lights, switches, numbers = dom("fan"), dom("light"), dom("switch"), dom("number")
        name = _short(devices.get(dev_id, {"name": dev_id}))
        if fans:
            attrs = states.get(fans[0], {}).get("attributes", {})
            step = attrs.get("percentage_step") or 100
            opts = {"led": lights[0] if lights else None, "speed_count": round(100 / step)}
            timers = [i for i in dom("select") if i.endswith("_timer")]
            if timers:
                opts["timer"] = timers[0]
            speed = lambda _on, a=attrs, s=step: f"Speed {round((a.get('percentage') or 0) / s)}"  # noqa: E731
            tiles.append(_tile(dev_id, "fan", name, "fan", "fan", fans[:1], states, speed, opts))
            continue
        if switches and numbers and not lights:
            tiles.append(_tile(dev_id, "display", name, "display", "clock", switches[:1], states,
                               lambda _on: "On", {"brightness": numbers[0]}))
            members[tiles[-1]["id"]] = [_number_member(numbers[0], states)]
            continue
        if lights:
            tiles.append(_tile(dev_id, "lights", f"{name} lights", "lights", "bulb", lights, states,
                               lambda on: f"{on} on", {}))
            members[tiles[-1]["id"]] = [_member(by_id[i], devices.get(dev_id, {}), states) for i in lights]
        if switches:
            tiles.append(_tile(dev_id, "switches", f"{name} power", "switches", "plug", switches, states,
                               lambda on: f"{on} on", {}))
            members[tiles[-1]["id"]] = [_member(by_id[i], devices.get(dev_id, {}), states) for i in switches]
    # A fixed order: sorting "on" first made every tile jump the moment it was tapped.
    tiles.sort(key=lambda t: (t["name"].lower(), t["id"]))
    return tiles, members
