"""v7 "Keel": one front shell + two flat back plates. The checks cover what the v6 print failed on
(the joint that would not close, screw holes too small) and what a printer needs (no supports, real
clearances, nothing thin). Run case/v7/export.sh all first (STLs in case/stl_v7)."""
import json, os
import numpy as np
import pytest
import trimesh
from check_struct import thin_spots
from check_v5 import check_part

STL7 = os.path.join(os.path.dirname(__file__), "..", "stl_v7")
PRINT = ["shell", "head_back", "key_back", "wheel", "caps", "dpad_ring", "dock", "pogo_plate_a", "pogo_plate_b",
         "dock_plate_a", "dock_plate_b", "t0_screw_gauge", "t1_wheel_zone", "t2_bottom_end"]
MULTI = {"caps", "t1_wheel_zone", "t2_bottom_end"}


@pytest.fixture(scope="module")
def P():
    return json.load(open(os.path.join(STL7, "params.json")))


def load(name):
    return trimesh.load(os.path.join(STL7, f"{name}.stl"), force="mesh")


def solid(m, pts):
    return bool(m.contains(np.asarray(pts, float)).all())


def empty(m, pts):
    return not bool(m.contains(np.asarray(pts, float)).any())


def ring(c, r, z0, z1, n=12, nz=5):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return [[c[0] + r * np.cos(t), c[1] + r * np.sin(t), z] for t in a for z in np.linspace(z0, z1, nz)]


def zb(P, y):
    return P["zb_tip"] + P["kh"] * y if y <= P["y_ap"] else P["z_ap"] + P["kk"] * (y - P["y_ap"])


# ---------- printability ----------
# The back plates print outside down, so each countersink is a 45 deg cone that the plate's 2-3 deg
# tilt takes to 47-48 deg: a ring 0.8 mm tall round a 2.6 mm hole. Those are allowed; nothing else is.
CSK_PARTS = {"head_back": ("holes", "s2"), "key_back": ("ps",), "t1_wheel_zone": None, "t2_bottom_end": None}


@pytest.mark.parametrize("part", PRINT)
def test_prints_without_supports_on_a_220_bed(part, P):
    path = os.path.join(STL7, f"{part}.stl")
    allow = 45.0 if part in CSK_PARTS else 1.0
    assert check_part(path, bed=210, allow_bodies=part in MULTI, max_overhang_area=allow) == []
    if CSK_PARTS.get(part):
        m = trimesh.load(path, force="mesh")
        n, c = m.face_normals, m.triangles_center
        steep = (n[:, 2] < -0.7072) & (n[:, 2] > -0.999) & (c[:, 2] > m.bounds[0][2] + 0.15)
        k = P["kh"] if part == "head_back" else P["kk"]
        cs, sn = 1 / np.hypot(1, k), -k / np.hypot(1, k)                 # the print turn about x: y' = y cos - z sin
        axes = np.array([[x, y * cs - zb(P, y) * sn] for key in CSK_PARTS[part] for x, y in P[key]])
        d = np.linalg.norm(c[steep][:, None, :2] - axes[None], axis=2).min(axis=1)
        assert (d < 3.0).all(), f"overhang away from a countersink: {np.round(c[steep][d >= 3.0][:5], 1).tolist()}"


def test_plates_lie_flat_on_their_outside():
    for p in ("head_back", "key_back"):
        m = load(p)
        n, c = m.face_normals, m.triangles_center
        flat = m.area_faces[(n[:, 2] < -0.999) & (c[:, 2] < m.bounds[0][2] + 0.05)].sum()
        assert flat > 2500, f"{p}: only {flat:.0f} mm2 on the bed"


def test_shell_is_a_true_flip_not_a_mirror(P):
    """POWER is at +x and the mic at -x (face up). Turn the printed shell back over about y and the
    POWER hole must be where the assembled model has it (v6's face-down panels were mirrored)."""
    m = load("shell").copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 4, [0, 0, 1]))
    m.apply_translation([0, P["L"] / 2, 0])
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [0, 1, 0]))
    m.apply_translation([0, 0, P["T"]])
    a = load("asm_shell")
    power = [P["bb_w"] / 2 - 7.5, P["bb_y0"] + 6.0, P["T"] - 1.0]
    mirror = [-power[0], power[1], power[2]]
    assert empty(a, [power]) and solid(a, [mirror])
    assert empty(m, [power]) and solid(m, [mirror])


