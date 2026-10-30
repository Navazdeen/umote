"""Printability check for exported STLs (z is the print direction): watertight, bodies,
overhangs steeper than 45 deg and flat downward bridges, both above the first layer."""
import sys, trimesh, numpy as np
for f in sys.argv[1:]:
    m = trimesh.load(f); n = m.face_normals; c = m.triangles_center; a = m.area_faces
    down = (n[:, 2] < -0.7072) & (c[:, 2] > m.bounds[0][2] + 0.15)
    print(f"{f}: watertight {m.is_watertight}, bodies {m.body_count}, "
          f"overhang >45deg {a[down & (n[:, 2] >= -0.999)].sum():.2f} mm2, flat bridges {a[down & (n[:, 2] < -0.999)].sum():.2f} mm2")
