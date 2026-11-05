# umote case v5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the v5 case described in the spec as printable STLs, along with:
- test coupons;
- a fit check, a print check and a viewer;
- the firmware support for the crease roller.

**Architecture:**
- **Model:** a set of small OpenSCAD files under `case/v5/` sharing one `params.scad`. One dispatcher (`umote_v5.scad`) writes every part in print orientation, assembled copies for checking, and a JSON dump of the parameters.
- **Checks:** Python scripts on trimesh. They assert printability and fit, reading the numbers from that JSON instead of copying them.
- **Firmware:** gains a host-tested roller decoder in `logic.h`.

**Tech Stack:** OpenSCAD 2021.01 (installed), Python 3 with trimesh + manifold3d + shapely (miniconda, as `fit_check.py` uses), pytest, ESPHome 2026.10.1, g++ for `firmware/test/test_logic.cpp`.

**Spec:** `docs/superpowers/specs/2026-11-05-remote-case-v5-design.md`. Concept geometry to start from: `docs/superpowers/specs/2026-11-05-remote-case-v5-assets/concept_d.scad` (with `concept_n9.scad`, `concept.scad`).

## Global Constraints

- Width 51 mm (inner 47, wall 2.0); thickness 15.8 mm at the edge; no palm swell.
- Board gap 18 mm (display end y 76.83 → button board y0 94.83); overall length ≈ 218 mm.
- Bend 8°, about a transverse axis on the face line (z = 15.8) at the head end, face concave.
- `usb_x = 0.22` (+x = BOOT side); every other USB-C, IR, LCD-window, cap-system and board value is copied from `case/remote_case.scad`.
- LiPo 46 × 105 × 5 (total, including the protection board). Leads exit at the tip end.
- Profile:
  - lower edge: quarter ellipse 3 × 7 with a 0.57 mm 45° foot;
  - straight band z 7–10.8;
  - upper edge: roll 2.2 mm over the top 5 mm;
  - land 1.4 mm;
  - face panels 1.6 mm, 0.15 mm gap.
- Roller:
  - EC11 on its side, off centre, and its own push is not used;
  - 16 mm wheel, 1.2 mm proud. Fallback order: 1.0 mm proud, then thin the collar top locally. Never a bump on the back;
  - A/B to MCP GPB1 (pin 2) and GPB5 (pin 6); press switch parallel to OK.
- Dock: 2 × P75-B1 probes in the dock; 2 flush brass heat-set inserts as pads; 10 × 2 N35 magnets outside the battery footprint; Schottky pad → +5V (C20/C22 or TP4054 pin 4).
- Head panel: 4 releasable snaps at the tip, opened with a card in the tip seam. No visible screw, hole or slot anywhere.
- Every part: watertight, one body, no overhang > 45° above the first layer, bridges ≤ 17 mm, longest bed dimension ≤ 180 mm.
- Fasteners M2.5. Heat-set insert holes 4.0 mm, ≥ 1.6 mm wall, depth ≥ insert + 1 mm.
- Uploads go to copyparty `/stl/` via `release/upload_to_copyparty.sh` (never upload secrets).
- No emoji or text-glyph icons in any viewer or page; use the inline-SVG icon set if icons are needed.

## Review Focus

1. **Roller set down or knocked:**
   - The remote resting on its back, or on its face (caps 3 mm proud), must not press or turn the roller.
   - The cradle's resting gap must stay ≥ 0.3 mm under the wheel's own weight.
   - Test: `test_roller_not_pressed_at_rest` (Task 5).
2. **USB-C plugged hard:**
   - The plug force goes into the display board screws, not the panel snaps.
   - The plug overmold must clear the notch floor exactly as in v4.
   - Test: the USB plug components in `fit_check_v5.py` (Task 6).
3. **Opening the head panel:**
   - A 0.4 mm card entering the tip seam must reach every snap's hook face.
   - Test: `test_card_reaches_snaps` (Task 7).
4. **Rocker pressed at one end:**
   - Only that switch's stem may move.
   - Test: `caps_asm_rocker_tilt` checked in Task 8.
