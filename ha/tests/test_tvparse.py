from conftest import fx
from custom_components.umote.const import SYSTEM_PACKAGES
from custom_components.umote.tvparse import parse_apps, parse_current_input, parse_inputs


def test_parse_inputs_finds_ps5_on_hdmi1():
    ins = parse_inputs(fx("tv_input.txt"), fx("hdmi_control.txt"))
    assert [i.port for i in ins] == [1, 2, 3, 4]
    ps5 = ins[0]
    assert ps5.passthrough_id == "com.mediatek.tvinput/.hdmi.HDMIInputService/HW4"
    assert ps5.cec_name == "PlayStation 5"
    assert ins[1].cec_name is None


def test_parse_apps_drops_system_packages():
    pk = {a.package for a in parse_apps(fx("packages.txt"), SYSTEM_PACKAGES)}
    assert {"com.netflix.ninja", "in.startv.hotstar", "com.amazon.amazonvideo.livingroom"} <= pk
    assert not pk & {"com.android.vending", "com.gathin.tvhome", "com.haier.launcher.haiermatrix",
                     "com.mediatek.wwtv.mediaplayer", "com.mediatek.wwtv.tvcenter"}


def test_parse_current_input_none_when_invalid():
    assert parse_current_input("mActiveSource: (invalid, invalid)") is None
    assert parse_current_input("mActiveSource: (0x04, 0x1000)\n ... display_name: PlayStation 5 power_status: 0 physical_address: 0x1000 port_id: 1") == 1


def test_parsers_tolerate_empty_output():
    assert parse_inputs("", "") == [] and parse_apps("", SYSTEM_PACKAGES) == []
