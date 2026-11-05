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


def _cast(mesh, pts, dirs):
    org = pts + dirs * 1e-3
    loc, ray, _ = mesh.ray.intersects_location(org, dirs, multiple_hits=False)
    out = np.full(len(pts), np.inf)
    if len(ray):
        out[ray] = np.linalg.norm(loc - org[ray], axis=1) + 1e-3
    return out


def thickness_samples(mesh, density=2.0, edge_skip=0.3, seed=1):
    """(points, thickness) for about `density` samples per mm2 of surface"""
    n = int(max(2000, mesh.area * density))
    pts, fi = trimesh.sample.sample_surface(mesh, n, seed=seed)
    nrm = mesh.face_normals[fi]
    if edge_skip > 0:
        # sharp edges: drop samples near a face boundary whose neighbour turns more than 30 deg
        ang = mesh.face_adjacency_angles
        sharp = mesh.face_adjacency_edges[ang > np.radians(30)]
        if len(sharp):
            a, b = mesh.vertices[sharp[:, 0]], mesh.vertices[sharp[:, 1]]
            keep = np.ones(len(pts), bool)
            for lo in range(0, len(pts), 4000):
                p = pts[lo:lo + 4000]
                d = _seg_dist(p, a, b)
                keep[lo:lo + 4000] = d > edge_skip
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


if __name__ == "__main__":
    m = trimesh.load(sys.argv[1], force="mesh")
    lim = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
    p, t = thin_spots(m, lim)
    for i in np.argsort(t)[:20]:
        print(f"{t[i]:.2f} at {np.round(p[i], 1).tolist()}")
    print(f"{len(t)} samples under {lim}")
    sys.exit(1 if len(t) else 0)