5. **Wires through the collar:**
   - A 4 mm-diameter bundle path from the battery's tip end to the display's BAT corner, and a 3 mm path from the roller to the button board, must be clear of every solid.
   - Test: the `wire bundle` components in `fit_check_v5.py` (Task 6).

---

## File Structure

| File | Responsibility |
|---|---|
| `case/v5/params.scad` | Every number and derived value; `assert`s on the stack. Nothing renders. |
| `case/v5/profile.scad` | `base2d`, `plan(i)`, `e_in(z)`, `envelope()`, `head_xf()`, `ycut()`. The outer form only. |
| `case/v5/collar.scad` | `collar()`, `wheel()`, `cradle()`. |
| `case/v5/head_half.scad` | `head_body()`, `head_panel()`. |
| `case/v5/key_half.scad` | `key_body()`, `key_panel()`. |
| `case/v5/keys.scad` | `round_cap()`, `ok_cap()`, `ring_cap(i)`, `rocker(pair)`, `dpad_ring()`. Cap modules copied from v4 with their comments. |
| `case/v5/dock.scad` | `magnet_plate()`, `dock()`. |
| `case/v5/umote_v5.scad` | `part=` dispatch: print-oriented parts, `asm_*` copies, coupons, `params` JSON echo. |
| `case/v5/export.sh` | Renders every part into `case/stl_v5/`, writes `case/stl_v5/params.json`. |
| `case/check_v5.py` | `check_part(path, bed=180) -> list[str]` (problems). The CLI exits 1 on any problem. |
| `case/fit_check_v5.py` | Component solids from `params.json`; collisions, insertion sweeps, wire paths, roller and rocker states. Exits 1 on any collision. |
| `case/tests/test_check_v5.py`, `case/tests/test_fit_v5.py` | pytest for the two scripts and the Review Focus tests. |
| `case/viewer/build_viewer.py` | Gains a `--v5` mode reading `case/stl_v5/`. |
| `firmware/logic.h`, `firmware/test/test_logic.cpp`, `firmware/remote.yaml` | Roller decode and routing. |

The test runner is `python3 -m pytest case/tests -q` (install once: `python3 -m pip install pytest`).

---

### Task 1: Parameters, profile, and the print checker

**Files:**
- Create: `case/v5/params.scad`, `case/v5/profile.scad`, `case/v5/umote_v5.scad`, `case/v5/export.sh`, `case/check_v5.py`, `case/tests/test_check_v5.py`

**Interfaces:**
- Produces:
  - **`params.scad` names** used by every later task. These are the v4 names where they exist, plus:
    - `W=51 wall=2.0 T=15.8 theta=8 board_gap=18 usb_x=0.22`
    - `ea=3 eb=7 bed_ch=0.57 roll_z=10.8 roll=2.2 land=1.4 pan_t=1.6 pcl=0.15`
    - `batt=[46,105,5]`, `batt_y0` (= collar key end + key tongue + 0.5)
    - `y_head_end`, `y_key_start`, `whl_d=16 whl_proud=1.2`
    - `ec11=[11.7,12,6.5]` [CHECK], `ec11_shaft_d=6` [CHECK], `ec11_detent_steps=4` [CHECK]
    - `snap_uc=0.6` (set from the coupon in Task 3)
  - **`profile.scad`:** `e_in(z)` returns the plan inset at height z; `plan(i)`; `envelope()`; `head_xf()` rotates children by `-theta` about `[x, y_head_end, T]`; `ycut(y0, y1)`.
  - **`check_v5.py`:**
    - `check_part(path: str, bed: float = 180, max_bridge: float = 17, allow_bodies: bool = False) -> list[str]`, which checks watertight, `body_count == 1`, the overhang area above layer 1 and the bed footprint (longest x/y extent).
    - `bridge_spans(mesh) -> list[float]`: the longest horizontal extent of each connected flat downward face patch.

- [ ] **Step 1: Write the failing tests** in `case/tests/test_check_v5.py`, using trimesh primitives:

```python
def test_box_passes(): assert check_part(save(box(50, 20, 10))) == []
def test_too_long_for_bed(): assert any("bed" in p for p in check_part(save(box(190, 20, 10))))
def test_two_bodies(): assert any("bodies" in p for p in check_part(save(two_boxes())))
def test_overhang_found(): assert any("overhang" in p for p in check_part(save(t_shape(arm=10))))   # 10 mm flat arm above z 5
def test_bridge_span(): assert max(bridge_spans(bridge(span=20))) == pytest.approx(20, abs=0.5)
```

