"""Keys: printability, and Review Focus 4 (a rocker pressed at one end moves only that switch)."""
import os
import numpy as np
import pytest
import trimesh
from conftest import STL
from check_v5 import check_part


def load(name):
    return trimesh.load(os.path.join(STL, f"{name}.stl"), force="mesh")


@pytest.mark.parametrize("name", ["caps", "dpad_ring"])
def test_keys_print_clean(name):
    assert check_part(os.path.join(STL, f"{name}.stl"), allow_bodies=name == "caps") == []


def bore_ceiling(m, x, y):
    hits, _, _ = m.ray.intersects_location([[x, y, 0.0]], [[0, 0, 1]])
    assert len(hits), f"no cap over ({x}, {y})"
    return hits[:, 2].min()


def stem_travel(P, name):
    bp = {"VOL+": (8.5, 77.0), "VOL-": (8.5, 90.0)}[name]
    x, y = P["bb_w"] / 2 - bp[0], P["bb_y0"] + bp[1]
    return bore_ceiling(load("caps_asm"), x, y) - bore_ceiling(load("caps_asm_rocker_tilt"), x, y)


def test_rocker_one_end_only(P):          # Review Focus 4
    assert stem_travel(P, "VOL+") >= 0.25
    assert stem_travel(P, "VOL-") <= 0.05


def test_ok_has_a_nub(P):
    m = load("caps_asm")
    ok = (P["bb_w"] / 2 - 21.5, P["bb_y0"] + 25.5)
    hits, _, _ = m.ray.intersects_location([[ok[0], ok[1], 40]], [[0, 0, -1]])
    assert hits[:, 2].max() >= P["T"] + P["cap_proud"] + 0.5


def test_dpad_ring_proud(P):
    assert load("asm_dpad_ring").bounds[1][2] == pytest.approx(P["T"] + 0.5, abs=0.02)


def test_tipped_rocker_clears_the_panel():
    h = trimesh.boolean.intersection([load("caps_asm_rocker_tilt"), load("asm_key_panel")], engine="manifold")
    assert h.is_empty or h.volume < 0.1
