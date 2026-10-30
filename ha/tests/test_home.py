import json

from conftest import FIX
from custom_components.umote.home import build_tiles

REG = json.loads((FIX / "registry.json").read_text())
FANS = ("fan.tv_fan", "fan.fridge_fan", "fan.clock_fan")
CAB_LIGHTS = [f"light.tv_cabinet_tv_cabinet_light_{n}" for n in (1, 2, 3, 4)] + ["light.tv_cabinet_tv_cabinet_bottom_light"]


def states(**over):
    st = {e["entity_id"]: {"state": "off", "attributes": {}} for e in REG["entities"]}
    for f in FANS:
        st[f] = {"state": "off", "attributes": {"percentage": 0, "percentage_step": 16.666666666666668}}
    st.update(over)
    return st


def tiles(**over):
    return build_tiles(REG["entities"], REG["devices"], states(**over), "living_room")


def tile(ts, name):
    return next(t for t in ts if t["name"] == name)


def test_tiles_for_living_room():
    ts = tiles()
    assert {t["name"] for t in ts} == {"TV fan", "Fridge fan", "Clock fan", "Cabinet lights", "Cabinet power", "Matrix clock"}
    fan = tile(ts, "TV fan")
    assert fan["kind"] == "fan" and fan["icon"] == "fan" and fan["entities"] == ["fan.tv_fan"]
    assert fan["options"] == {"led": "light.tv_fan_led", "speed_count": 6, "timer": "select.tv_fan_set_timer"}
    clock = tile(ts, "Matrix clock")
    assert clock["kind"] == "display" and clock["icon"] == "clock"
    assert clock["options"] == {"brightness": "number.living_room_weather_matrix_matrix_brightness"}
    assert tile(ts, "Cabinet power")["icon"] == "plug" and len(tile(ts, "Cabinet power")["entities"]) == 3
    assert tile(ts, "Cabinet lights")["entities"] == sorted(CAB_LIGHTS)


def test_fan_label_shows_speed_when_on():
    on = {"state": "on", "attributes": {"percentage": 50, "percentage_step": 16.666666666666668}}
    ts = tiles(**{"fan.tv_fan": on})
    assert tile(ts, "TV fan")["label"] == "Speed 3" and tile(ts, "TV fan")["state"] == "on"
    assert tile(ts, "Fridge fan")["label"] == "Off"
    assert ts[0]["name"] == "TV fan"                 # on tiles first


def test_unavailable_is_offline_not_off():
    t = tile(tiles(**{"fan.clock_fan": {"state": "unavailable", "attributes": {}}}), "Clock fan")
    assert t["state"] == "offline" and t["label"] == "Offline"


def test_group_state_on_if_any_member_on():
    t = tile(tiles(**{CAB_LIGHTS[0]: {"state": "on", "attributes": {}}}), "Cabinet lights")
    assert t["state"] == "on" and t["label"] == "1 on"


def test_other_areas_ignored():
    ids = {e for t in tiles() for e in t["entities"]}
    assert "light.desktop_automation_onboard_led" not in ids
    assert not any(i.startswith(("media_player.", "remote.", "sensor.", "update.", "select.")) for i in ids)