- [ ] **Step 2: Run `python3 -m pytest case/tests/test_check_v5.py -q`.** Expected: FAIL (`check_v5` not found).

- [ ] **Step 3: Implement `check_part` and `bridge_spans`.**
  - Base the overhang and bridge logic on `case/check_print.py`: face normal z < -0.7072, above `min z + 0.15`.
  - Count flat downward patches (normal z < -0.999) as bridges, not overhangs, and fail only if a span exceeds `max_bridge`.
  - The CLI is `python3 case/check_v5.py case/stl_v5/*.stl`. It prints one line per part and exits 1 on any problem.

- [ ] **Step 4: Run the tests.** Expected: 5 passed.

- [ ] **Step 5: Write `params.scad` and `profile.scad`.**
  - Copy `e_in`, `plan`, `envelope` and `head_xf` from `concept_n9.scad` / `concept_d.scad`, renamed to the names above.
  - Derived values come from the v4 formulas with `board_gap=18`.
  - Asserts in `params.scad`:
    - `W/2 - wall - batt[0]/2 >= 0.3` (battery side clearance);
    - `bb_y0 - (db_y0+db_l) == board_gap`;
    - `whl_d/2 + 0.4 <= min(bb_y0 - cy, cy - (db_y0+db_l))`, where `cy` is the wheel axle's y (the wheel clears both board ends);
    - `batt_y0 + batt[1] <= bb_y0 + bb_l` (battery under the board);
    - `L <= 219`.

- [ ] **Step 6: Write `umote_v5.scad`.**
  - It includes the files and dispatches `part`.
  - For now: `envelope` (straight + bent) and `params`.
  - `params` must `echo(str("PARAMS ", <JSON object of every param>))`.

- [ ] **Step 7: Write `export.sh`.**
  - It loops over a `PARTS` list, runs `openscad -o case/stl_v5/$p.stl -D "part=\"$p\""`, and fails on any `WARNING:` or `ERROR` in the log.
  - It extracts the `PARAMS` echo into `case/stl_v5/params.json`.

- [ ] **Step 8: Run `bash case/v5/export.sh envelope params`.**
  - Expected: `case/stl_v5/envelope.stl` and `params.json` exist.
  - `python3 -c "import json;p=json.load(open('case/stl_v5/params.json'));print(p['W'],round(p['L'],1))"` prints `51 218.0` (± 0.1).

- [ ] **Step 9: Commit**: `git add case/v5 case/check_v5.py case/tests && git commit -m "feat(case-v5): params, profile, print checker"`.

### Task 2: Test coupons, exported and uploaded

**Files:**
- Modify: `case/v5/umote_v5.scad` (parts `snap_test`, `roller_test`), `case/v5/collar.scad` (first cut of `collar()`, `wheel()`, `cradle()`), `case/v5/head_half.scad` (`snap()` module)

**Interfaces:**
- Consumes: Task 1 names.
- Produces:
  - `snap(uc)`: one cantilever snap. Beam 9 mm long, 1.2 → 0.8 mm thick, undercut `uc`, PETG.
  - `catch()`: its matching ledge in the head body.
  - `collar()`, `wheel()`, `cradle()`: Task 5 finishes them.

- [ ] **Step 1: Get the EC11 measurements.**
  - Ask the user for caliper readings of their EC11: body width × height × depth, shaft diameter and flat or knurl, shaft length, and detents per turn.
  - Write them into `ec11*` in `params.scad`, replacing the [CHECK] defaults.

- [ ] **Step 2: Model `snap_test`.**
  - A 30 mm slice of the head tip end in print orientation: head body corner with `catch()`, plus a head-panel corner with three `snap(uc)` at uc = 0.4 / 0.6 / 0.8.
  - Engraved 1 / 2 / 3 dots on the inside mark them.
  - The tip seam is the real 0.15 mm gap.

