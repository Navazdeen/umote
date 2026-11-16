"""Build the ordered source list the remote shows. Pure functions."""
from __future__ import annotations

from urllib.parse import quote

from .const import (APP_NAMES, DEFAULT_COLOR, PASSTHROUGH_PREFIX, STYLE,
                    TUNER_PACKAGE, UNUSED_AFTER_S)
from .tvparse import App, Input

QUICK_SIZE = 4


def _app_name(package: str) -> str:
    return APP_NAMES.get(package) or package.rsplit(".", 1)[-1].capitalize()


def _source(id_, kind, name, port, target, color, icon, uses):
    return {"id": id_, "kind": kind, "name": name, "port": port, "target": target,
            "color": color, "icon": icon, "uses": uses}


def build_sources(inputs: list[Input], apps: list[App], names: dict[int, str],
                  usage: dict[str, tuple[int, float]], now: float, current: str | None) -> dict:
    """Inputs (connected, by port), Live TV, then apps, most recently used first; stale apps last.
    The quick row is what's running now, then the most recently used sources."""
    uses = lambda sid: usage.get(sid, (0, now))[0]  # noqa: E731
    # when it was last used; 0 for never (a new app is stored as 0 uses at the time it was first seen)
    last = lambda sid: usage[sid][1] if usage.get(sid, (0, 0))[0] else 0  # noqa: E731
    sources = []
    for i in inputs:
        if not i.connected:
            continue
        sid = f"hdmi{i.port}"
        ps5 = bool(i.cec_name and "PlayStation" in i.cec_name)
        name = names.get(i.port) or i.cec_name or f"HDMI {i.port}"
        sources.append(_source(sid, "input", name, i.port, PASSTHROUGH_PREFIX + quote(i.passthrough_id, safe=""),
                               STYLE["ps5"] if ps5 else DEFAULT_COLOR, "ps5" if ps5 else "hdmi", uses(sid)))
    sources.append(_source("tuner", "tuner", "Live TV", None, TUNER_PACKAGE, DEFAULT_COLOR, "tv", uses("tuner")))

    stale = {a.package for a in apps if now - usage.get(a.package, (0, now))[1] > UNUSED_AFTER_S}
    ordered = sorted(apps, key=lambda a: (a.package in stale, -last(a.package), -uses(a.package),
                                          _app_name(a.package).lower()))
    for a in ordered:
        p = a.package
        sources.append(_source(p, "app", _app_name(p), None, p, STYLE.get(p, DEFAULT_COLOR), p, uses(p)))

    rank = sorted(range(len(sources)), key=lambda k: (sources[k]["id"] != current, sources[k]["id"] in stale,
                                                      -last(sources[k]["id"]), -sources[k]["uses"], k))
    quick = [sources[k]["id"] for k in rank[:QUICK_SIZE]]
    return {"sources": sources, "quick": quick, "more": [a.package for a in ordered if a.package in stale],
            "current": current}


def source_id_for_activity(activity: str | None, current_input: int | None) -> str | None:
    if not activity:
        return None
    if activity == TUNER_PACKAGE:
        return f"hdmi{current_input}" if current_input else "tuner"
    return activity
