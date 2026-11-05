# umote case v6: structural rework of v5

Date: 2026-11-05. Status: design, decisions taken with the user in conversation, pending review of this document.
Builds on: `2026-11-05-remote-case-v5-design.md` (form, layout, keys, dock, USB-C, IR stay as there unless changed here).
Code: new `case/v6/`, started as a copy of `case/v5/`. v5 stays as the record of what failed.

## 1. Why v6: what the v5.1 print showed

The user printed v5.1 in full. It passed 38 clash/fit tests and failed in the hand. Every failure traces to the geometry, none to the printer:

| # | Seen on the print | Cause in v5 |
|---|---|---|
| F1 | Key half bends when held | battery door window 46.6 + 2 × 0.15 in a 47.0 cavity: 0.05 mm of back left per side over ~106 mm; the key body is a floorless U-channel |
| F2 | Collar joints shaky, visible gaps/steps at both seams | butt joints; 4 mm prongs + M2 and 1.2 mm tongues only; nothing overlaps or aligns |
| F3 | Collar top flimsy | wheel window 16.8 long in a 17.6 collar: 0.4 mm left each end; top skin 0.8 |
| F4 | Hole through the collar back | 0.4 mm back skin under the wheel (two layers) |
| F5 | Wheel mount too thin; EC11 cannot fit | 1.0 mm rocking cradle; EC11 modelled as a plain box, with no bushing, shaft, pins or tabs; the real M7 bushing runs into the wheel |
| F6 | Key panel pulls out of its seat when keys are pressed | 4 snaps, all at the bottom end, 0.4 undercut with 45° retention faces (designed to pry open) |
| F7 | Holes in the tip end above the screen | head snap catches cut through the rolled tip wall |
| F8 | Openings in the bottom end | dock magnet pockets break through the rolled edge |
| F9 | Chipped corners at the key body / collar joint | slivers left beside the door window |
| F10 | Keys rub slightly | 0.45 per side round caps and D-pad, no lead-in |

**Root cause of F3–F5:** with the wheel on the encoder shaft, skin over the encoder = wheel radius − wheel proud − half the EC11 body (8 − 1.1 − 6 ≈ 0.8). With 2 mm skins and a closed back the wheel zone needs ~18.8 mm of thickness; v5 squeezed it into 15.8.

**Process cause:** the tests only checked collisions. v6 adds structural checks (section 7) and test pieces before any full print.

## 2. Decisions (user, 2026-11-05)

1. **Solid back.** No battery door. The key-half back is a full floor; the battery goes in from the front (unscrew the key panel, lift the button board).
2. **EC11 on a small carrier perfboard**, bushing through a printed bulkhead with its nut.
3. **No wheel press.** The rocking cradle and its tact switch go; OK does select. (v5 goal 3 "press to select" is dropped. The tact was wired in parallel with OK, so firmware is unchanged.)
4. **Key panel held by M2 screws from the back into brass inserts, plus a perimeter lip.**
5. **Back ridge at the wheel:** only the crease zone grows to ~19 mm, as a ridge on the back. Face stays flat, rest stays 15.8. (v5 struck finger rest [19]; this ridge is functional and the user chose it.)
6. **Two bodies joined by a long overlapping sleeve** (220 mm bed: 218 mm one-piece only fits diagonally and the bend lifts the head). The collar becomes a wheel housing that carries no load.
7. Bed is **220 mm**; parts may now be up to 210 mm in their longest bed dimension.

## 3. Structural rules (apply to every part)

- Walls ≥ **2.4 mm** (6 lines at 0.4); back and face panels ≥ **2.0 mm**.
- No cut-out or pocket leaves less than **3.0 mm** of material beside it (lands, slivers).
- Every pocket keeps ≥ **1.2 mm** to the outer surface, measured on the rolled/curved surface, not the nominal wall.
- No butt joints between load-carrying parts: overlap ≥ 8 mm, or a lip ≥ 1.6 mm tall.
- Bought parts are modelled with every feature they have (bushing, shaft, pins, tabs, nut).
- Retention faces that must hold under use are 90°; 45° faces only where a part is meant to pry off.

The 2.4 mm walls cost 0.8 mm of inner width (47.0 → 46.2). The battery is 46.0: 0.1 a side is too tight, so **W grows 51 → 52** (inner 47.2, 0.6 a side). [CHECK in the plan: the face layout, which was centred, is unaffected; the dock pocket grows with W.]

## 4. The wheel zone

### 4.1 EC11 (Alps EC11E, 20 mm flat shaft with switch; datasheet page "EC11 Series")
- body 11.7 × 12.0 footprint, 4.5 from the PCB seat to the frame top; terminals 3.5 below the seat
- bushing M7 × 0.75, 7 long from the frame top; shaft Ø6, 20 from the frame top, flat 10 long leaving 4.5
- holes: A C B at 2.5 pitch, D E 5 apart, the two rows 14.5 apart (7 and 7.5 from centre); tab slots 12.5 apart, 2.6 × 1.5
- nut: not on the drawing. Measured on the test piece [CHECK]; modelled as M7 thin nut 10 AF × 2.0 until then.
- The user's part is a clone: body and nut confirmed on the encoder test piece before the full print.

