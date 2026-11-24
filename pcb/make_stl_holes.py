"""Holes-only printable button board: no copper ridges. Through-hole parts get their drilled
holes, and wiring is point-to-point on the copper side.

SMD 1206 parts sit in shallow locating pockets on the copper side. Each end has a wire hole
just past the end cap. A wire or a leg clipped from a through-hole part goes through that hole
and is soldered to the cap. The hole-less J5 wire pads become plain wire holes.

v7.2: printed COMPONENT side UP (as make_carrier_stl.py: viewed from above it matches board.py),
so the five spacer posts on the component side stand upright. The 1206 pockets then open onto the
bed (3.6 x 2.0 bridges, 0.8 up). Both long edges get 0.5 x 45 deg chamfers, top and bottom: the
bottom ones sit on the v7.1 shell's hook slopes and the posts press the board onto them from the
face (make_stl_common.py). Reads best.pkl."""
import math, os, pickle, sys
import numpy as np, trimesh
from shapely.geometry import Point, box
from shapely.ops import unary_union
from shapely import affinity
import board as B
from make_stl_common import extrude, posts2d, add_spacers, chamfer_long_edges, check_clear

OUT = sys.argv[1] if len(sys.argv) > 1 else "stl"
T = 1.6              # board thickness
HOLE_EXTRA = 0.3     # printed holes come out small (same as make_stl.py)
POCKET_DEPTH = 0.8   # leaves a 0.8 mm floor
POCKET_GAP = 0.2     # per side around the 3.2 x 1.6 mm 1206 body
WIRE_DRILL = 0.8     # wire hole at each SMD end and at hole-less pads
END_OFFSET = 2.3     # wire hole centre from the part centre, just past the end cap
os.makedirs(OUT, exist_ok=True)
res = pickle.load(open("best.pkl", "rb"))
parts = B.build(res["assign"], res["layout"])

holes, pockets = [], []
for part in parts:
    if part.kind in ("R_1206", "C_1206"):
        vert = part.rot == 90
        L, W = 3.2 + 2 * POCKET_GAP, 1.6 + 2 * POCKET_GAP
        w, h = (W, L) if vert else (L, W)
        pockets.append(box(part.x - w / 2, part.y - h / 2, part.x + w / 2, part.y + h / 2))
        for s in (-1, 1):
            x, y = (part.x, part.y + s * END_OFFSET) if vert else (part.x + s * END_OFFSET, part.y)
            holes.append(Point(x, y).buffer((WIRE_DRILL + HOLE_EXTRA) / 2, 24))
        continue
    for p in part.pads:
        d = p.drill or WIRE_DRILL
        holes.append(Point(p.x, p.y).buffer((d + HOLE_EXTRA) / 2, 24))

holes, pockets = unary_union(holes), unary_union(pockets)
flip_y = lambda g: affinity.scale(g, yfact=-1, origin=(B.BOARD_W / 2, B.BOARD_H / 2))
fix = flip_y                       # component side up (v7.2); copper side up before, mirrored as well
outline = box(0, 0, B.BOARD_W, B.BOARD_H)
solid2d = fix(outline.difference(holes))                    # component side: the top 0.8
pocket2d = fix(outline.difference(holes).difference(pockets))   # copper side, on the bed: the pockets
bodies = unary_union([box(p.x - p.body[0] / 2, p.y - p.body[1] / 2, p.x + p.body[0] / 2, p.y + p.body[1] / 2)
                      for p in parts if p.body])

if __name__ == "__main__":
    posts = posts2d()
    gap = check_clear(posts, unary_union([holes, pockets, bodies]), what="holes, pockets or part bodies")
    lower = extrude(pocket2d, POCKET_DEPTH + 0.01, 0)
    upper = extrude(solid2d, T - POCKET_DEPTH, POCKET_DEPTH)
    board = trimesh.boolean.union([lower, upper], engine="manifold")
    board = add_spacers(board, fix(posts), T)
    board = chamfer_long_edges(board, B.BOARD_W, B.BOARD_H, T)
    print(f"spacers: {gap:.2f} mm clear of the nearest hole, pocket or part body")
    board.export(f"{OUT}/button_board_holes.stl")
    print("watertight", board.is_watertight, "bodies", board.body_count,
          "size", np.round(board.extents, 2).tolist(),
          "holes", len(getattr(holes, "geoms", [holes])),
          "pockets", len(getattr(pockets, "geoms", [pockets])))
