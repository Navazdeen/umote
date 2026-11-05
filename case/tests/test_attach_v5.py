"""Features must be attached and walls printable: the user found the prongs floating, the reviewer a
0.19 mm collar floor."""
import os
import numpy as np
import pytest
import trimesh
from conftest import STL


def load(name):
    return trimesh.load(os.path.join(STL, f"{name}.stl"), force="mesh")


def column_solid(m, x, y, z0, z1, step=0.2):
    """True if every point on the vertical line (x, y, z0..z1) is inside the mesh"""
    zs = np.arange(z0, z1 + 1e-9, step)
    return bool(m.contains(np.c_[np.full_like(zs, x), np.full_like(zs, y), zs]).all())


@pytest.mark.parametrize("body,yside", [("asm_head_body", -1), ("asm_key_body", 1)])
def test_prong_roots_stand_on_the_floor(P, body, yside):
    """each prong's root is a pillar from the floor up, inside its own body"""
    m = load(body)
    y = (P["y_head_end"] - 0.4) if yside < 0 else (P["y_key_start"] + 1.5)   # the head pillar is 0.8 long
    for sx in (-1, 1):
        x = sx * 20.5
        if body == "asm_head_body":     # the head is bent: test in its own coordinates via the straight part
            m = load("head_body")
        assert column_solid(m, x, y, P["floor_t"] - 0.2, P["floor_t"] + 4.0), f"prong root at x {x} isn't a pillar"


def test_collar_back_is_solid_under_the_cradle(P):
    """a real floor (>= 0.8) under the EC11 and the cradle, and under the tact switch up to floor_t"""
    c = load("asm_collar")
    assert column_solid(c, 9.0, P["cy"], 0.1, 0.9)                         # under the EC11
    tx, ty = P["tact_c"]
    assert column_solid(c, tx, ty, 0.1, P["floor_t"] - 0.1)                # the tact switch sits on floor_t
