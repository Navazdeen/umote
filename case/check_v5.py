"""Printability check for the v5 STLs, which are exported in print orientation (z up).
A part passes when it is watertight, is one body, has no downward face steeper than 45 deg
above the first layer, no flat bridge longer than max_bridge, and fits the bed.

Usage: python3 case/check_v5.py case/stl_v5/<part>.stl ...    (exit 1 on any problem)
"""
import sys
import numpy as np
import trimesh

FIRST_LAYER = 0.15
DOWN_45 = -0.7072            # face normal z below this faces down more than 45 deg
FLAT = -0.999


def _down(m, limit):
    n, c = m.face_normals, m.triangles_center
    return (n[:, 2] < limit) & (c[:, 2] > m.bounds[0][2] + FIRST_LAYER)


def bridge_spans(m):
    """Longest horizontal extent of each connected flat downward patch (mm)."""
    idx = np.nonzero(_down(m, FLAT))[0]
    if len(idx) == 0:
        return []
    adj = m.face_adjacency
    keep = np.isin(adj, idx).all(axis=1)
    groups = trimesh.graph.connected_components(adj[keep], nodes=idx)
    spans = []
    for g in groups:
        v = m.vertices[m.faces[g].ravel()]
        ext = float((v[:, :2].max(axis=0) - v[:, :2].min(axis=0)).max())
        if m.area_faces[g].sum() / ext < 0.5:      # a strip under ~0.5 mm wide is a ledge (elephant's-foot steps), not a bridge
            continue
        spans.append(ext)
    return spans


def check_part(path, bed=180, max_bridge=17, allow_bodies=False, max_overhang_area=1.0):
    m = trimesh.load(path, force="mesh")
    problems = []
    if not m.is_watertight:
        problems.append("not watertight")
    if not allow_bodies and m.body_count != 1:
        problems.append(f"{m.body_count} bodies")
    steep = _down(m, DOWN_45) & (m.face_normals[:, 2] >= FLAT)
    area = float(m.area_faces[steep].sum())
    if area > max_overhang_area:
        problems.append(f"overhang >45deg {area:.2f} mm2")
    long = [s for s in bridge_spans(m) if s > max_bridge]
    if long:
        problems.append(f"bridge {max(long):.1f} mm > {max_bridge}")
    ext = m.bounds[1] - m.bounds[0]
    if max(ext[0], ext[1]) > bed:
        problems.append(f"bed: {max(ext[0], ext[1]):.1f} mm > {bed}")
    return problems


def main(paths):
    bad = 0
    for p in paths:
        probs = check_part(p, allow_bodies=p.rsplit("/", 1)[-1].startswith("caps"))
        print(f"{p}: {'ok' if not probs else '; '.join(probs)}")
        bad += bool(probs)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