# ---------- thickness: nothing under 1.2 except the named design features ----------
# boxes in each part's own (exported) coordinates: (x0, x1, y0, y1, z0, z1, why)
EXCEPT = {
    "asm_shell": [(-7.6, 7.6, 1.7, 2.7, 2.5, 11.8, "USB-C stop skin 0.6 (as v4-v6: the plug must reach the socket)"),
                  (-15, -9, 0, 7.6, 12.0, 14.7, "IR window skin ~0.9 under the face roll, and the LED saddle"),
                  (9, 15, 0, 7.6, 12.0, 14.7, "IR window skin and LED saddle"),
                  (-20.5, -14.5, 70.8, 72.4, 10.4, 14.7, "display boss, flat side towards the LCD: 1.05"),
                  (14.5, 20.5, 70.8, 72.4, 10.4, 14.7, "display boss, flat side"),
                  (8, 14.5, 109, 115, 14.5, 16.7, "POWER / D-pad web 0.6: both fixed by the button PCB (as v5, v6)"),
                  (-2, 2, 145, 148.5, 14.5, 16.7, "HOME / D-pad web 1.1: both fixed by the button PCB")],
    "pogo_plate_a": [(-5, 5, 219.5, 220.7, 4, 12.5, "backstop behind each brass pad insert, with its wire hole through (as v6)"),
                     (-16.5, -5.0, 219.5, 225.6, -0.1, 12.7, "10 mm magnet in a 12.45 plate: 1.1 above and below (as v6)"),
                     (5.0, 16.5, 219.5, 225.6, -0.1, 12.7, "10 mm magnet: 1.1 above and below")],
    "dock_plate_a": [(-13, 13, 1, 4, 3, 8, "magnet pocket floor 1.15 (as v6)")],
}


@pytest.mark.parametrize("part", ["asm_shell", "head_back", "key_back", "wheel", "dock", "pogo_plate_a", "pogo_plate_b", "dock_plate_a", "dock_plate_b"])
def test_no_thin_material(part):
    pts, t = thin_spots(load(part), 1.2)
    ok = np.zeros(len(pts), bool)
    for x0, x1, y0, y1, z0, z1, _ in EXCEPT.get(part, []):
        ok |= (pts[:, 0] >= x0) & (pts[:, 0] <= x1) & (pts[:, 1] >= y0) & (pts[:, 1] <= y1) & (pts[:, 2] >= z0) & (pts[:, 2] <= z1)
    bad = pts[~ok]
    assert len(bad) == 0, f"{len(bad)} thin samples, e.g. {np.round(bad[:8], 1).tolist()} ({np.round(t[~ok][:8], 2).tolist()})"


# ---------- structure ----------
def test_shell_is_one_piece_tip_to_end(P):
    s = load("asm_shell")
    assert s.body_count == 1
    assert s.bounds[1][1] - s.bounds[0][1] == pytest.approx(P["L"], abs=0.05)


def test_face_is_2_0(P):
    s = load("asm_shell")
    pts = [[x, y, z] for x, y in [(0, 4), (-20, 40), (20, 40), (0, 75), (15, P["cy"]), (0, P["bb_y0"] + 62), (-16, 205), (0, P["L"] - 4)]
           for z in np.linspace(P["pz0"] + 0.05, P["T"] - 0.05, 4)]
    assert solid(s, pts)


def test_side_walls_are_2_4(P):
    s = load("asm_shell")
    w = P["W"] / 2
    pts = [[sx * x, y, z] for sx in (-1, 1) for y in (15, 40, 65, 120, 150, 180, 205) for z in (8.5, 9.5, 11.0)
           for x in np.linspace(w - P["wall"] + 0.05, w - 0.05, 4)]
    assert solid(s, pts)


def test_back_plates_are_2_0_and_cover_the_whole_back(P):
    h, k = load("asm_head_back"), load("asm_key_back")
    for m, ys in ((h, [10, 30, 50, 70, 95]), (k, [110, 140, 170, 200, 218])):
        pts = [[x, y, zb(P, y) + d] for x in (-18, -6, 6, 18) for y in ys for d in (0.1, 1.0, P["back_t"] - 0.1)]
        assert solid(m, pts)


def test_back_is_closed_under_the_wheel(P):
    h = load("asm_head_back")
    pts = [[P["whl_x"] + dx, P["cy"] + dy, z] for dx in (-3, 0, 3) for dy in (-3, 0, 3)
           for z in np.linspace(zb(P, P["cy"] + dy) + 0.05, zb(P, P["cy"] + dy) + 1.9, 4)]
    assert solid(h, pts)


