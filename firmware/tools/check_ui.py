"""Layout validator over the simulator's LVGL dump (JSON lines, one object per line).

usage: python firmware/tools/check_ui.py dump.jsonl   -> exit 0, or one line per failure and exit 1
Rules match spec §4.3 and the mockup validator: targets >= 44 px, >= 8 px between targets (outer focus
rings counted; full-width stacked `row_` objects may touch), text >= 12 px, no clipped text unless the
object name ends `_trunc`, everything inside 240x320, no glyph/emoji icons.
"""
from __future__ import annotations

import json
import sys

import regex

SCREEN_W, SCREEN_H = 240, 320
MIN_TARGET, MIN_GAP, MIN_FONT = 44, 8, 12
GLYPH = regex.compile(r"[←-⇿⌀-⏿①-⓿■-➿⤀-⯿‹›«»✓✔✕]|\p{Extended_Pictographic}")


def _gap(a: dict, b: dict) -> float:
    """Distance between two rects grown by their outlines; negative when they overlap."""
    oa, ob = a["outline"], b["outline"]
    dx = max(b["x"] - ob - (a["x"] + a["w"] + oa), a["x"] - oa - (b["x"] + b["w"] + ob))
    dy = max(b["y"] - ob - (a["y"] + a["h"] + oa), a["y"] - oa - (b["y"] + b["h"] + ob))
    return max(dx, dy)


def _contains(a: dict, b: dict) -> bool:
    return a["x"] <= b["x"] and a["y"] <= b["y"] and a["x"] + a["w"] >= b["x"] + b["w"] and a["y"] + a["h"] >= b["y"] + b["h"]


def _stacked_rows(a: dict, b: dict) -> bool:
    return (a["obj"].startswith("row_") and b["obj"].startswith("row_") and a["x"] == b["x"] and a["w"] == b["w"]
            and _gap(a, b) >= -max(a["outline"], b["outline"]) * 2)


def check(objs: list[dict]) -> list[str]:
    fails = []
    for screen in dict.fromkeys(o["screen"] for o in objs):
        live = [o for o in objs if o["screen"] == screen and not o["hidden"]]
        if any(o["layer"] == "modal" for o in live):
            live = [o for o in live if o["layer"] == "modal"]
        where = lambda o: f"{screen}/{o['obj']}"  # noqa: E731
        for o in live:
            if o["x"] < 0 or o["y"] < 0 or o["x"] + o["w"] > SCREEN_W or o["y"] + o["h"] > SCREEN_H:
                fails.append(f"bounds: {where(o)} at {o['x']},{o['y']} {o['w']}x{o['h']}")
            if o["clickable"] and (o["w"] < MIN_TARGET or o["h"] < MIN_TARGET):
                fails.append(f"target: {where(o)} is {o['w']}x{o['h']}")
            if o.get("text"):
                if o.get("font_px") is not None and o["font_px"] < MIN_FONT:
                    fails.append(f"text: {where(o)} is {o['font_px']} px")
                if o.get("text_w") is not None and o["text_w"] > o["w"] and not o["obj"].endswith("_trunc"):
                    fails.append(f"clipped: {where(o)} text {o['text_w']} px in {o['w']} px")
                if GLYPH.search(o["text"]):
                    fails.append(f"glyph: {where(o)} {o['text'][:18]!r}")
        targets = [o for o in live if o["clickable"]]
        for i, a in enumerate(targets):
            for b in targets[i + 1:]:
                if _contains(a, b) or _contains(b, a) or _stacked_rows(a, b):
                    continue
                if _gap(a, b) < MIN_GAP:
                    fails.append(f"gap: {where(a)} and {b['obj']} are {_gap(a, b):.0f} px apart")
    return fails


def main(argv: list[str]) -> int:
    with open(argv[0]) as f:
        objs = [json.loads(line) for line in f if line.strip()]
    fails = check(objs)
    for line in fails:
        print(line)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
