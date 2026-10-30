from custom_components.umote.sources import build_sources, source_id_for_activity
from custom_components.umote.tvparse import App, Input

HW = "com.mediatek.tvinput/.hdmi.HDMIInputService/HW"
NOW = 1_800_000_000.0
DAY = 86400
INPUTS = [Input(1, HW + "4", "PlayStation 5", True), Input(2, HW + "5", None, True),
          Input(3, HW + "6", None, False), Input(4, HW + "7", None, True)]
APPS = [App("com.netflix.ninja"), App("in.startv.hotstar"), App("com.amazon.amazonvideo.livingroom"),
        App("org.videolan.vlc"), App("com.sonyliv")]
USAGE = {"com.netflix.ninja": (9, NOW - DAY), "com.amazon.amazonvideo.livingroom": (9, NOW - 2 * DAY),
         "in.startv.hotstar": (2, NOW - DAY), "org.videolan.vlc": (5, NOW - 40 * DAY), "hdmi1": (20, NOW)}


def build(**kw):
    args = dict(inputs=INPUTS, apps=APPS, names={}, usage=USAGE, now=NOW, current=None)
    args.update(kw)
    return build_sources(**args)


def by_id(out):
    return {s["id"]: s for s in out["sources"]}


def test_disconnected_inputs_hidden_and_tuner_always_present():
    ids = [s["id"] for s in build()["sources"]]
    assert "hdmi3" not in ids and "tuner" in ids
    assert ids[:4] == ["hdmi1", "hdmi2", "hdmi4", "tuner"]
    assert by_id(build(inputs=[]))["tuner"]["target"] == "com.mediatek.wwtv.tvcenter"


def test_input_name_priority():
    s = by_id(build(names={1: "Console", 2: "Fire TV"}))
    assert s["hdmi1"]["name"] == "Console" and s["hdmi2"]["name"] == "Fire TV"
    s = by_id(build())
    assert s["hdmi1"]["name"] == "PlayStation 5" and s["hdmi2"]["name"] == "HDMI 2"
    assert s["hdmi1"]["icon"] == "ps5" and s["hdmi1"]["color"] == "#00439c" and s["hdmi2"]["icon"] == "hdmi"


def test_apps_ordered_by_uses_then_name():
    apps = [s["id"] for s in build()["sources"] if s["kind"] == "app"]
    assert apps[:3] == ["com.netflix.ninja", "com.amazon.amazonvideo.livingroom", "in.startv.hotstar"]


def test_apps_unused_30_days_go_to_more():
    out = build()
    assert out["more"] == ["org.videolan.vlc"]
    apps = [s["id"] for s in out["sources"] if s["kind"] == "app"]
    assert apps[-1] == "org.videolan.vlc"            # collapsed apps sort last
    assert "com.sonyliv" not in out["more"]         # never used = not yet stale


def test_quick_row_is_top4_and_always_contains_current():
    out = build()
    assert out["quick"] == ["hdmi1", "com.netflix.ninja", "com.amazon.amazonvideo.livingroom", "org.videolan.vlc"]
    out = build(current="in.startv.hotstar")
    assert len(out["quick"]) == 4 and "in.startv.hotstar" in out["quick"] and out["current"] == "in.startv.hotstar"


def test_passthrough_target_is_url_encoded():
    src = by_id(build())["hdmi1"]
    assert src["target"] == "content://android.media.tv/passthrough/com.mediatek.tvinput%2F.hdmi.HDMIInputService%2FHW4"


def test_app_fields():
    s = by_id(build())["com.netflix.ninja"]
    assert s == {"id": "com.netflix.ninja", "kind": "app", "name": "Netflix", "port": None,
                 "target": "com.netflix.ninja", "color": "#e50914", "icon": "com.netflix.ninja", "uses": 9}


def test_source_id_for_activity():
    assert source_id_for_activity("com.mediatek.wwtv.tvcenter", 1) == "hdmi1"
    assert source_id_for_activity("com.mediatek.wwtv.tvcenter", None) == "tuner"
    assert source_id_for_activity("com.netflix.ninja", None) == "com.netflix.ninja"
    assert source_id_for_activity(None, None) is None