def test_keel_thickness(P):
    assert P["T"] - P["zb_tip"] == pytest.approx(15.6, abs=0.05)
    assert P["T"] - P["z_ap"] == pytest.approx(20.5, abs=0.05)
    e = load("asm_shell").bounds, load("asm_key_back").bounds
    assert e[1][0][2] == pytest.approx(P["z_ap"], abs=0.05)             # the keel is the lowest point


# ---------- screws: holes a printer can make, in real material ----------
def test_self_tap_holes_are_drawn_1_9(P):
    assert P["m2"][0] == pytest.approx(1.9) and P["m2"][1] >= 2.6
    s = load("asm_shell")
    for x, y in P["s2"] + P["ps"]:
        z = zb(P, y) + P["back_t"] + 3.0
        assert empty(s, ring([x, y], 0.85, z, z + 2, nz=3)), f"pilot at {x},{y} is under 1.7"
        assert solid(s, ring([x, y], 1.05, z, z + 2, nz=3)), f"pilot at {x},{y} is over 2.1"


def test_plate_screws_bite_real_material(P):
    s = load("asm_shell")
    for x, y in P["s2"] + P["ps"]:
        z = zb(P, y) + P["back_t"]
        assert solid(s, ring([x, y], 2.1, z + 1.0, z + P["tap_depth"] - 0.5)), f"under 1.1 round the pilot at {x},{y}"


def test_display_screws_are_all_m2x12(P):
    for x, y in P["holes"]:
        seat = max(P["z_seat"], zb(P, y) + P["m2"][3])
        bite = seat + 12.0 - P["db_top"]
        assert 2.5 <= bite <= P["boss_hole"], f"M2x12 at y {y:.1f}: {bite:.2f} mm in the boss"
    s = load("asm_shell")
    for x, y in P["holes"]:
        assert solid(s, ring([x, y], 1.7, P["db_top"] + 0.8, P["pz0"] - 0.1))
        assert solid(s, [[x + np.sign(x) * 4.5, y, P["db_top"] + 1.5]]), "boss has no web to the side wall"


def test_display_posts_reach_the_board(P):
    h = load("asm_head_back")
    for x, y in P["holes"]:
        assert solid(h, ring([x, y], 2.1, P["db_z0"] - 2.0, P["db_z0"] - 0.1))


def test_screw_count(P):
    assert len(P["holes"]) + len(P["s2"]) + len(P["ps"]) == 8


# ---------- the plates locate themselves and close ----------
def test_sliding_fits_are_at_least_0_25(P):
    assert P["fit"] >= 0.25 and P["lip_clr"] >= 0.3


def test_plates_have_lips_inside_the_walls(P):
    inner = P["W"] / 2 - P["wall"] - P["lip_clr"]
    for name, y in (("asm_head_back", 40), ("asm_key_back", 130)):
        m = load(name)
        z = zb(P, y) + P["back_t"]
        for sx in (-1, 1):
            assert solid(m, [[sx * (inner - 0.6), y, z + 0.5], [sx * (inner - 0.9), y, z + P["lip_h"] - 0.2]])
            assert empty(m, [[sx * (inner + 0.15), y, z + 0.5]])


def test_key_plate_hooks_under_the_cheeks(P):
    k = load("asm_key_back")
    assert k.bounds[0][1] < P["y_ap"] - 1.2
    import fit_check_v7 as fc
    lifted = k.copy(); lifted.apply_translation([0, 0, -1.5])
    assert fc.hit(lifted, load("asm_shell"), tol=0.05) is not None


def test_battery_sits_on_a_flat_deck(P):
    # v7.1: one level deck from lip to lip (v7.0 had three ribs), so the battery can be taped down
    k = load("asm_key_back")
    assert P["batt_z0"] >= P["seat_z"]
    xs = [-P["batt"][0] / 2 + 0.5, *P["rib_x"], -7.5, 7.5, P["batt"][0] / 2 - 0.5]
    ys = (P["batt_y0"] + 10, P["batt_y0"] + 50, P["batt_end"] - 10)
    assert solid(k, [[x, y, P["seat_z"] - 0.1] for x in xs for y in ys])
    assert not any(k.contains([[x, y, P["seat_z"] + 0.1] for x in xs for y in ys]))


@pytest.mark.parametrize("plate,body", [("asm_pogo_plate_a", "asm_shell"), ("asm_pogo_plate_b", "asm_shell"),
                                        ("asm_dock_plate_a", "asm_dock"), ("asm_dock_plate_b", "asm_dock")])
