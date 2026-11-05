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
