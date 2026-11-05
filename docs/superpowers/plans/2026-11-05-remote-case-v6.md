# umote case v6 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the v5 case as v6 so it is stiff, joins solidly and holds the real EC11, per the v6 spec.

**Architecture:** `case/v6/` starts as a copy of `case/v5/` (OpenSCAD, one params file, part dispatcher). The key body now owns the wheel zone as two solid side rails. The head body joins the rails with two tenons and 2 M2. The collar is a wheel housing with the back ridge, dropped in from the back between the rails and screwed to them. New mesh checks (`case/check_struct.py`) gate every export.

**Tech Stack:** OpenSCAD 2021+, Python 3 + trimesh/manifold3d/shapely, pytest.

**Spec:** `docs/superpowers/specs/2026-11-05-remote-case-v6-design.md`

## Global Constraints

- Walls ≥ 2.4, back/face panels ≥ 2.0, lands ≥ 3.0, pockets ≥ 1.2 to the outer surface (spec §3).
- No supports; overhang ≤ 45°; bridges ≤ 17; longest bed dimension ≤ 210.
- Bought parts modelled with every feature (spec §3, §4.1).
- Coordinates as v5: origin at the tip centre, z = 0 on the back, +y towards the bottom, +x = BOOT side.

## Changes to the spec, found while planning (geometry forced them)

1. **T 15.8 → 16.6.** 2.0 floor + 2.0 face (was 1.6 + 1.6) cost 0.8 mm the button-board stack doesn't have (`bb_top + top_parts + 0.3 ≤ front_in` was already exactly met in v5).
2. **board_gap 18 → 24, L 218 → ~224.** An Ø18.6 wheel (2.0 skin over the EC11 at T 16.6) plus a carrier board 17 long (the EC11's pin rows are 14.5 apart) need ~18 mm of clear inside the collar. That also leaves ≥ 3 mm of collar top round the wheel window.
3. **Wheel off-centre, x = −4.** EC11 frame-top at x 8, bushing through a 2.5 bulkhead, carrier at x 12.5–14.1, all inside a collar ±17.6 so the rails (|x| ≥ 18) stay solid.
4. **Carrier board has no screws.** It spans floor to top skin (12.3 tall), so it can't turn; the bushing nut carries the encoder.
5. **Key panel: 2 screws (bottom zone) + top tongues in collar grooves + perimeter ledge/skirt**, not 6 screws. Mid-length screws would need holes in the button PCB (non-goal) or would hit the 46 mm battery beside the 43 mm board.
6. **Head panel: 4 M2 from the back through the display posts and the display's own corner holes into bosses under the panel.** This clamps the display too. There's no room for a side ledge (the LCD fills the width).
7. **The ridge is part of the collar**, as wide as the back, with 45° flanks and ends. The key body has to print back-down flat, so it can't carry a ridge.
8. **No battery thumb notch** (it would thin the 2.0 floor): a tape pull tab under the battery instead.

---

### Task 1: Structural mesh checks
**Files:** Create `case/check_struct.py`, `case/tests/test_check_struct.py`
**Interfaces — Produces:** `min_thickness(mesh, samples=4000, exclude=None) -> (float, np.ndarray points)`, which casts a ray inward from each surface sample along −normal and reports the distance to the next hit; `breakthrough(mesh_outer, mesh_part) -> float`.
- [ ] Tests: a 2.4-thick box shell → min ≈ 2.4; a box with a 0.6 slot near one face → min ≈ 0.6 located at the slot.
- [ ] Implement with `trimesh.ray` (offset origin 1e-3 along the ray).
- [ ] Run `pytest case/tests/test_check_struct.py` → pass. Commit.

### Task 2: v6 scaffold and params
**Files:** Copy `case/v5/*` → `case/v6/` (`umote_v5.scad` → `umote_v6.scad`), `case/v6/export.sh` (OUT=stl_v6), `case/tests/conftest.py` gets `STL6`/`P6`.
- [ ] params: W 52, wall 2.4, T 16.6, floor_t 2.0, pan_t 2.0, land 2.4, board_gap 24, the EC11 table from spec §4.1, whl_d 18.6, cap_hole 9.8, side_clr 0.6, y_head_end = db_end + 1, y_key_start = bb_y0 − 1, asserts for every spec-§3 number that params can express.
- [ ] Export params → params.json. Commit.

### Task 3: Collar (wheel housing) + EC11/carrier/wheel models
**Files:** `case/v6/collar.scad`, `case/tests/test_collar_v6.py`
- [ ] Tests: EC11 asm (body, bushing, shaft, nut, pins) collides with nothing but the bulkhead hole it passes through; the swept wheel volume is clear; collar top lands ≥ 3.0; ridge floor under the wheel ≥ 2.0; wire channel ≥ 4 × 4 clear through both end walls.
- [ ] Implement; export `collar`, `wheel`, `asm_*`; run the tests. Commit.

### Task 4: Head body + head panel
**Files:** `case/v6/head_half.scad`, `case/tests/test_head_v6.py`
- [ ] Tests: no snaps/catches; 4 through-holes post→PCB hole→panel boss line up (one axis each); the tenons are printable (check_v5 on head_body); min_thickness ≥ 2.4 on the walls.
- [ ] Implement; export; test. Commit.

### Task 5: Key body + key panel
**Files:** `case/v6/key_half.scad`, `case/v6/dock.scad` (magnet pockets), `case/tests/test_key_v6.py`
- [ ] Tests: floor solid under the whole battery (column checks on a grid); the rails are solid; mortises match the tenons (fit check); magnet/pad pockets ≥ 1.2 to the outer surface; 2 panel screws line up; panel tongues sit in the collar grooves.
- [ ] Implement; export; test. Commit.

### Task 6: Fit check v6, print check, test pieces
**Files:** `case/fit_check_v6.py` (from v5, cradle/tact removed, EC11/carrier/nut added), `case/v6/umote_v6.scad` test pieces `t1_wheel_zone`, `t2_key_corner`, `t3_bottom_end`.
- [ ] Fit check: zero undesigned collisions. Print check (bed 210) and min_thickness on every print part. Commit.

### Task 7: Release
- [ ] Export all, build the viewer, upload `/stl/v6.0/` (whole set, SHA-checked), update HANDOFF. Commit.

## Review Focus
1. Head ↔ key joint under bending (holding the remote by the key half and pressing the screen): the tenons and the 2 screws carry it; the fit check must show the end faces bearing.
2. The real EC11 clone's frame lug against the bulkhead: T1 test piece; bend the lug flat if needed.
3. Battery out through the front: lifting the key panel with the board still clipped to it, with the wires long enough.
4. Elephant's foot on face-down panels narrowing the key holes: the 0.4 chamfers stay on.
5. Wires head ↔ key through the collar's channel past the wheel.