- [ ] **Step 3: Model `roller_test`.**
  - A collar slice: floor, the 16 mm `wheel()` on an EC11 dummy bore, `cradle()` hinged at one end, and a pocket for a 6×6 tact switch beside the encoder.
  - The collar top skin sits over the encoder, with the slot for the wheel.

- [ ] **Step 4: Export the coupons** with `bash case/v5/export.sh snap_test roller_test`, then run `python3 case/check_v5.py case/stl_v5/snap_test.stl case/stl_v5/roller_test.stl`. Expected: both report no problems, exit 0.

- [ ] **Step 5: Upload.**
  - Copy both STLs into `release/`, then run `bash release/upload_to_copyparty.sh`.
  - Expected: `201` (or `200`) for `snap_test.stl` and `roller_test.stl`, and both appear in the final listing.

- [ ] **Step 6: Commit** the source and `release/*_test.stl`: `git commit -m "feat(case-v5): snap and roller coupons"`.

### Task 3: Coupon results (user gate)

- [ ] **Step 1: Ask the user to print both coupons and report:**
  - which snap holds firmly and releases with a card in the tip seam without whitening;
  - whether the roller turns freely, clicks the tact switch with a light press, and does not click under its own weight.
- [ ] **Step 2: Set the parameters from the report.** Set `snap_uc` to the chosen value. Adjust `cradle` gap and hinge thickness and `whl_proud` within the fallback order in Global Constraints. Re-export and re-upload the changed coupon, and repeat until the user is satisfied.
- [ ] **Step 3: Commit**: `git commit -m "fix(case-v5): coupon-tuned snap and cradle"`.

### Task 4: Head half

**Files:**
- Modify: `case/v5/head_half.scad`, `case/v5/umote_v5.scad` (parts `head_body`, `head_panel`, `asm_head_body`, `asm_head_panel`)
- Test: `case/tests/test_fit_v5.py` (created here, run against the export)

**Interfaces:**
- Consumes: `snap(uc)`, `catch()`, `collar()` fork positions (`fork_y = 72.83`, `fork_x = ±17.45`: the display antenna-end holes).
- Produces: `head_body()` and `head_panel()` in model coordinates (straight); the `asm_*` parts apply `head_xf()`.

- [ ] **Step 1: Write the failing tests** in `case/tests/test_fit_v5.py` (they load `case/stl_v5/*.stl` and `params.json`):

```python
def test_head_parts_print_clean():
    for p in ["head_body", "head_panel"]: assert check_part(f"{STL}/{p}.stl") == []
def test_usb_notch_centre(): assert notch_centre_x("head_body") == pytest.approx(0.22, abs=0.05)
def test_ir_clips_tilted(): assert ir_axis_angle("head_body") == pytest.approx(-8, abs=0.5)    # degrees about x, down
```

Helpers `notch_centre_x(part)` and `ir_axis_angle(part)` live in the test file and slice the mesh: the notch at y = 0.5, the clip bores by fitting a line through their centres.

- [ ] **Step 2: Run `python3 -m pytest case/tests/test_fit_v5.py -q`.** Expected: FAIL (no STL).

- [ ] **Step 3: Implement `head_body()`.**
  - The envelope cut at `y_head_end`, hollowed, with the v4 USB-C notch (floor skin, receptacle hole) at `usb_x`.
  - IR clips and pockets from v4, rotated +8° about x so the beam is level when the key half is level.
  - The IR wire groove.
  - Two M2.5 insert posts under the display's USB-end holes.
  - The 4 `catch()` ledges at the tip.
  - An end wall that seats on the collar fork.

- [ ] **Step 4: Implement `head_panel()`.**
  - `stack(pz0, T, …, land+pcl)` with the v4 screen window and bezel chamfer, a hook lip at the collar end, and 4 `snap(snap_uc)` at the tip.
  - Printed face down: no feature on the face side.

- [ ] **Step 5: Export and run the tests.** Run `bash case/v5/export.sh head_body head_panel asm_head_body asm_head_panel && python3 -m pytest case/tests -q`. Expected: all pass.

- [ ] **Step 6: Commit**: `git commit -m "feat(case-v5): head body and panel"`.

### Task 5: Collar, roller and cradle (final)

