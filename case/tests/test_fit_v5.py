"""The whole assembly: no undesigned collisions (includes the USB-C plug and both wire paths,
Review Focus 2 and 5) and every key-half print part prints clean."""
import os
import pytest
from conftest import STL
from check_v5 import check_part
import fit_check_v5


@pytest.mark.parametrize("name", ["key_body", "key_panel"])
def test_key_parts_print_clean(name):
    assert check_part(os.path.join(STL, f"{name}.stl")) == []


def test_fit_check_clean():
    assert fit_check_v5.main([STL, "0.15"]) == 0