### 4.2 Layout
- Shaft along x, as v5. Turn the encoder so both pin rows run along **y**: the carrier board then only needs ~10 mm of z (holes span ±2.5 z). The side tabs are snipped (they would need ±7 mm of z).
- Carrier: 1.6 mm perfboard ~20 (y) × 10 (z), perpendicular to the shaft, screwed with 2 × M2 to posts on the collar floor; wires leave from its back.
- Bulkhead: 2.5 mm printed wall in the collar, M7 clearance hole 7.3, the nut on the wheel side. The bushing carries the encoder; the board stops it rotating and carries the wires.
- Wheel: Ø18, 9 wide, on the outer 10 mm of the shaft (the flat), D-bore, grub-free press fit [CHECK on the test piece], 1.2 proud of the face.
- Heights (z from the ridge's back): back 2.0, wheel bottom ≥ back + 0.6, EC11 skin over the body ≥ 2.0 → wheel zone thickness ~19.4; ridge depth ~3.6 below the 15.8 back. Exact numbers come out of params with asserts.

### 4.3 Collar
- A wheel housing only: top, bulkhead, carrier posts, ridge. It sits in a pocket formed by the two bodies' sleeve (4.4), held by 2 M2.
- Wheel window leaves ≥ 3 mm of top at both ends and both sides.
- Back of the collar ≥ 2.0 everywhere; no thinning pocket (the cradle is gone).

## 5. Joints and panels

### 5.1 Body joint (head ↔ key)
- The key body carries a **sleeve** that runs ≥ 10 mm into the head body, inside its walls, 0.15 clearance, on all three sides (back + both side walls), past the collar zone. The head's wall ends step down so the outer surface stays continuous: a lap joint, not a butt.
- 4 × M2 from the back through the sleeve into heat-set inserts in the head (M2 × 3 inserts) [CHECK insert stock; else self-tap 1.7 holes ≥ 6 deep].
- The 8° bend lives in the head body; the sleeve is straight in key coordinates and the head's socket is cut with `head_xf()`.
- The seam reads as a deliberate 0.8 V line (v5 goal 8), now on overlapping parts.

### 5.2 Key panel
- 6 × M2 from the back into M2 heat-set inserts in bosses under the panel, spread along its length (2 near the collar, 2 mid, 2 bottom). Positions chosen clear of switches, the battery and board, which get matching clearance notches or holes. [Plan: pick the sites from the board layout.]
- Perimeter lip: the panel's edge drops 1.6 into a 1.6 rebate in the body wall (research report recipe), so presses load the wall, not the screws.
- The v5 snaps and board clips go. The board is held between panel bosses and floor standoffs.

### 5.3 Head panel
- Same treatment: lip all round + 4 × M2 from the back. The tip snaps go (F7).

## 6. Other fixes

- **Dock magnets (F8):** pockets moved down/in so ≥ 1.2 mm remains to the rolled surface; the check in section 7 enforces it.
- **Key fit (F10):** caps, rockers and D-pad 0.6 per side (was 0.45), 0.4 × 45° lead-in at the top of each hole. The rib notch keeps its 0.25.
- **Battery from the front:** the battery bay is a 0.6-a-side pocket in the solid floor with a 4 mm thumb notch at one end to lift it; foam stays.
- Back screws: 4 (joint) + 6 (key panel) + 4 (head panel) + 2 (collar) = 16 M2 heads on the back, in counterbores. This revises v5 goal 8 "no visible screws": screws are allowed on the back only.

## 7. Verification

New checks in `case/tests/`, run on every part before export; a part that fails isn't exported:
1. **Wall thickness:** sample the mesh (ray-cast inward from surface points) → no point under 2.4 on walls / 2.0 on panels, except named, documented features (key holes, window bezel chamfers).
2. **Lands:** every cut leaves ≥ 3.0 around it.
3. **Breakthrough:** every pocket ≥ 1.2 to the outer surface.
4. **Real parts:** the EC11 model (with bushing, shaft, flat, pins, nut) and the carrier board are in the fit check; zero collisions, and the wheel turns clear (swept volume).
5. Existing checks stay: clash/fit, print orientation, no supports, bed ≤ 210 mm.

**Test pieces, printed and confirmed by the user before the full print:**
- T1 wheel zone: collar + a short stub of both bodies with the sleeve joint. Confirms EC11 body/nut, wheel press fit, joint stiffness.
- T2 key panel corner: a 40 mm slice of key body + panel with 2 screw sites and the lip. Confirms the lip, insert holes, key fit 0.6.
- T3 bottom end: the last 20 mm of the key body. Confirms the magnet and pad pockets.

Release: `/stl/v6.0/` on copyparty, full set, SHA-checked (as v5).

## 8. Open items for the plan

- Insert stock (M2 heat-set) and screw lengths.
- EC11 nut, wheel press fit: from T1.
- Firmware: no change (the press tact was in parallel with OK; the encoder stays on MCP GPB1/GPB5).
- Viewer rebuilt for v6.