**Files:**
- Modify: `case/v5/collar.scad`, `case/v5/umote_v5.scad` (parts `collar`, `wheel`, `cradle`, `asm_collar`, `asm_wheel`, `asm_cradle`, `asm_cradle_pressed`)
- Test: `case/tests/test_fit_v5.py`

**Interfaces:**
- Consumes: `ec11*`, `whl_*`, cradle values from Task 3; `head_xf()`.
- Produces:
  - `collar()` in assembled coordinates: the hull between the head end profile (through `head_xf`) and the key start profile.
  - The head **fork**: plate plus 2 standoffs from the head floor to `db_z0`, Ø5.2, under the antenna-end holes.
  - The key **tongue**: 7 mm on the key floor, 2 M2.5 insert holes.
  - Hook lips for both panels.
  - A wire channel ≥ 4 mm Ø beside the roller.
  - `cradle_travel = 0.3`.

- [ ] **Step 1: Write the failing tests:**

```python
def test_collar_prints_clean(): assert check_part(f"{STL}/collar.stl") == []      # printed on its side
def test_roller_not_pressed_at_rest():          # Review Focus 1
    assert gap(f"{STL}/asm_cradle.stl", "tact_actuator") >= 0.3
def test_roller_presses_when_pushed():
    assert gap(f"{STL}/asm_cradle_pressed.stl", "tact_actuator") <= 0.0
def test_wheel_proud(): assert wheel_top_z() - P["T"] == pytest.approx(P["whl_proud"], abs=0.05)
def test_encoder_off_centre(): assert abs(encoder_centre_x()) >= 9
```

`tact_actuator` is a 3.5 mm Ø × 0.4 mm disc at the 6×6 switch's plunger top, built in the test from `params.json`. `gap()` returns the minimum distance from the mesh to it.

- [ ] **Step 2: Run the tests.** Expected: FAIL.

- [ ] **Step 3: Finish `collar()`, `wheel()` and `cradle()`** to satisfy the tests and the spec section 5 table (print orientation on its side, slot bridge ≤ 17 mm). Apply the fallback order only if the stack assert in `params.scad` fails.

- [ ] **Step 4: Export the collar parts and run `python3 -m pytest case/tests -q`.** Expected: all pass.

- [ ] **Step 5: Commit**: `git commit -m "feat(case-v5): collar, roller and cradle"`.

### Task 6: Key half and the full fit check

**Files:**
- Modify: `case/v5/key_half.scad`, `case/v5/umote_v5.scad` (parts `key_body`, `key_panel`, `asm_key_body`, `asm_key_panel`)
- Create: `case/fit_check_v5.py`

**Interfaces:**
- Consumes: the collar tongue holes and lip; v4 cap-collar modules (copied into `key_half.scad`).
- Produces:
  - `fit_check_v5.py [stl_dir] [grow]`, which exits 1 on any undesigned collision.
  - Its component names are reused by Tasks 7–9: `display PCB`, `LCD + touch glass`, `display back parts`, `USB-C receptacle`, `USB-C plug overmold`, `USB-C plug metal`, `IR LED L/R`, `button PCB`, `copper-side SMDs`, `switch *`, `stem *`, `MCP23017 DIP-28`, `Q1 TO-92`, `INMP441 module`, `battery 46x105`, `EC11`, `tact 6x6`, `wire bundle BAT`, `wire bundle roller`, `insert *`, `magnet *`, `pogo pad *`.

- [ ] **Step 1: Write `fit_check_v5.py`.**
  - Port `fit_check.py`: same `box`/`rbox`/`cyl` helpers, `report()`, skip list and insertion sweeps.
  - Read every value from `params.json`. Head components go through the same 8° transform as `head_xf()`.
  - Add the new components listed in Produces.
  - Sweep paths follow section 5's order: each part drops along −z of its own half.
  - Wire bundles:
    - `BAT`: a 4 mm Ø polyline from (battery tip-end corner, z 4) through the collar channel to the display BAT corner;
    - `roller`: 3 mm Ø from the EC11 pins to the MCP pins 2 and 6.

- [ ] **Step 2: Run `python3 case/fit_check_v5.py case/stl_v5 0.15`.** Expected: collisions reported for the key half (`battery`, `button PCB` and others against the missing parts), confirming the check sees them.

