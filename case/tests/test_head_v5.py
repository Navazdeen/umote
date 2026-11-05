"""Head half: printability, the USB-C opening and the IR LED aim."""
import os
import numpy as np
import pytest
import trimesh
from conftest import STL
from check_v5 import check_part


def load(name):
    return trimesh.load(os.path.join(STL, f"{name}.stl"), force="mesh")


@pytest.mark.parametrize("name", ["head_body", "head_panel"])
def test_head_parts_print_clean(name):
    assert check_part(os.path.join(STL, f"{name}.stl")) == []


def notch_centre_x(name, y=1.5):
    """Centre of the USB-C opening in the tip wall: the hole in the body's section at y."""
    sec = load(name).section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    poly, to3d = sec.to_2D()
    holes = [h for p in poly.polygons_full for h in p.interiors]
    assert holes, "no opening in the tip wall"
    ring = np.array(max(holes, key=lambda h: len(h.coords)).coords)
    xs = trimesh.transform_points(np.c_[ring, np.zeros(len(ring))], to3d)[:, 0]
    return (xs.min() + xs.max()) / 2


def test_usb_notch_centre(P):
    assert notch_centre_x("head_body") == pytest.approx(P["usb_x"], abs=0.05)


def bore_centre_z(mesh, y, x0, z0):
    """Centre height of the IR clip's bore (radius ~1.55) in the panel's section at y."""
    sec = mesh.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    pts = sec.vertices[:, [0, 2]]
    r = np.hypot(pts[:, 0] - x0, pts[:, 1] - z0)
    arc = pts[(r > 1.2) & (r < 1.9)]
    assert len(arc) >= 6, f"no bore arc at y {y}"
    # least-squares circle fit
    A = np.c_[2 * arc, np.ones(len(arc))]
    c = np.linalg.lstsq(A, (arc ** 2).sum(1), rcond=None)[0]
    return c[1]


def ir_axis_angle(P):
    """Angle of the IR LED bore in straight head coordinates (deg, negative = tip end lower)."""
    m = load("head_panel")
    m.apply_transform(np.diag([1, 1, -1, 1])); m.apply_translation([0, 0, P["T"]])   # print -> model
    y0, y1 = P["tip_wall"] + 2.0, P["tip_wall"] + 4.5
    z0 = bore_centre_z(m, y0, P["ir_x"], P["ir_z"])
    z1 = bore_centre_z(m, y1, P["ir_x"], P["ir_z"])
    return np.degrees(np.arctan2(z1 - z0, y1 - y0)) * -1


def test_ir_clips_tilted(P):
    assert ir_axis_angle(P) == pytest.approx(-P["theta"], abs=0.5)
