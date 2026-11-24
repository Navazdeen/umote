"""Printed button carrier for the CJMCU-2317 / HW-839 MCP23017 module (no copper, free wiring).

Same 43 x 112 outline as the button board, so the case fits it unchanged. It has:
  - leg holes for all 14 tact switches (from board.tact6, so the positions match the case);
  - a through-window for the module in the clear band between the BACK/HOME/VOICE row (bodies
    end at y 53) and the VOL+/CH+ row (bodies start at y 74). The module lies 26 mm along x,
    its PCB in the plate's plane, resting on two lips under its 21 mm ends (the pin rows run
    along the 26 mm edges, so the lips stay clear of them). Its pads can be reached from below;
  - 3 holes for Q1 (TO-92, layout "pads" position) and a row of 10 tie-down holes where the
    J5 wire pads were (strain relief for the display and IR LED wires);
  - an engraved arrow on the top face pointing at the tip (POWER end), so the board can't go in
    mirrored.
  - v7.2: five spacer posts (d 4.0, 4.6 tall) on the top face. They stop 0.1 under the case face, so the
    plate is held both ways: posts against the face, the shell's 4 hooks under its edges.
The 1206 resistors and capacitors go inline on the wires.

Printed TOP FACE UP (component side up; the lips print on the bed). Viewed from above, the STL
matches board.py's component-side view (POWER at the top left).

Usage: make_carrier_stl.py [out_dir] [module_L] [module_W]   (measured module size, mm)
Writes button_carrier.stl and button_carrier_fit_test.stl (the window strip only).
"""
import os, sys
import numpy as np, trimesh
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union
from shapely import affinity
from shapely.geometry.polygon import orient
import board as B

_MAIN = __name__ == "__main__"
OUT = sys.argv[1] if _MAIN and len(sys.argv) > 1 else "stl"
MOD_L = float(sys.argv[2]) if _MAIN and len(sys.argv) > 2 else 26.0    # along x (the pin rows)
MOD_W = float(sys.argv[3]) if _MAIN and len(sys.argv) > 3 else 21.0    # along y
MOD_CLR = 0.15        # window clearance a side
PLATE = 1.6           # same as the PCB (the case and fit_check assume 1.6)
LIP_T, LIP_W = 0.6, 1.2
HOLE_EXTRA = 0.3      # printed holes come out small (as in make_stl.py)
MOD_X, MOD_Y = 21.5, 63.5   # window centre: board centre-ish, centred in the 53..74 band
# v7.2 spacers: posts on the top face that stop 0.1 under the shell face's underside (pz0 - bb_top - 0.1),
# so the board can't be pushed in; the shell's hooks hold it from the back. Spots (board coords) are on
# flat face underside, clear of caps, rockers, the D-pad ring, clips, wires, the mic, Q1 and the window.
SPACERS = [(17.0, 3.5), (6.5, 39.0), (35.0, 41.5), (6.5, 100.5), (32.0, 102.0)]
SPACER_D, SPACER_H = 4.0, 4.6

# ---- switch and Q1 holes
parts = [B.tact6(r, x, y, "S", fn, rot) for r, (x, y, fn, rot) in B.BUTTONS.items()]
qx, qy = B.LAYOUTS["pads"]["Q1"]
parts.append(B.to92("Q1", qx, qy, "E", "B", "C"))
hole_list = [Point(p.x, p.y).buffer((p.drill + HOLE_EXTRA) / 2, 24) for pt in parts for p in pt.pads]
# tie-down row along the bottom edge (old J5 pad positions)
hole_list += [Point(26.19 + (i - 4.5) * 2.54, 108.8).buffer((1.0 + HOLE_EXTRA) / 2, 24) for i in range(10)]
holes = unary_union(hole_list)

# ---- module window
wx0, wx1 = MOD_X - MOD_L / 2 - MOD_CLR, MOD_X + MOD_L / 2 + MOD_CLR
wy0, wy1 = MOD_Y - MOD_W / 2 - MOD_CLR, MOD_Y + MOD_W / 2 + MOD_CLR
window = box(wx0, wy0, wx1, wy1)
lips = box(wx0, wy0, wx0 + LIP_W, wy1).union(box(wx1 - LIP_W, wy0, wx1, wy1))

# How much plastic is left between the window and the nearest switch leg hole?
sw_holes = unary_union(hole_list[:4 * len(B.BUTTONS)])
gap = window.distance(sw_holes)
cuts_holes = window.intersects(sw_holes)

# ---- orientation arrow on the top face (bottom right, pointing at the tip / POWER end)
ax, ay = 39.0, 99.0
arrow = Polygon([(ax, ay - 4.0), (ax - 2.2, ay - 0.5), (ax - 0.7, ay - 0.5), (ax - 0.7, ay + 3.0),
                 (ax + 0.7, ay + 3.0), (ax + 0.7, ay - 0.5), (ax + 2.2, ay - 0.5)])
ARROW_D = 0.4

outline = box(0, 0, B.BOARD_W, B.BOARD_H)
flip_y = lambda g: affinity.scale(g, yfact=-1, origin=(B.BOARD_W / 2, B.BOARD_H / 2))


def extrude(g, h, z0):
    ms = []
    for poly in getattr(g, "geoms", [g]):
        poly = orient(poly.buffer(0).simplify(0.02), 1.0)
        if poly.is_empty or poly.area < 0.01:
            continue
        m = trimesh.creation.extrude_polygon(poly, h); m.apply_translation([0, 0, z0])
        if not m.is_volume:
            m.fix_normals()
        ms.append(m)
    assert all(m.is_volume for m in ms), "extrusion is not a closed volume"
    return trimesh.boolean.union(ms, engine="manifold") if len(ms) > 1 else ms[0]


def build(clip=None):
    plate2d = outline.difference(holes).difference(window)
    lip2d = lips.difference(holes)
    if clip is not None:
        plate2d, lip2d = plate2d.intersection(clip), lip2d.intersection(clip)
    body = trimesh.boolean.union([extrude(flip_y(plate2d), PLATE, 0), extrude(flip_y(lip2d), LIP_T, 0)],
                                 engine="manifold")
    posts = unary_union([Point(x, y).buffer(SPACER_D / 2, 48) for x, y in SPACERS])
    if clip is not None:
        posts = posts.intersection(clip)
    if not posts.is_empty:
        body = trimesh.boolean.union([body, extrude(flip_y(posts), SPACER_H + 0.01, PLATE - 0.01)], engine="manifold")
    if clip is None or clip.contains(arrow):
        cut = extrude(flip_y(arrow), ARROW_D + 0.01, PLATE - ARROW_D)
        body = trimesh.boolean.difference([body, cut], engine="manifold")
    return body


def save(m, name):
    m.export(f"{OUT}/{name}")
    print(f"{name}: watertight {m.is_watertight}, bodies {m.body_count}, size {np.round(m.extents, 2).tolist()}")
    assert m.is_watertight and m.body_count == 1, name


if _MAIN:
    os.makedirs(OUT, exist_ok=True)
    save(build(), "button_carrier.stl")
    # fit-test coupon: the strip with the window and the adjacent switch leg holes
    save(build(box(0, 45.0, B.BOARD_W, 82.0)), "button_carrier_fit_test.stl")
    print(f"module {MOD_L} x {MOD_W}: window x[{wx0:.2f},{wx1:.2f}] y[{wy0:.2f},{wy1:.2f}], "
          f"plastic to nearest switch hole {gap:.2f} mm{' (window CUTS INTO switch holes)' if cuts_holes else ''}")