- [ ] **Step 3: Implement `key_body()`.**
  - Envelope from `y_key_start` to L, hollowed: vertical inner wall below `roll_z`, following the roll above it.
  - Battery floor with a 0.5 mm foam allowance at `batt_y0`.
  - Two M2.5 insert bosses at the bottom end, outside the battery, at x such that the pads and magnets fit.
  - Two flush M3 brass-insert pad holes in the bottom end face, ≥ 6 mm apart.
  - Four magnet pockets outside the battery footprint.
  - Strap-eyelet boss and slot in a bottom corner.
  - Magnet-plate recess 1.2 mm deep over the screw bosses.
  - Insert holes for the collar tongue.

- [ ] **Step 4: Implement `key_panel()`.**
  - v4 cap holes, cap flange collars and key notches at the v4 positions shifted by the new `bb_y0`.
  - D-pad opening plus the `dpad_ring` pocket.
  - Capsule holes for both rockers.
  - Mic grille.
  - Two 0.5 mm island wells (nav: hull of the D-pad circle r 20.2 and the BACK/VOICE caps; media: offset 2.2 round both rocker capsules).
  - Button-board posts or clips registering the board to the panel.
  - Two screw bosses over the body bosses.
  - Hook lip under the collar.

- [ ] **Step 5: Export everything so far and run the fit check.** Run `bash case/v5/export.sh key_body key_panel asm_key_body asm_key_panel && python3 case/fit_check_v5.py case/stl_v5 0.15`. Expected: `RESULT: no collisions` (only skip-listed designed contacts remain).

- [ ] **Step 6: Add the fit check to pytest.** Add `test_fit_check_clean` to `test_fit_v5.py`: it runs `fit_check_v5.main([...])` and asserts 0 collisions. This includes the `USB-C plug overmold` and both wire bundles (Review Focus 2 and 5). Run `python3 -m pytest case/tests -q`. Expected: all pass.

- [ ] **Step 7: Commit**: `git commit -m "feat(case-v5): key half and fit check"`.

### Task 7: Head panel release

**Files:**
- Test: `case/tests/test_fit_v5.py`
- Modify: `case/v5/head_half.scad` (only if the test fails)

**Interfaces:**
- Consumes: `asm_head_panel`, `asm_head_body`.

- [ ] **Step 1: Write the test.**

```python
def test_card_reaches_snaps():   # Review Focus 3
    card = card_path(thickness=0.4, depth=8)   # slab entering the tip seam along +y, at the seam's z
    assert all(touches(card, hook) for hook in snap_hook_faces("asm_head_panel"))
    assert not collides(card, "asm_head_body", allow=snap_hook_faces("asm_head_panel"))
```

- [ ] **Step 2: Run the test.** Expected: PASS, or FAIL pointing at a snap the card can't reach.

- [ ] **Step 3: If it fails,** move the snap hooks or add a 0.4 mm lead-in inside the seam (not visible from outside), re-export, and re-run until it passes.

- [ ] **Step 4: Commit**: `git commit -m "test(case-v5): head panel opens with a card"`.

### Task 8: Keys

**Files:**
- Modify: `case/v5/keys.scad`, `case/v5/umote_v5.scad` (parts `caps`, `caps_asm`, `caps_asm_pressed`, `caps_asm_rocker_tilt`)

**Interfaces:**
- Consumes: the key panel hole and collar positions; v4 `round_cap`, `ring_cap`, `ok_cap`, `ef_flange`, `bore`, `mark`.
- Produces:
  - `rocker(pair)`: a capsule cap over two switches 13 mm apart, with a saddle top, a centre fulcrum rib bearing on the panel underside, and two hex bores at the switch positions.
  - `ok_cap()`: gains a 1.6 mm dome nub.
  - `dpad_ring()`: standing 0.5 mm proud, flange inside.

- [ ] **Step 1: Write the failing test.**

```python
def test_rocker_one_end_only():   # Review Focus 4
    m = load("caps_asm_rocker_tilt")   # VOL rocker rotated about its fulcrum until the VOL+ end has moved 0.3 mm
    assert stem_travel(m, "VOL+") >= 0.25 and stem_travel(m, "VOL-") <= 0.05
def test_caps_print_clean(): assert check_part(f"{STL}/caps.stl", allow_bodies=True) == []
```

