"""Battery door and dock."""
import os
import numpy as np
import pytest
import trimesh
from conftest import STL
from check_v5 import check_part


def load(name):
    return trimesh.load(os.path.join(STL, f"{name}.stl"), force="mesh")


@pytest.mark.parametrize("name", ["magnet_plate", "dock"])
def test_dock_parts_print_clean(name):
    assert check_part(os.path.join(STL, f"{name}.stl")) == []


def test_pogo_travel(P):
    """each P75 tip stands 0.6-0.9 proud of the pocket floor (= the remote's end face): its compression"""
    tips = load("asm_pogo")
    proud = P["L"] - tips.bounds[0][1]
    assert 0.6 <= proud <= 0.9


def test_plate_flush(P):
    """the door's outer face is flush with the back (z 0) where the battery is"""
    m = load("asm_magnet_plate")
    hits, _, _ = m.ray.intersects_location([[0, P["batt_y0"] + 50, -5]], [[0, 0, 1]])
    assert abs(hits[:, 2].min()) <= 0.1
