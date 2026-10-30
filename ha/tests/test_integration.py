import json

import pytest
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import area_registry as ar, device_registry as dr, entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_mock_service

from conftest import FIX, fx
from custom_components.umote import coordinator as coord_mod
from custom_components.umote.const import CMD_HDMI, CMD_PACKAGES, CMD_TV_INPUT, DOMAIN, TV_ADB, TV_CAST, TV_REMOTE

RESPONSES = {CMD_TV_INPUT: "tv_input.txt", CMD_HDMI: "hdmi_control.txt", CMD_PACKAGES: "packages.txt"}


@pytest.fixture(autouse=True)
def auto_enable(enable_custom_integrations):
    yield


@pytest.fixture(autouse=True)
def fast(monkeypatch):
    monkeypatch.setattr(coord_mod, "HOME_SETTLE_S", 0)


class MockAdb:
    def __init__(self, hass: HomeAssistant):
        self.hass, self.up = hass, True
        hass.states.async_set(TV_REMOTE, "on", {"current_activity": "com.netflix.ninja"})
        hass.states.async_set(TV_ADB, "playing", {})
        hass.services.async_register("androidtv", "adb_command", self._cmd)

    async def _cmd(self, call: ServiceCall):
        if not self.up:
            return
        self.hass.states.async_set(TV_ADB, "playing", {"adb_response": fx(RESPONSES[call.data["command"]])})

    def go_unavailable(self):
        self.up = False
        self.hass.states.async_set(TV_ADB, "unavailable", {})
        self.hass.states.async_set(TV_REMOTE, "off", {})


@pytest.fixture
def mock_adb(hass):
    return MockAdb(hass)


async def setup(hass):
    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def refresh(hass):
    await hass.config_entries.async_loaded_entries(DOMAIN)[0].runtime_data.async_refresh()
    await hass.async_block_till_done()


async def test_config_flow_creates_single_entry(hass):
    res = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    assert res["type"] == "form"
    res = await hass.config_entries.flow.async_configure(res["flow_id"], {})
    assert res["type"] == "create_entry"


async def test_sources_sensor_publishes_json(hass, mock_adb):
    await setup(hass)
    st = hass.states.get("sensor.umote_sources")
    assert st.attributes["sources"][0]["id"] == "hdmi1"
    assert st.attributes["sources"][0]["name"] == "PlayStation 5"
    assert st.attributes["tv_on"] is True and st.attributes["current"] == "com.netflix.ninja"
    assert len(json.dumps({k: st.attributes[k] for k in ("sources", "quick", "more", "current")})) <= 3072
    assert int(st.state) == len(st.attributes["sources"])


async def test_coordinator_keeps_last_sources_when_adb_unavailable(hass, mock_adb, caplog):
    await setup(hass)
    mock_adb.go_unavailable()
    await refresh(hass)
    st = hass.states.get("sensor.umote_sources")
    assert st.state != "unavailable"
    assert st.attributes["sources"] and st.attributes["tv_on"] is False
    assert "ERROR" not in caplog.text


async def test_launch_input_sends_home_then_passthrough(hass, mock_adb):
    await setup(hass)      # media_player loads first, then the mocks replace its services
    order = []
    hass.services.async_register("remote", "send_command", lambda c: order.append(("remote", c.data["command"])))
    hass.services.async_register("media_player", "play_media",
                                 lambda c: order.append((c.data["media_content_type"], c.data["media_content_id"])))
    await hass.services.async_call(DOMAIN, "launch", {"source_id": "hdmi1"}, blocking=True)
    assert order == [("remote", "HOME"), ("url", "content://android.media.tv/passthrough/"
                                                  "com.mediatek.tvinput%2F.hdmi.HDMIInputService%2FHW4")]
    await hass.services.async_call(DOMAIN, "launch", {"source_id": "com.netflix.ninja"}, blocking=True)
    assert order[-1] == ("app", "com.netflix.ninja")


async def test_launch_unknown_source_raises(hass, mock_adb):
    await setup(hass)
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(DOMAIN, "launch", {"source_id": "com.gathin.tvhome"}, blocking=True)


async def test_usage_counted_and_persisted(hass, mock_adb, hass_storage):
    await setup(hass)
    async_mock_service(hass, "remote", "send_command")
    async_mock_service(hass, "media_player", "play_media")
    await hass.services.async_call(DOMAIN, "launch", {"source_id": "hdmi2"}, blocking=True)
    await hass.services.async_call(DOMAIN, "name_source", {"port": 2, "name": "Fire TV"}, blocking=True)
    st = hass.states.get("sensor.umote_sources")
    hdmi2 = next(s for s in st.attributes["sources"] if s["id"] == "hdmi2")
    assert hdmi2["uses"] == 1 and hdmi2["name"] == "Fire TV"
    assert hass_storage["umote.names"]["data"] == {"2": "Fire TV"}
    coord = hass.config_entries.async_loaded_entries(DOMAIN)[0].runtime_data
    await coord._usage_store.async_save(coord.usage)
    assert hass_storage["umote.usage"]["data"]["hdmi2"][0] == 1


async def test_home_sensor_lists_living_room_tiles(hass, mock_adb):
    reg = json.loads((FIX / "registry.json").read_text())
    ar.async_get(hass).async_create("Living Room")
    src = MockConfigEntry(domain="test")
    src.add_to_hass(hass)
    devs, ents = dr.async_get(hass), er.async_get(hass)
    dev_ids = {}
    for d in reg["devices"].values():
        dev = devs.async_get_or_create(config_entry_id=src.entry_id, identifiers={("test", d["id"])},
                                       name=d["name"])
        devs.async_update_device(dev.id, name_by_user=d["name_by_user"], area_id=d["area_id"])
        dev_ids[d["id"]] = dev.id
    for e in reg["entities"]:
        dom, obj = e["entity_id"].split(".", 1)
        ents.async_get_or_create(dom, "test", e["entity_id"], suggested_object_id=obj,
                                 device_id=dev_ids.get(e["device_id"]), entity_category=e["entity_category"] and EntityCategory(e["entity_category"]),
                                 config_entry=src)
        hass.states.async_set(e["entity_id"], "off", {"percentage_step": 16.67} if dom == "fan" else {})
    await setup(hass)
    st = hass.states.get("sensor.umote_home")
    assert {t["name"] for t in st.attributes["tiles"]} == {
        "TV fan", "Fridge fan", "Clock fan", "Cabinet lights", "Cabinet power", "Matrix clock"}
    hass.states.async_set("fan.tv_fan", "on", {"percentage": 50, "percentage_step": 16.67})
    await hass.async_block_till_done()
    assert hass.states.get("sensor.umote_home").attributes["tiles"][0]["label"] == "Speed 3"


async def test_artwork_entity_unavailable_without_art(hass, mock_adb):
    hass.states.async_set(TV_CAST, "off", {})
    await setup(hass)
    assert hass.states.get("image.umote_artwork").state == "unavailable"
