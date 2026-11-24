"""Insulating plate between the copper-tape board's copper side and the battery (v7.2, 2026-11-24).

The user's battery is 4.2 thick (the case models 5.0), so under the board there's 2.25:
  board underside (bb_z0 8.3) - 1.0 raised traces - 0.05 copper tape = plate top 7.25
  plate 0.8 thick                                                     = plate bottom 6.45
  battery top: deck 1.65 + 0.2 tape + 4.2                             = 6.05, so 0.4 clear.
It has the board's 43 x 112 outline and:
  - a 0.4 deep pocket on its board side over every through-hole, for the solder joint and the
    flush-cut leg (0.4 of plastic stays between each joint and the battery);
  - windows through it for the copper-side 1206 parts (C1, C2, R4 to R7: they stand too tall to
    cover) and for the J5 wire pads, open to the board's bottom end so the wires get out.
Printed battery side down (pockets open upwards, no supports). Seen from above it matches
button_board_print.stl printed copper side up, so it lies on that board's traces as printed.
Fix it with a few dots of double-sided tape or glue on the trace tops.

Usage: make_insulator_stl.py [out_dir]     writes button_board_insulator.stl
"""
import os, pickle, sys
import numpy as np, trimesh
from shapely.geometry import MultiPoint, Point, box
from shapely.ops import unary_union
from shapely import affinity
import board as B
from make_stl_common import extrude

OUT = sys.argv[1] if len(sys.argv) > 1 else "stl"
BB_Z0, RIDGE, TAPE = 8.3, 1.0, 0.05          # v7 board underside; make_stl.py's RIDGE; copper tape
SEAT, BATT_TAPE, BATT = 1.65, 0.2, 4.2       # key plate deck, tape under the battery, the user's battery (measured)
PLATE_T, POCKET_H, POCKET_D = 0.8, 0.4, 3.0
WIN_MARGIN = 0.8                             # round the 1206 pads and bodies
os.makedirs(OUT, exist_ok=True)
res = pickle.load(open("best.pkl", "rb"))
parts = B.build(res["assign"], res["layout"])

top = BB_Z0 - RIDGE - TAPE
clear = top - PLATE_T - (SEAT + BATT_TAPE + BATT)
assert clear >= 0.3, f"plate to battery {clear:.2f}"

pockets = unary_union([Point(p.x, p.y).buffer(POCKET_D / 2, 32) for pt in parts for p in pt.pads if p.drill])
wins = []
for pt in parts:
    if pt.kind in ("R_1206", "C_1206"):
        pts = [(p.x + sx * p.w / 2, p.y + sy * p.h / 2) for p in pt.pads for sx in (-1, 1) for sy in (-1, 1)]
        wins.append(MultiPoint(pts).convex_hull.buffer(WIN_MARGIN, 16))
    if pt.kind == "HDR_1x10":                # J5 wire pads: a slot open to the board's bottom end
        xs = [p.x for p in pt.pads]
        wins.append(box(min(xs) - 1.6, pt.y - 1.8, max(xs) + 1.6, B.BOARD_H + 1))
windows = unary_union(wins)

outline = box(0, 0, B.BOARD_W, B.BOARD_H)
mirror = lambda g: affinity.scale(g, xfact=-1, origin=(B.BOARD_W / 2, B.BOARD_H / 2))
flip_y = lambda g: affinity.scale(g, yfact=-1, origin=(B.BOARD_W / 2, B.BOARD_H / 2))
fix = lambda g: flip_y(mirror(g))            # as make_stl.py: copper side seen from above
lower = extrude(fix(outline.difference(windows)), PLATE_T - POCKET_H + 0.01, 0)                 # battery side, on the bed
upper = extrude(fix(outline.difference(windows).difference(pockets)), POCKET_H, PLATE_T - POCKET_H)
plate = trimesh.boolean.union([lower, upper], engine="manifold")
plate.export(f"{OUT}/button_board_insulator.stl")
print(f"button_board_insulator.stl: watertight {plate.is_watertight}, bodies {plate.body_count}, "
      f"size {np.round(plate.extents, 2).tolist()}, pockets {len(getattr(pockets, 'geoms', [pockets]))}, "
      f"windows {len(getattr(windows, 'geoms', [windows]))}, {clear:.2f} clear of a {BATT} battery")
assert plate.is_watertight and plate.body_count == 1
