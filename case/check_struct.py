"""Structural checks for case parts (v6): material thickness measured through the mesh.

From each surface sample a ray goes inward (against the face normal); the distance to the next
surface is the local thickness. A wall, a floor, a land beside a cut-out and the skin over a pocket
all show up as short rays, so one measurement covers spec v6 section 3. Sharp convex edges give
short rays too (the ray grazes the neighbouring face), so samples within `edge_skip` of an edge
are left out.

Usage: python3 case/check_struct.py part.stl [min_mm]      prints the thinnest spots, exit 1 below min
"""
import sys
import numpy as np
import trimesh


def thickness_at(mesh, point, direction):
    """thickness along one inward ray from a surface point"""
    t = _cast(mesh, np.array([point], float), np.array([direction], float))
    return float(t[0])


FACING = np.cos(np.radians(40))     # a ray counts only if it leaves through a face within 40 deg of facing it (a 45 deg chamfer doesn't)


def _cast(mesh, pts, dirs):
    """inward ray length per sample; inf where it leaves through a face turned more than 50 deg
    away (the other side of a 45 deg chamfer, a blunt wedge or a rolled edge, not the opposite wall)"""
    org = pts + dirs * 1e-3
    loc, ray, tri = mesh.ray.intersects_location(org, dirs, multiple_hits=False)
    out = np.full(len(pts), np.inf)
    if len(ray):
        facing = (mesh.face_normals[tri] * dirs[ray]).sum(1) > FACING
        out[ray[facing]] = np.linalg.norm(loc[facing] - org[ray[facing]], axis=1) + 1e-3
    return out


def thickness_samples(mesh, density=2.0, edge_skip=0.3, seed=1, acute_skip=0.0):
    """(points, thickness) for about `density` samples per mm2 of surface.
    Samples within edge_skip of any sharp (> 30 deg) edge are dropped, and within acute_skip of a
    convex edge sharper than 90 deg (a wedge: a ray from beside it leaves through the other face
    after a short way, though the part isn't thin there)."""
    n = int(max(2000, mesh.area * density))
    pts, fi = trimesh.sample.sample_surface(mesh, n, seed=seed)
    nrm = mesh.face_normals[fi]
    ang = mesh.face_adjacency_angles
    for lim, skip in ((np.radians(30), edge_skip), (np.radians(91), acute_skip)):
        sel = (ang > lim) & (mesh.face_adjacency_convex if lim > np.radians(90) else True)
        edges = mesh.face_adjacency_edges[sel]
        if skip <= 0 or not len(edges):
            continue
        a, b = mesh.vertices[edges[:, 0]], mesh.vertices[edges[:, 1]]
        keep = np.ones(len(pts), bool)
        for lo in range(0, len(pts), 4000):
            keep[lo:lo + 4000] = _seg_dist(pts[lo:lo + 4000], a, b) > skip
        pts, nrm = pts[keep], nrm[keep]
    return pts, _cast(mesh, pts, -nrm)


def _seg_dist(p, a, b):
    """distance from each point in p to the nearest of the segments a-b"""
    ab = b - a
    L2 = np.maximum((ab * ab).sum(1), 1e-12)
    best = np.full(len(p), np.inf)
    for lo in range(0, len(a), 2000):
        A, AB, l2 = a[lo:lo + 2000], ab[lo:lo + 2000], L2[lo:lo + 2000]
        t = np.clip(((p[:, None, :] - A[None]) * AB[None]).sum(2) / l2[None], 0, 1)
        q = A[None] + t[..., None] * AB[None]
        best = np.minimum(best, np.linalg.norm(p[:, None, :] - q, axis=2).min(1))
    return best


def min_thickness(mesh, density=2.0, exclude=None, edge_skip=0.3):
    """(thinnest thickness, its point); exclude(points) -> bool mask of samples to ignore"""
    pts, t = thickness_samples(mesh, density, edge_skip)
    ok = np.isfinite(t)
    if exclude is not None:
        ok &= ~exclude(pts)
    i = np.argmin(np.where(ok, t, np.inf))
    return float(t[i]), pts[i]


def thin_spots(mesh, limit, density=2.0, exclude=None, edge_skip=0.3):
    """every sample thinner than limit: (points, thickness)"""
    pts, t = thickness_samples(mesh, density, edge_skip)
    bad = np.isfinite(t) & (t < limit)
    if exclude is not None:
        bad &= ~exclude(pts)
    return pts[bad], t[bad]


def clusters(pts, t, cell=2.0):
    """thin samples grouped on a cell grid: [(min thickness, centre, count)], thinnest first"""
    out = {}
    for p, v in zip(pts, t):
        k = tuple(np.floor(p / cell).astype(int))
        lo, c, n = out.get(k, (np.inf, np.zeros(3), 0))
        out[k] = (min(lo, v), c + p, n + 1)
    return sorted([(lo, c / n, n) for lo, c, n in out.values()], key=lambda r: r[0])


if __name__ == "__main__":
    m = trimesh.load(sys.argv[1], force="mesh")
    lim = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
    p, t = thin_spots(m, lim)
    for lo, c, n in clusters(p, t)[:25]:
        print(f"{lo:.2f} at {np.round(c, 1).tolist()} ({n})")
    print(f"{len(t)} samples under {lim}")
    sys.exit(1 if len(t) else 0)
