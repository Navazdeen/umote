"""Printable stand-in for the button board: a 1.6 mm base with the copper pattern raised on the
copper side (guides for copper tape) and every through-hole drilled. Printed copper side UP,
component side on the bed, so the pattern is mirrored (seen from the copper side), as on the
plotter SVG. Reads best.pkl from build_board.py.

v7.2 (2026-11-24, the 1.0 traces and 0.25-0.35 rings round the holes printed badly with a 0.4 nozzle):
  - every net's copper grows by up to GROW a side into free space, but stays GAP from every other
    net (traces up to 2.0 wide where there's room; switch rings ~0.85). Crowded spots keep v7.1's copper;
  - holes are drill + 0.2 (0.3 before): set the slicer's X-Y hole compensation to +0.1;
  - the DIP-28 holes are 1.2 and Q1's 1.1 (v7.2.2; 0.9 in v7.2 was too small);
  - v7.2.2: the base is 1.0 inside a 1.6 rim and all trace tops are level at 2.0, so the board is
    2.0 thick at every hole (2.6 in v7.2) and the legs come through 0.6 further;
  - both long edges chamfered 0.5 x 45 deg top and bottom, to lock onto the v7.1 shell's hooks
    (make_stl_common.py);
  - 0.2 deep locating recesses on the component side (the bed side) for the 5 spacer posts, which
    print separately (button_spacers.stl) and are glued in: they can't print on the bed side, and
    a peg hole would cut a trace at one spot.
Writes button_board_print.stl and button_spacers.stl."""
import os, pickle, sys
import numpy as np, trimesh
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity
import board as B
from route import pad_geom
from make_stl_common import extrude, chamfer_long_edges, check_clear, posts2d, SPACERS, SPACER_D, SPACER_H, CHAMFER

OUT = sys.argv[1] if len(sys.argv) > 1 else "stl"
RIDGE = float(os.environ.get("RIDGE", 1.0))   # raised copper pattern height (0.4 at first, 1.4 on 2026-10-29, 1.0 on 2026-11-16: user's requests)
HOLE_EXTRA = 0.2     # + the slicer's X-Y hole compensation 0.1 (0.3 in the model before, which ate the rings)
LEG_HOLE = {"DIP28": 1.2, "TO92_wide": 1.1}   # v7.2.2: 0.9 (v7.2) printed too small for the MCP23017's legs
# v7.2.2: the legs didn't come through 1.6 base + 1.0 traces. The base is 1.0 inside a 1.6 rim (the rim
# keeps the edge chamfers and the hook fit) and every trace top is level at TOP, so the board is 2.0 at
# every hole. The component side stays flat: the switches (and so the caps) don't move.
BASE_IN, RIM_LONG, RIM_SHORT, TOP = 1.0, 2.5, 2.0, 2.0
GROW, GAP = 0.5, 0.6 # copper growth a side; the least gap between two nets (copper tape mustn't bridge it)
EDGE = CHAMFER + 0.3 # copper keeps this far from the board's edge (off the chamfer and the hooks)
RECESS_D, RECESS_H = SPACER_D + 0.2, 0.2
os.makedirs(OUT, exist_ok=True)
res = pickle.load(open("best.pkl", "rb"))
parts = B.build(res["assign"], res["layout"])


def hole_d(part, p):
    return LEG_HOLE.get(part.kind, p.drill + HOLE_EXTRA)


# copper by net (a pad with no net is its own net)
nets = {}
for part in parts:
    for i, p in enumerate(part.pads):
        nets.setdefault(p.net or f"nc-{part.ref}-{i}", []).append(pad_geom(p))
for net, pts in res["traces"]:
    nets.setdefault(net, []).append(LineString(pts).buffer(B.TRACE_W / 2, 16))
nets = {k: unary_union(v) for k, v in nets.items()}
inside = box(0, 0, B.BOARD_W, B.BOARD_H).buffer(-EDGE, join_style=2)
# grow in STEP steps: each step a net may reach GAP + STEP from the others' current copper, so when they
# grow too the gap stays >= GAP. Nets 0.94 apart (DIP pins) each take their half of the 0.34 to spare.
STEP = 0.05
grown = dict(nets)
for _ in range(int(round(GROW / STEP))):
    nxt = {}
    for k, g in grown.items():
        others = unary_union([v for kk, v in grown.items() if kk != k])
        nxt[k] = g.buffer(STEP, 8).difference(others.buffer(GAP + STEP, 16)).intersection(inside).union(g)
    grown = nxt
