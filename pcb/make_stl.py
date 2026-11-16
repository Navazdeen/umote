"""Printable stand-in for the button board: a 1.6 mm base with the copper pattern raised 0.4 mm
on the copper side (guides for copper tape) and every through-hole drilled. Printed copper side
UP, component side on the bed, so the pattern is mirrored (seen from the copper side), as on
the plotter SVG. Reads best.pkl from build_board.py."""
import os, pickle, sys
import numpy as np, trimesh
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity
import board as B
from route import pad_geom

OUT = sys.argv[1] if len(sys.argv) > 1 else "stl"
RIDGE = float(os.environ.get("RIDGE", 1.0))   # raised copper pattern height (0.4 at first, 1.4 on 2026-10-29, 1.0 on 2026-11-16: user's requests)
HOLE_EXTRA = 0.3     # printed holes come out small (0.2 was still tight)
os.makedirs(OUT, exist_ok=True)
res = pickle.load(open("best.pkl", "rb"))
parts = B.build(res["assign"], res["layout"])

cu = unary_union([pad_geom(p) for part in parts for p in part.pads] +
                 [LineString(pts).buffer(B.TRACE_W / 2, 16) for _, pts in res["traces"]])
holes = unary_union([Point(p.x, p.y).buffer((p.drill + HOLE_EXTRA) / 2, 24)
                     for part in parts for p in part.pads if p.drill])
mirror = lambda g: affinity.scale(g, xfact=-1, origin=(B.BOARD_W / 2, B.BOARD_H / 2))
# board y runs down the board; flip y too so the STL reads the right way up from above
flip_y = lambda g: affinity.scale(g, yfact=-1, origin=(B.BOARD_W / 2, B.BOARD_H / 2))
base2d = flip_y(mirror(box(0, 0, B.BOARD_W, B.BOARD_H).difference(holes)))
ridge2d = flip_y(mirror(cu.difference(holes)))


def extrude(g, h, z0):
    from shapely.geometry.polygon import orient
    ms = []
    for poly in getattr(g, "geoms", [g]):
        poly = orient(poly.buffer(0).simplify(0.02), 1.0)   # 0.02 mm: removes near-duplicate vertices that break triangulation
        if poly.is_empty or poly.area < 0.01:
            continue
        m = trimesh.creation.extrude_polygon(poly, h); m.apply_translation([0, 0, z0])
        if not m.is_volume:
            m.fix_normals()
        ms.append(m)
    bad = [m for m in ms if not m.is_volume]
    assert not bad, f"{len(bad)} extrusions are not closed volumes"
    return trimesh.boolean.union(ms, engine="manifold") if len(ms) > 1 else ms[0]


base = extrude(base2d, B_PCB := 1.6, 0)
ridge = extrude(ridge2d, RIDGE + 0.01, B_PCB - 0.01)
board = trimesh.boolean.union([base, ridge], engine="manifold")
board.export(f"{OUT}/button_board_print.stl")
print("watertight", board.is_watertight, "bodies", board.body_count,
      "size", np.round(board.extents, 2).tolist(), "holes", len(getattr(holes, "geoms", [holes])))
