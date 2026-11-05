"""Tests for case/check_v5.py on simple solids (z is the print direction)."""
import os, sys
import pytest
import trimesh

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from check_v5 import check_part, bridge_spans


@pytest.fixture
def save(tmp_path):
    def _save(mesh, name="part.stl"):
        p = tmp_path / name
        mesh.export(p)
        return str(p)
    return _save


def box(x, y, z, at=(0, 0, 0)):
    b = trimesh.creation.box(extents=[x, y, z])
    b.apply_translation([at[0] + x / 2, at[1] + y / 2, at[2] + z / 2])
    return b


def union(*ms):
    return trimesh.boolean.union(list(ms), engine="manifold")


def test_box_passes(save):
    assert check_part(save(box(50, 20, 10))) == []


def test_too_long_for_bed(save):
    assert any("bed" in p for p in check_part(save(box(190, 20, 10))))


def test_two_bodies(save):
    assert any("bodies" in p for p in check_part(save(trimesh.util.concatenate([box(10, 10, 10), box(10, 10, 10, at=(20, 0, 0))]))))


def test_two_bodies_allowed(save):
    two = trimesh.util.concatenate([box(10, 10, 10), box(10, 10, 10, at=(20, 0, 0))])
    assert check_part(save(two), allow_bodies=True) == []


def test_overhang_found(save):
    # a 56 deg downward face above the first layer: a wedge leaning out
    wedge = trimesh.Trimesh(vertices=[[0, 0, 0], [10, 0, 0], [0, 10, 0], [10, 10, 0],
                                      [0, 0, 10], [25, 0, 10], [0, 10, 10], [25, 10, 10]],
                            faces=[[0, 2, 1], [1, 2, 3], [4, 5, 6], [5, 7, 6], [0, 1, 5], [0, 5, 4],
                                   [2, 6, 7], [2, 7, 3], [0, 4, 6], [0, 6, 2], [1, 3, 7], [1, 7, 5]])
    assert wedge.is_watertight
    assert any("overhang" in p for p in check_part(save(wedge)))


def test_bridge_span(save):
    # two 10 mm pillars, 20 mm apart, joined by a roof: a 20 mm flat bridge
    b = union(box(5, 10, 10), box(5, 10, 10, at=(25, 0, 0)), box(30, 10, 2, at=(0, 0, 10)))
    assert max(bridge_spans(b)) == pytest.approx(20, abs=0.5)


def test_long_bridge_fails(save):
    b = union(box(5, 10, 10), box(5, 10, 10, at=(25, 0, 0)), box(30, 10, 2, at=(0, 0, 10)))
    assert any("bridge" in p for p in check_part(save(b), max_bridge=17))


def test_thin_step_is_not_a_bridge(save):
    # a 30 x 30 block on a 29.8 x 29.8 one: a 0.1 mm ledge all round at z 0.2, not a bridge
    b = union(box(29.8, 29.8, 0.2, at=(0.1, 0.1, 0)), box(30, 30, 3, at=(0, 0, 0.2)))
    assert check_part(save(b)) == []
