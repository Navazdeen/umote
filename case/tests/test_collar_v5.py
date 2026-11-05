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


def floor_under_tact(P):
    """the real floor the tact switch stands on: ray cast down onto the collar at the switch"""
    x, y = P["tact_c"]
    hits, _, _ = load("asm_collar").ray.intersects_location([[x, y, 10.0]], [[0, 0, -1]])
    return hits[:, 2].max()


def test_tact_stands_on_floor_t(P):
    assert floor_under_tact(P) == pytest.approx(P["floor_t"], abs=0.02)


def test_roller_not_pressed_at_rest(P):          # Review Focus 1
    plunger_top = floor_under_tact(P) + P["tact"][2]
    z = arm_bottom_z(load("asm_cradle"), P)
    assert plunger_top - 0.02 <= z <= plunger_top + 0.05


def test_roller_presses_when_pushed(P):
    plunger_top = floor_under_tact(P) + P["tact"][2]
    assert arm_bottom_z(load("asm_cradle_pressed"), P) <= plunger_top - 0.2


def test_wheel_keeps_off_the_back_when_pressed():
    """0.25 or more to the collar's closed back skin under the wheel, pressed"""
    w = load("asm_wheel_pressed"); c = load("asm_collar")
    hits, _, _ = c.ray.intersects_location([[0, w.bounds[0][1] + (w.bounds[1][1] - w.bounds[0][1]) / 2, 5.0]], [[0, 0, -1]])
    assert w.bounds[0][2] - hits[:, 2].max() >= 0.25


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


def test_pressed_wheel_clears_the_battery_door():
    h = trimesh.boolean.intersection([load("asm_wheel_pressed"), load("asm_magnet_plate")], engine="manifold")
    assert h.is_empty or h.volume < 1e-3
