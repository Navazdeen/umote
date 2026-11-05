"""Collar and roller: printability, the cradle at rest and pressed, wheel and encoder placement."""
import os
import numpy as np
import pytest
import trimesh
from conftest import STL
from check_v5 import check_part


def load(name):
    return trimesh.load(os.path.join(STL, f"{name}.stl"), force="mesh")


def test_collar_prints_clean():
    assert check_part(os.path.join(STL, "collar.stl")) == []


@pytest.mark.parametrize("name", ["wheel", "cradle"])
def test_roller_parts_print_clean(name):
    assert check_part(os.path.join(STL, f"{name}.stl")) == []


def arm_bottom_z(m, P):
    """Lowest point of the cradle right above the tact plunger (ray cast upward)."""
    x, y = P["tact_c"]
    hits, _, _ = m.ray.intersects_location([[x, y, 0.0]], [[0, 0, 1]])
    assert len(hits), "no cradle above the tact switch"
    return hits[:, 2].min()


def test_roller_not_pressed_at_rest(P):          # Review Focus 1
    plunger_top = P["floor_t"] + P["tact"][2]
    z = arm_bottom_z(load("asm_cradle"), P)
    assert plunger_top - 0.02 <= z <= plunger_top + 0.05


def test_roller_presses_when_pushed(P):
    plunger_top = P["floor_t"] + P["tact"][2]
    assert arm_bottom_z(load("asm_cradle_pressed"), P) <= plunger_top - 0.2


def test_wheel_keeps_off_the_back_when_pressed():
    assert load("asm_wheel_pressed").bounds[0][2] >= 0.4 + 0.1      # back skin under the wheel is 0.4


def test_wheel_proud(P):
    assert load("asm_wheel").bounds[1][2] - P["T"] == pytest.approx(P["whl_proud"], abs=0.05)


def test_encoder_off_centre():
    b = load("asm_ec11").bounds
    assert abs((b[0][0] + b[1][0]) / 2) >= 9


def test_roller_parts_clear_each_other():
    parts = {k: load(f"asm_{k}") for k in ["collar", "wheel", "cradle", "ec11"]}
    for a, b in [("collar", "wheel"), ("collar", "cradle"), ("collar", "ec11"), ("wheel", "cradle")]:
        hit = trimesh.boolean.intersection([parts[a], parts[b]], engine="manifold")
        assert hit.is_empty or hit.volume < 1e-3, f"{a} hits {b}"
