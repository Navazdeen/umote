"""v6 structural rework (spec 2026-11-05-remote-case-v6-design.md): the checks the v5.1 print would
have failed. Run case/v6/export.sh all first (STLs in case/stl_v6)."""
import json, os
import numpy as np
import pytest
import trimesh
from check_struct import thin_spots
from check_v5 import check_part

STL6 = os.path.join(os.path.dirname(__file__), "..", "stl_v6")
PRINT = ["head_body", "head_panel", "frame", "ridge", "wheel", "key_body", "key_panel", "caps", "dpad_ring", "dock"]


@pytest.fixture(scope="module")
def P():
    return json.load(open(os.path.join(STL6, "params.json")))


def load(name):
    return trimesh.load(os.path.join(STL6, f"{name}.stl"), force="mesh")


def solid(m, pts):
    return bool(m.contains(np.asarray(pts, float)).all())


def ring(c, r, z0, z1, n=12, nz=5):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return [[c[0] + r * np.cos(t), c[1] + r * np.sin(t), z] for t in a for z in np.linspace(z0, z1, nz)]


# ---------- printability ----------
@pytest.mark.parametrize("part", PRINT)
def test_prints_without_supports_on_a_220_bed(part):
    assert check_part(os.path.join(STL6, f"{part}.stl"), bed=210, allow_bodies=part == "caps") == []


# ---------- thickness: nothing under 1.2 except the named design features ----------
# boxes in each part's print coordinates: (x0, x1, y0, y1, z0, z1, why)
EXCEPT = {
    "head_body": [(-7.5, 7.5, 1.5, 2.6, 3.0, 11.0, "USB-C stop skin 0.6 (v4/v5, printed fine; the plug must reach the socket)"),
                  (-15.5, -8.5, -0.5, 2.6, 10.5, 15.0, "IR window skin ~0.95 under the top roll (thin on purpose; the display PCB is under the LEDs)"),
                  (8.5, 15.5, -0.5, 2.6, 10.5, 15.0, "IR window skin"),
                  (-19.2, -17.9, 80, 86, 0, 3.0, "tenon pin hole: 1.15 to the tenon's inner face, which bears on the frame wall"),
                  (17.9, 19.2, 80, 86, 0, 3.0, "tenon pin hole")],
    "head_panel": [(-16, -8.5, 1.5, 9, 0, 6, "IR LED clip saddle"), (8.5, 16, 1.5, 9, 0, 6, "IR LED clip saddle"),
                   (-20.5, -14.5, 3.5, 10, 0, 6.5, "display boss d4 (clears the LCD)"), (14.5, 20.5, 3.5, 10, 0, 6.5, "display boss"),
                   (-20.5, -14.5, 69.5, 76.5, 0, 6.5, "display boss"), (14.5, 20.5, 69.5, 76.5, 0, 6.5, "display boss")],
    "key_panel": [(8, 14.5, 108, 114, 0, 3, "POWER / D-pad web 0.6: both fixed by the button PCB (as v5)"),
                  (-2, 2, 145, 147, 0, 3, "HOME / D-pad web 1.1: both fixed by the button PCB"),
                  (-23.5, -20.5, 0, 230, 0, 9.5, "board clip beam 1.0 (flexes)"), (20.5, 23.5, 0, 230, 0, 9.5, "board clip beam 1.0")],
}


@pytest.mark.parametrize("part", ["head_body", "head_panel", "frame", "ridge", "key_body", "key_panel", "wheel", "dock"])
def test_no_thin_material(part):
    pts, t = thin_spots(load(part), 1.2)
    ok = np.zeros(len(pts), bool)
    for x0, x1, y0, y1, z0, z1, _ in EXCEPT.get(part, []):
        ok |= (pts[:, 0] >= x0) & (pts[:, 0] <= x1) & (pts[:, 1] >= y0) & (pts[:, 1] <= y1) & (pts[:, 2] >= z0) & (pts[:, 2] <= z1)
    bad = pts[~ok]
    assert len(bad) == 0, f"{len(bad)} thin samples, e.g. {np.round(bad[:5], 1).tolist()} ({np.round(t[~ok][:5], 2).tolist()})"


# ---------- F1: the key half has a real back and real walls ----------
def test_key_floor_is_solid_under_the_battery(P):
    m = load("asm_key_body")
    pts = [[x, y, z] for x in np.arange(-21, 21.1, 3) for y in np.arange(P["batt_y0"], P["batt_end"], 7)
           for z in np.linspace(0.1, P["floor_t"] - 0.05, 3)]
    assert solid(m, pts)