The caps plate has many bodies, hence `allow_bodies=True` (defined in Task 1).

- [ ] **Step 2: Run the tests.** Expected: FAIL.

- [ ] **Step 3: Implement `rocker`, `ok_cap` (nub) and `dpad_ring`.** Keep the v4 hex-bore grip (`grip_af = 3.4`) and the fit values confirmed on v4.

- [ ] **Step 4: Export the caps parts and run the fit check and the tests.** Run `bash case/v5/export.sh caps caps_asm caps_asm_pressed caps_asm_rocker_tilt && python3 case/fit_check_v5.py case/stl_v5 0.15 && python3 -m pytest case/tests -q`. Expected: no collisions; all tests pass.

- [ ] **Step 5: Commit**: `git commit -m "feat(case-v5): rockers, OK nub, raised D-pad ring"`.

### Task 9: Magnet plate and dock

**Files:**
- Modify: `case/v5/dock.scad`, `case/v5/umote_v5.scad` (parts `magnet_plate`, `dock`, `asm_magnet_plate`, `asm_dock`)

**Interfaces:**
- Consumes: the key-body magnet pockets, pad positions and recess.
- Produces:
  - `magnet_plate()`: flush in the recess, held by magnets, covers both screws.
  - `dock()`: a cradle holding the remote on its bottom end with the screen toward the user.
    - Two P75-B1 holes, 1.0 mm press-fit [CHECK], whose plungers meet the pads with 0.6–0.9 mm of travel.
    - Dock magnets opposite the remote's.
    - A USB-C breakout pocket.

- [ ] **Step 1: Write the failing test.**

```python
def test_dock_parts_print_clean():
    for p in ["magnet_plate", "dock"]: assert check_part(f"{STL}/{p}.stl") == []
def test_pogo_travel():
    assert 0.6 <= pogo_compression() <= 0.9      # P75 tip z in asm_dock vs the pad face
def test_plate_flush(): assert abs(plate_offset()) <= 0.1
```

- [ ] **Step 2: Run the tests.** Expected: FAIL.

- [ ] **Step 3: Implement both parts**, add them to the fit check (`pogo pad *`, `magnet *`), and export.

- [ ] **Step 4: Run `python3 case/fit_check_v5.py case/stl_v5 0.15 && python3 -m pytest case/tests -q`.** Expected: no collisions, all pass.

- [ ] **Step 5: Commit**: `git commit -m "feat(case-v5): magnet plate and charging dock"`.

### Task 10: Firmware roller support

**Files:**
- Modify: `firmware/logic.h`, `firmware/test/test_logic.cpp`, `firmware/remote.yaml`

**Interfaces:**
- Produces:
  - `Key::ROLL_UP` and `Key::ROLL_DOWN`.
  - `struct RollDecoder { int8_t acc = 0; uint8_t last = 0; int steps_per_detent = 4; int feed(uint8_t ab); }`. It takes the new 2-bit A/B state (A = bit 1) and returns +1, −1 or 0 per completed detent. Invalid transitions are ignored.
  - `press` codes 17 = ROLL_UP, 18 = ROLL_DOWN.

- [ ] **Step 1: Write the failing tests** in `test_logic.cpp`:

```cpp
static void roll_decoder_counts_detents() {
  RollDecoder d; int s = 0;
  for (uint8_t ab : {1, 3, 2, 0}) s += d.feed(ab);        // one CW detent (4 quarter steps)
  assert(s == 1);
  for (uint8_t ab : {2, 3, 1, 0}) s += d.feed(ab);        // one CCW detent
  assert(s == 0);
  assert(d.feed(3) == 0);                                 // 0 -> 3 skips a state: ignored
}
static void roll_routes_by_page() {
  assert(is(route(Page::TV, Key::ROLL_UP, false, false), Target::SOUNDBAR_IR, "VOL_UP"));
  assert(is(route(Page::TV, Key::ROLL_UP, true, false), Target::TV_KEY, "VOLUME_UP"));
  assert(is(route(Page::SOUNDBAR, Key::ROLL_DOWN, false, false), Target::SOUNDBAR_IR, "VOL_DOWN"));
  assert(is(route(Page::HOME, Key::ROLL_DOWN, false, false), Target::PAGE_SCROLL, "DOWN"));
  assert(is(route(Page::SETTINGS, Key::ROLL_UP, false, false), Target::LIST_MOVE, "UP"));
}
```

