"""Tests for case/check_struct.py on simple solids."""
import os, sys
import numpy as np
import pytest
import trimesh

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from check_struct import min_thickness, thickness_at


def box(x, y, z, at=(0, 0, 0)):
    b = trimesh.creation.box(extents=[x, y, z])
    b.apply_translation([at[0] + x / 2, at[1] + y / 2, at[2] + z / 2])
    return b


def diff(a, *b):
    return trimesh.boolean.difference([a, *b], engine="manifold")


def test_shell_thickness():
    shell = diff(box(40, 30, 20), box(40 - 4.8, 30 - 4.8, 20, at=(2.4, 2.4, 2.4)))   # 2.4 walls and floor, open top
    t, _ = min_thickness(shell)
    assert t == pytest.approx(2.4, abs=0.05)


def test_thin_slot_found():
    # a 6 mm plate with a pocket leaving 0.6 under it
    plate = diff(box(40, 30, 6), box(10, 10, 6, at=(15, 10, 0.6)))
    t, where = min_thickness(plate)
    assert t == pytest.approx(0.6, abs=0.05)
    assert 15 - 0.1 <= where[0] <= 25 + 0.1 and 10 - 0.1 <= where[1] <= 20 + 0.1


def test_thickness_at_point():
    plate = box(40, 30, 6)
    assert thickness_at(plate, [20, 15, 6.0], [0, 0, -1]) == pytest.approx(6.0, abs=0.01)


def wedge(top_x):
    """a 6 mm plate, 40 long at the bottom, top_x long at the top: its end is a wedge"""
    w = trimesh.Trimesh(vertices=[[0, 0, 0], [40, 0, 0], [0, 20, 0], [40, 20, 0],
                                  [0, 0, 6], [top_x, 0, 6], [0, 20, 6], [top_x, 20, 6]],
                        faces=[[0, 2, 1], [1, 2, 3], [4, 5, 6], [5, 7, 6], [0, 1, 5], [0, 5, 4],
                               [2, 6, 7], [2, 7, 3], [0, 4, 6], [0, 6, 2], [1, 3, 7], [1, 7, 5]])
    assert w.is_watertight
    return w


def test_blunt_wedge_edge_is_not_thin():
    # 60 deg (a panel's rolled edge, a 45 deg tongue): only the edge itself is thin
    t, _ = min_thickness(wedge(40 - 6 / np.tan(np.radians(60))))
    assert t > 1.2


def test_knife_edge_is_thin():
    # 20 deg: thin for mm back from its edge, and it is reported
    t, _ = min_thickness(wedge(40 - 6 / np.tan(np.radians(20))))
    assert t < 1.2