@pytest.mark.parametrize("body,ys", [("asm_key_body", [110, 140, 170, 205]), ("head_body", [15, 40, 65])])
def test_side_walls_are_2_4(P, body, ys):
    m = load(body)
    w = P["W"] / 2
    pts = [[sx * x, y, z] for sx in (-1, 1) for y in ys for z in (7.5, 9.5, 11.0) for x in np.linspace(w - P["wall"] + 0.05, w - 0.05, 4)]
    assert solid(m, pts)


@pytest.mark.parametrize("panel,pts", [("asm_key_panel", [[0, 175, 0], [-16, 200, 0], [16, 160, 0], [0, 105, 0]]),
                                       ("head_panel", [[0, 4, 0], [-20, 40, 0], [20, 40, 0]])])
def test_panels_are_2_0(P, panel, pts):
    m = load(panel)
    if panel == "head_panel":      # print orientation: face down, 0..pan_t
        col = [[x, y, z] for x, y, _ in pts for z in np.linspace(0.05, P["pan_t"] - 0.05, 4)]
    else:
        col = [[x, y, z] for x, y, _ in pts for z in np.linspace(P["pz0"] + 0.05, P["T"] - 0.05, 4)]
    assert solid(m, col)


# ---------- F2/F5: the joint and the wheel zone are screwed through real material ----------
def test_joint_screws_pass_through_the_tenons(P):
    head = load("asm_head_body")
    for x, y in P["s1"]:
        assert solid(head, ring([x, y], 1.3, 0.3, 1.8)), f"tenon round s1 at {x}"


def test_ridge_screws_bite_the_rails_and_the_frame(P):
    key, frame = load("asm_key_body"), load("asm_frame")
    for x, y in P["s2"]:
        assert solid(key, ring([x, y], 1.3, 0.5, 7.0)), f"rail round s2 at {x}"
    for x, y in P["s3"]:
        assert solid(frame, ring([x, y], 1.5, P["floor_t"] + 0.3, P["floor_t"] + 6.5)), f"bulkhead boss round s3 at {y}"


def test_key_panel_screws_bite_its_bosses(P):
    m = load("asm_key_panel")
    for x, y in P["ps"]:
        assert solid(m, ring([x, y], 1.6, P["pz0"] - 3.5, P["pz0"] - 0.5))


def test_head_panel_bosses_sit_on_the_display_holes(P):
    m = load("head_panel")                     # print orientation: z = T - z_assembled
    for x, y in P["holes"]:
        z0, z1 = P["T"] - P["pz0"] + 0.3, P["T"] - P["db_top"] - 1.0
        assert solid(m, ring([x, y], 1.6, z0, z1))


def test_ec11_is_the_real_part(P):
    b = load("asm_ec11").bounds
    xf = P["ec11_xf"]
    assert b[0][0] == pytest.approx(xf - P["ec11_shaft"][1], abs=0.05)                     # the 20 mm shaft
    assert b[1][0] >= xf + P["ec11_h"] + P["carrier"][0]                                    # pins through the carrier
    assert b[1][2] - b[0][2] == pytest.approx(P["ec11_w"], abs=0.05)


def test_collar_top_lands_are_3(P):
    win = P["win"]
    assert P["cy"] - win[1] / 2 - P["y_head_end"] >= 3.0
    assert P["y_key_start"] - (P["cy"] + win[1] / 2) >= 3.0


def test_ridge_closes_the_back_under_the_wheel(P):
    r = load("asm_ridge")
    z_well = P["axle_z"] - P["whl_d"] / 2 - 0.5
    pts = [[P["whl_x"] + dx, P["cy"] + dy, z] for dx in (-3, 0, 3) for dy in (-3, 0, 3) for z in np.linspace(-P["ridge_h"] + 0.1, z_well - 0.1, 4)]
    assert solid(r, pts)


# ---------- F6/F7: no snaps ----------
def test_panels_are_one_body_with_no_snaps():
    for p in ("head_panel", "key_panel"):
        assert load(p).body_count == 1


# ---------- fit ----------
def test_fit_check_has_no_collisions():
    import fit_check_v6
    assert fit_check_v6.main([STL6]) == 0
