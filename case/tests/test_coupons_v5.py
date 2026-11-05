"""The two test prints exist and print clean (several bodies each: the parts print side by side)."""
import os
import pytest
from conftest import STL
from check_v5 import check_part


@pytest.mark.parametrize("name", ["snap_test", "roller_test"])
def test_coupon_prints_clean(name):
    path = os.path.join(STL, f"{name}.stl")
    assert os.path.exists(path), f"{name}.stl not exported"
    assert check_part(path, allow_bodies=True) == []
