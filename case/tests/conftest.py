import json, os, sys
import pytest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))
STL = os.path.join(HERE, "..", "stl_v5")


@pytest.fixture(scope="session")
def P():
    return json.load(open(os.path.join(STL, "params.json")))