Call both from `main`.

- [ ] **Step 2: Run `g++ -std=c++17 -Wall -Werror firmware/test/test_logic.cpp -o /tmp/tl && /tmp/tl`.** Expected: compile error (no `RollDecoder`).

- [ ] **Step 3: Implement the decoder and the routing.**
  - `RollDecoder::feed` uses the standard 16-entry quadrature table.
  - In `route()`, map ROLL_UP / ROLL_DOWN to VOL_UP / VOL_DOWN behaviour on the TV and SOUNDBAR pages, to `PAGE_SCROLL` on HOME and to `LIST_MOVE` on SETTINGS.

- [ ] **Step 4: Re-run.** Expected: the test binary exits 0.

- [ ] **Step 5: Wire it in `remote.yaml`.**
  - Add two `gpio` binary sensors on `mcp` pins 9 and 13 (GPB1, GPB5): input, pullup, `interrupt: CHANGE`, with the same `g_board_ok` filter and no `delayed_on`.
  - Both `on_state` handlers call one script, `roll`. It feeds `(A<<1)|B` into a global `RollDecoder` and runs `press` with k 17 or 18.
  - Add `{17, Key::ROLL_UP}, {18, Key::ROLL_DOWN}` to the `KEYS` map.

- [ ] **Step 6: Validate and compile.**
  - Run `uvx esphome==2026.10.1 config firmware/remote.yaml`, then `uvx esphome==2026.10.1 compile firmware/remote.yaml`.
  - Expected: config valid; compile succeeds. Record the flash %: it must not rise more than 0.3 points over the last build, given the 85 % target issue.

- [ ] **Step 7: Commit**: `git commit -m "feat(firmware): crease roller on MCP GPB1/GPB5"`.

### Task 11: Viewer, release, handoff

**Files:**
- Modify:
  - `case/viewer/build_viewer.py` (`--v5`)
  - `case/v5/export.sh` (`all`)
  - `release/upload_to_copyparty.sh`: takes an optional directory argument (default: its own folder), uses `shopt -s nullglob` so a folder without `.zip`/`.png` files doesn't fail, and keeps the `URL` override
  - `HANDOFF.md`
- Create: `release/v5/` (STLs plus `viewer.html`)

- [ ] **Step 1: Export and check everything.** Run `bash case/v5/export.sh all && python3 case/check_v5.py case/stl_v5/[!a]*.stl && python3 case/fit_check_v5.py case/stl_v5 0.15 && python3 -m pytest case/tests -q`. Expected: every print part reports no problems, `RESULT: no collisions`, all tests pass.

- [ ] **Step 2: Build the v5 viewer.**
  - Add `--v5` to `build_viewer.py`: an assembled view of the `asm_*` parts, plus a download list of the print parts with their orientation notes.
  - Run `python3 case/viewer/build_viewer.py --v5`.
  - Expected: `case/stl_v5/viewer.html` opens and shows the assembly (check with Playwright: no console errors, screenshot reviewed).

- [ ] **Step 3: Upload the release.**
  - Copy the print parts and `viewer.html` to `release/v5/`.
  - Upload with `URL=http://192.168.31.9:3923/stl/v5/ bash release/upload_to_copyparty.sh release/v5`.
  - Expected: one `2xx` per file, and they appear in the listing.

- [ ] **Step 4: Update `HANDOFF.md`.** Add a v5 section with:
  - part list and print orientations;
  - assembly order;
  - the hardware checks still open:
    - USB-C square at `usb_x` 0.22;
    - IR range with the 8° tilt;
    - RSSI with and without the encoder;
    - dock charges, pads dead when undocked, a coin across the pads does nothing;
  - the Schottky wiring point.

- [ ] **Step 5: Commit**: `git add case release/v5 HANDOFF.md && git commit -m "release(case-v5): parts, viewer, handoff"`.