cu = unary_union(list(grown.values()))
hole_list = [(Point(p.x, p.y).buffer(hole_d(part, p) / 2, 24), part, p) for part in parts for p in part.pads if p.drill]
holes = unary_union([h for h, _, _ in hole_list])

# checks: nets apart by >= GAP (or as close as v7.1 had them), and the ring round each hole
keys = list(grown)
for i in range(len(keys)):
    for j in range(i + 1, len(keys)):
        d = grown[keys[i]].distance(grown[keys[j]])
        assert d >= min(GAP, nets[keys[i]].distance(nets[keys[j]])) - 1e-6, f"{keys[i]} / {keys[j]} {d:.2f} apart"
rings = {}
for h, part, p in hole_list:
    c = next(v for k, v in grown.items() if v.contains(Point(p.x, p.y)))
    outside = box(-5, -5, B.BOARD_W + 5, B.BOARD_H + 5).difference(c.union(h))
    r = hole_d(part, p) / 2
    w = min(Point(p.x + r * np.cos(a), p.y + r * np.sin(a)).distance(outside) for a in np.linspace(0, 2 * np.pi, 36, endpoint=False))
    rings.setdefault(part.kind, []).append(w)
recesses = posts2d().buffer((RECESS_D - SPACER_D) / 2, 48)
check_clear(recesses, holes, what="holes")

mirror = lambda g: affinity.scale(g, xfact=-1, origin=(B.BOARD_W / 2, B.BOARD_H / 2))
# board y runs down the board; flip y too so the STL reads the right way up from above
flip_y = lambda g: affinity.scale(g, yfact=-1, origin=(B.BOARD_W / 2, B.BOARD_H / 2))
fix = lambda g: flip_y(mirror(g))
outline = box(0, 0, B.BOARD_W, B.BOARD_H)
B_PCB = 1.6
assert TOP - BASE_IN == RIDGE
rim = outline.difference(box(RIM_LONG, RIM_SHORT, B.BOARD_W - RIM_LONG, B.BOARD_H - RIM_SHORT))
base = trimesh.boolean.union([extrude(fix(outline.difference(holes).difference(recesses)), RECESS_H + 0.01, 0),
                              extrude(fix(outline.difference(holes)), BASE_IN - RECESS_H, RECESS_H),
                              extrude(fix(rim.difference(holes)), B_PCB - BASE_IN + 0.01, BASE_IN - 0.01)], engine="manifold")
ridge = extrude(fix(cu.difference(holes)), TOP - BASE_IN + 0.01, BASE_IN - 0.01)   # tops level at TOP (0.4 over the rim)
board = trimesh.boolean.union([base, ridge], engine="manifold")
board = chamfer_long_edges(board, B.BOARD_W, B.BOARD_H, B_PCB)
board.export(f"{OUT}/button_board_print.stl")
assert board.is_watertight and board.body_count == 1
print("button_board_print.stl: watertight", board.is_watertight, "bodies", board.body_count,
      "size", np.round(board.extents, 2).tolist(), "holes", len(hole_list))
print("ring round the holes, min / median:", {k: (round(min(v), 2), round(float(np.median(v)), 2)) for k, v in rings.items()})
print(f"copper area +{100 * (cu.area / unary_union(list(nets.values())).area - 1):.0f}% on v7.1")

# the spacer posts: printed standing, glued into the recesses (their tops press on the case face)
posts = []
for i in range(len(SPACERS)):
    m = trimesh.creation.cylinder(radius=SPACER_D / 2, height=SPACER_H + RECESS_H, sections=48)
    m.apply_translation([i * (SPACER_D + 3), 0, (SPACER_H + RECESS_H) / 2])
    posts.append(m)
spacers = trimesh.util.concatenate(posts)
spacers.export(f"{OUT}/button_spacers.stl")
print("button_spacers.stl:", len(posts), "posts", SPACER_D, "x", round(SPACER_H + RECESS_H, 2))
