"""Shared helpers for the printable board scripts (make_stl.py, make_stl_holes.py, make_carrier_stl.py)."""
import numpy as np
import trimesh
from shapely.geometry import Point, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

# ---- v7.2: fitting the boards to the v7.1 shell as printed (the shell is not reprinted) ----
# The v7.1 clip hooks have a 45 deg slope where the board's bottom edge sits (x 21.0 -> 21.6 from
# bb_z0 to bb_z0 + 0.6). A 0.5 x 45 deg chamfer on the board's bottom long edges lies on that slope with
# the board at its design height, and one on the top edges is the lead-in that spreads the clips as
# the board goes in from the back.
CHAMFER = 0.5
# Spacer posts on the component side (towards the case face). Board coordinates (board.py, component
# side, POWER top left). Each lands on flat face underside, clear of caps, rockers, the D-pad ring,
# clips, wires, the mic, Q1, the module window and the holes board's parts and wire holes
# (case/tests/test_v7.py checks them against the case).
SPACERS = [(17.0, 3.5), (6.0, 40.5), (35.0, 41.5), (11.0, 106.0), (33.5, 103.5)]
SPACER_D = 4.0
PRELOAD = 0.05                      # past the face: the board rides 0.05 up the hook slopes, clips spread 0.05
SPACER_H = 14.6 - 9.9 + PRELOAD     # face underside (pz0) - board top (bb_top) in the v7 case


def extrude(g, h, z0):
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


def posts2d():
    """The spacer footprints, in board coordinates."""
    return unary_union([Point(x, y).buffer(SPACER_D / 2, 48) for x, y in SPACERS])


def add_spacers(body, posts, top):
    """Spacer posts (already in the STL's xy frame) standing on the plate's top face at z = top."""
    return trimesh.boolean.union([body, extrude(posts, SPACER_H + 0.01, top - 0.01)], engine="manifold")


def chamfer_long_edges(body, w, l, t, c=CHAMFER):
    """c x 45 deg off the top and bottom of both long edges (x = 0 and x = w) of a w x l x t plate
    lying on z = 0, y from 0 to l."""
    e = 0.01
    cuts = []
    for tri in ([(-e, -e), (c + e, -e), (-e, c + e)],                 # bottom edge at x = 0
                [(-e, t + e), (-e, t - c - e), (c + e, t + e)]):     # top edge at x = 0
        for side in (0, 1):
            pts = tri if side == 0 else [(w - x, z) for x, z in tri]
            m = trimesh.creation.extrude_polygon(orient(Polygon(pts), 1.0), l + 2)
            m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))   # (x, z, e) -> (x, -e, z)
            m.apply_translation([0, l + 1, 0])
            cuts.append(m)
    return trimesh.boolean.difference([body] + cuts, engine="manifold")


def check_clear(posts, keepouts, gap=0.4, what="board parts"):
    """Each post must stay gap clear of the holes, pockets and part bodies (all in board coordinates)."""
    d = posts.distance(keepouts)
    assert d >= gap, f"a spacer is {d:.2f} from the {what} (needs {gap})"
    return d
