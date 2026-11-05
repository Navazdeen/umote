"""Review Focus 3: the head panel opens with a 0.4 mm card in the tip seam."""
import json, os
import numpy as np
import trimesh
from conftest import STL

P = json.load(open(os.path.join(STL, "params.json")))


def e_in(z):
    if z < P["roll_z"]:
        return 0.0
    return P["roll"] * ((z - P["roll_z"]) / (P["T"] - P["roll_z"])) ** 2


def card(t=0.4, half_w=4.0, steps=16):
    """a card following the middle of the (curved) tip seam, in short straight pieces, from above
    the face down to the ledge the panel rests on: there it is under the panel's edge and levers it"""
    def ring(z):
        zz = min(z, P["T"])
        ym = e_in(zz) + P["land"] + (P["pcl"] + P["pry_setback"]) / 2
        return [[sx * half_w, ym + sy * t / 2, z] for sx in (-1, 1) for sy in (-1, 1)]
    zs = [P["T"] + 1.0] + list(np.linspace(P["T"], P["pz0"] + 0.05, steps))
    pieces = [trimesh.convex.convex_hull(np.array(ring(a) + ring(b))) for a, b in zip(zs[:-1], zs[1:])]
    return trimesh.boolean.union(pieces, engine="manifold")


def overlap(a, b):
    h = trimesh.boolean.intersection([a, b], engine="manifold")
    return 0.0 if h.is_empty else h.volume


def test_card_reaches_below_the_panel():
    body = trimesh.load(os.path.join(STL, "head_body.stl"))
    panel = trimesh.load(os.path.join(STL, "head_panel.stl"))
    panel.apply_transform(np.diag([1, 1, -1, 1])); panel.apply_translation([0, 0, P["T"]])   # print -> model
    c = card()
    assert c.bounds[0][2] <= P["pz0"] + 0.1, "card doesn't reach the panel's underside"
    assert overlap(c, body) < 1e-3
    assert overlap(c, panel) < 1e-3