def test_contact_plates_fit_their_slots(plate, body):
    import fit_check_v7 as fc
    assert fc.hit(load(plate), load(body), tol=0.05) is None


@pytest.mark.parametrize("plate", ["asm_pogo_plate_a", "asm_pogo_plate_b"])
def test_contact_plate_cant_fall_out_of_the_end(plate):
    import fit_check_v7 as fc
    m = load(plate).copy(); m.apply_translation([0, 0.8, 0])
    assert fc.hit(m, load("asm_shell"), tol=0.05) is not None


def test_ec11_is_the_real_part(P):
    b = load("asm_ec11").bounds
    xf = P["ec11_xf"]
    assert b[0][0] == pytest.approx(xf - P["ec11_shaft"][1], abs=0.05)
    assert b[1][0] >= xf + P["ec11_h"] + P["carrier"][0]
    assert b[1][2] - b[0][2] == pytest.approx(P["ec11_w"], abs=0.05)


def test_wheel_window_lands_are_3(P):
    win = P["win"]
    assert P["cy"] - win[1] / 2 - P["y_head_end"] >= 3.0
    assert P["y_key_start"] - (P["cy"] + win[1] / 2) >= 3.0


# ---------- fit ----------
def test_fit_check_has_no_collisions():
    import fit_check_v7
    assert fit_check_v7.main([STL7]) == 0


# ---------- v7.2: 6x6x9.5 switches, roofed cap pockets, hooks that hold, carrier spacers ----------
import sys as _sys
_sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "pcb"))
import board as _B


def switch_xy(P):
    return [(P["bb_w"] / 2 - x, P["bb_y0"] + y) for (x, y, *_r) in _B.BUTTONS.values()]


def test_plunger_fits_bore(P):
    """The 5.7 plunger goes all the way into the hex bore and leaves >= 1.0 of cap over its tip."""
    assert P["sw_total"] == 9.5 and P["sw_body"] == 3.8
    assert P["sock"] == pytest.approx(P["act_top"] - (P["front_in"] - 0.8))
    assert P["act_top"] + 1.0 <= P["T"] + P["cap_proud"] + 1e-6


@pytest.mark.parametrize("asm", ["caps_asm", "caps_asm_pressed", "caps_asm_rocker_tilt"])
def test_caps_clear_switch_bodies(asm, P):
    """No cap, D-pad sector or rocker touches a 6 x 6 switch body, at rest, pressed 0.3 or tipped."""
    caps = load(asm)
    for x, y in switch_xy(P):
        body = trimesh.creation.box([6.0, 6.0, P["sw_body"]])
        body.apply_translation([x, y, P["bb_top"] + P["sw_body"] / 2])
        inter = trimesh.boolean.intersection([caps, body], engine="manifold")
        assert inter.is_empty or inter.volume < 1e-3, f"{asm} hits the switch at ({x:.1f}, {y:.1f}): {inter.volume:.3f} mm3"


def test_no_bridges_in_caps():
    """The only flat ceilings left in the caps are the hex bores' tops (~10 mm2 each)."""
    m = load("caps")
    z0 = m.bounds[0][2]
    for f, n, a in zip(m.facets, m.facets_normal, m.facets_area):
        if n[2] < -0.999 and m.triangles_center[f, 2].min() > z0 + 0.3:
            assert a < 11.0, f"bridged ceiling of {a:.1f} mm2 at {np.round(m.triangles_center[f[0]], 1).tolist()}"


def test_shell_is_the_printed_v7_1():
    """v7.2 doesn't touch the shell: the user has it printed. Boards and caps fit it as it is."""
    rel = os.path.join(os.path.dirname(__file__), "..", "..", "release", "v7.1", "shell.stl")
    assert open(os.path.join(STL7, "shell.stl"), "rb").read() == open(rel, "rb").read()


def hook_inner_x(m, P, y, z):
    x_wall = P["bb_w"] / 2 + 0.1
    s = m.section([0, 0, 1], [0, 0, z])
    v = s.vertices[(np.abs(s.vertices[:, 1] - y) < 3.5) & (s.vertices[:, 0] > x_wall - 1.0) & (s.vertices[:, 0] < x_wall + 2)]
    return v[:, 0].min()


def test_board_chamfer_sits_on_the_hook_slope(P):
    """The v7.1 hooks have a 45 deg slope where the board's bottom edge is. The boards' 0.5 x 45 deg
    bottom chamfer lies on it with the board at bb_z0, so the spacers press the board onto 4 slopes."""
    import make_stl_common as K
    m = load("asm_shell")
    for y in P["clip_y"]:
        for dz in (0.1, 0.25, 0.4):
            board_edge = P["bb_w"] / 2 - K.CHAMFER + dz          # the chamfer's x at height dz above the board's underside
            assert hook_inner_x(m, P, y, P["bb_z0"] + dz) == pytest.approx(board_edge, abs=0.06)


def test_spacers_land_on_the_face(P):
    """Each spacer rises from the board's top to the face's underside, 0.05 past it (the board rides
    0.05 up the hook slopes: a light preload), and its column misses the caps (at rest, pressed,
    tipped), the D-pad ring and every shell feature on the way."""
    import make_stl_common as K
    assert K.SPACER_H == pytest.approx(P["pz0"] - P["bb_top"] + K.PRELOAD) and K.PRELOAD == 0.05
    shell = load("asm_shell")
    others = [load(n) for n in ("caps_asm", "caps_asm_pressed", "caps_asm_rocker_tilt", "asm_dpad_ring")]
    for bx, by_ in K.SPACERS:
        x, y = P["bb_w"] / 2 - bx, P["bb_y0"] + by_
        h = P["pz0"] - P["bb_top"]
        col = trimesh.creation.cylinder(radius=K.SPACER_D / 2 + 0.3, height=h, sections=32)
        col.apply_translation([x, y, P["bb_top"] + h / 2])
        for m in others:
            i = trimesh.boolean.intersection([m, col], engine="manifold")
            assert i.is_empty or i.volume < 1e-3, f"spacer ({bx}, {by_}) hits a cap or the ring"
        below = col.copy(); below.apply_translation([0, 0, -0.02])
        i = trimesh.boolean.intersection([shell, below], engine="manifold")
        assert i.is_empty or i.volume < 1e-3, f"spacer ({bx}, {by_}) hits a shell feature on its way up"
        for r in (0, K.SPACER_D / 2 - 0.1):
            for a in np.linspace(0, 2 * np.pi, 8, endpoint=False):
                hit, _, _ = shell.ray.intersects_location([[x + r * np.cos(a), y + r * np.sin(a), P["bb_top"] + 0.1]], [[0, 0, 1]])
                assert hit[:, 2].min() == pytest.approx(P["pz0"], abs=0.02), f"spacer ({bx}, {by_}) does not land on the flat face"


@pytest.mark.parametrize("stl", ["button_carrier.stl", "button_board_holes.stl"])
def test_boards_have_spacers_and_chamfers(stl):
    import make_stl_common as K
    m = trimesh.load(os.path.join(os.path.dirname(__file__), "..", "..", "pcb", "stl", stl))
    assert m.is_watertight and m.body_count == 1
    assert m.extents[2] == pytest.approx(1.6 + K.SPACER_H, abs=0.01)
    assert m.extents[0] == pytest.approx(43.0, abs=0.01) and m.extents[1] == pytest.approx(112.0, abs=0.01)
    # 0.5 x 45 deg on both long edges, top and bottom of the 1.6 plate: full width only from 0.5 to 1.1
    for z, w in ((0.05, 43.0 - 2 * (0.5 - 0.05)), (0.8, 43.0), (1.55, 43.0 - 2 * (0.5 - 0.05))):
        cx, y = m.bounds[:, 0].mean(), m.bounds[0][1] + 25.0
        assert solid(m, [[cx - w / 2 + 0.03, y, z], [cx + w / 2 - 0.03, y, z]]), f"{stl} narrower than {w} at z {z}"
        assert empty(m, [[cx - w / 2 - 0.03, y, z], [cx + w / 2 + 0.03, y, z]]), f"{stl} wider than {w} at z {z}"


def test_copper_board_fits_the_v7_1_hooks_and_spacers():
    """The copper-tape board (make_stl.py): chamfered like the other boards, 0.2 recesses on the bed
    side for the 5 glue-in posts (button_spacers.stl), which reach the face with the same preload."""
    import make_stl_common as K
    pcb = os.path.join(os.path.dirname(__file__), "..", "..", "pcb", "stl")
    m = trimesh.load(os.path.join(pcb, "button_board_print.stl"))
    assert m.is_watertight and m.body_count == 1
    cx, y = m.bounds[:, 0].mean(), m.bounds[0][1] + 25.0
    for z, w in ((0.05, 42.1), (0.8, 43.0), (1.55, 42.1)):
        assert solid(m, [[cx - w / 2 + 0.03, y, z], [cx + w / 2 - 0.03, y, z]])
        assert empty(m, [[cx - w / 2 - 0.03, y, z], [cx + w / 2 + 0.03, y, z]])
    # recesses: printed copper side up and mirrored, so board (x, y) is at (43 - x, 112 - y) in the STL
    for bx, by_ in K.SPACERS:
        x, yy = m.bounds[0][0] + 43.0 - bx, m.bounds[0][1] + 112.0 - by_
        assert empty(m, [[x, yy, 0.1], [x + 1.9, yy, 0.1]]) and solid(m, [[x, yy, 0.3]])
    s = trimesh.load(os.path.join(pcb, "button_spacers.stl"))
    assert len(s.split()) == 5 and s.extents[2] == pytest.approx(K.SPACER_H + 0.2, abs=0.01)


def test_insulator_plate_fits_under_the_copper_board(P):
    """button_board_insulator.stl, a tray: 0.8 thick, on the copper tape over the 1.0 traces, clear of
    the shell (walls, clips, end stops), nothing over a solder joint, ribs only on trace tops."""
    pcb = os.path.join(os.path.dirname(__file__), "..", "..", "pcb", "stl")
    plate = trimesh.load(os.path.join(pcb, "button_board_insulator.stl"))
    assert plate.is_watertight and plate.extents[2] == pytest.approx(0.8, abs=0.01)
    # print frame -> case: stl (x, y) = (43 - bx, 112 - by), board (bx, by) -> case (bb_w/2 - bx, bb_y0 + by)
    m = plate.copy()
    m.apply_transform(np.diag([1, -1, 1, 1]))
    m.apply_translation([-P["bb_w"] / 2, P["bb_y0"] + P["bb_l"], P["bb_z0"] - 1.0 - 0.05 - 0.8])
    i = trimesh.boolean.intersection([m, load("asm_shell")], engine="manifold")
    assert i.is_empty or i.volume < 1e-3, f"the plate hits the shell: {i.volume:.3f} mm3"
    board = trimesh.load(os.path.join(pcb, "button_board_print.stl"))
    # every hole of the copper board (empty through its base) has the plate's pocket over it
    xs, ys = np.meshgrid(np.arange(0.5, 43, 0.5), np.arange(0.5, 112, 0.5))
    pts = np.c_[xs.ravel(), ys.ravel()]
    in_hole = ~board.contains(np.c_[pts, np.full(len(pts), 0.8)])
    hole_pts = pts[in_hole & board.contains(np.c_[pts + [0.9, 0], np.full(len(pts), 0.8)])]
    assert len(hole_pts) > 50
    assert not plate.contains(np.c_[hole_pts, np.full(len(hole_pts), 0.6)]).any(), "plastic over a solder joint"
    # tray (v7.2): inside the 1.5 rim, every rib point rests on a trace top
    inner = pts[(pts[:, 0] > 1.7) & (pts[:, 0] < 41.3) & (pts[:, 1] > 1.7) & (pts[:, 1] < 110.3)]
    rib = inner[plate.contains(np.c_[inner, np.full(len(inner), 0.6)])]
    assert len(rib) > 100, "no ribs"
    assert board.contains(np.c_[rib, np.full(len(rib), board.bounds[1][2] - 0.3)]).all(), "a rib off the traces"


def test_cap_walls_round_the_switch_pockets(P):
    """v7.2.1: the 6.6 pockets' corners broke through the caps' 8.6 walls just above the flange (the
    user's print had a hole at each corner). Above the pocket's square part every cap, sector and
    rocker keeps >= 0.5 of wall at the diagonals (r 3.8 from the switch is solid)."""
    caps = load("caps_asm")
    rockers = {(round(x, 1), round(y, 1)) for k, (x, y) in enumerate(switch_xy(P))
               if list(_B.BUTTONS)[k] in ("SW10", "SW11", "SW13", "SW14")}
    for x, y in switch_xy(P):
        rk = (round(x, 1), round(y, 1)) in rockers
        z0 = P["front_in"] - 0.8 - (0.3 if rk else 0.0) + (1.0 if rk else 0.6) + 0.25   # cap bottom + pocket square part + margin
        pts = [[x + 3.8 * np.cos(a), y + 3.8 * np.sin(a), z] for a in np.radians([45, 135, 225, 315])
               for z in np.linspace(z0, P["T"] + P["cap_proud"] - 1.5, 6)]
        assert solid(caps, pts), f"thin or open cap wall at a pocket corner, switch ({x:.1f}, {y:.1f})"
