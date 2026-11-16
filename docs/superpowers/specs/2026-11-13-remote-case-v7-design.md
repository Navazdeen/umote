# umote case v7 "Keel": straight body, one front shell, two flat back plates

Date: 2026-11-13. Status: built and released as v7.0 (`release/v7.0/`, copyparty `/stl/v7.0/`). The user chose the shape from three mockups (`.superpowers/brainstorm/…/form-concepts.html`, option A) and said "go ahead and build, no questions", so everything below except the shape is the builder's call.
Code: `case/v7/`. v6 (`case/v6/`) stays as the record of what failed.

## 1. Why v7: what the v6.1 print showed (user, 2026-11-13)

| Seen on the print | Cause in v6 |
|---|---|
| The display half stops short of the key half; a gap stays at the seam | the two tenons had 0.15 mm a side in their slots and entered at the 8° bend; a printed sliding fit needs 0.2 to 0.3, and the squashed first layer alone is more than 0.15 |
| Screw holes too small where the display half meets the wheel housing | every M2 pilot was drawn 1.7 as a 24-gon; small printed holes come out 0.1 to 0.2 under, so about 1.5 |
| "The bending part is not clear" | the bend made every joint face lean; the user asked to scrap the bend and find a new form |
| Found while building v7: the key panel was a mirror image | face-down parts were exported with `mirror([0,0,1])`, not a flip. POWER's hole landed on the mic's side |

## 2. The form

- Straight. The face is one flat plane, 52 × 225.4 mm.
- The back is a shallow V (the keel): 15.6 mm thick at the tip, 20.5 at the keel line, 16.6 at the bottom end. The keel line is at `y_ap` = the key-side wall of the wheel zone (y 101.5), so the depth the wheel needs (Ø18.6 wheel + 2.0 skin) is the shape of the remote, not a hump.
- Cross-section as v6 (lower quarter ellipse, straight band, roll round the face). The lower part is sheared along y by `zb(y)`, so the outline and the walls stay vertical.
- `board_gap` 25 (24 in v6): with no bend the wheel sits centred between two 2.0 cross walls and needs the extra millimetre. L 225.43.

## 3. Construction: 3 printed case parts (v6 had 7)

| Part | What it is | Prints |
|---|---|---|
| `shell` | the whole face and all four walls in one piece; on the inside of the face: display bosses, IR saddles, wheel-zone cheeks + cross walls + EC11 bulkhead, key collars, 4 board clips, the end block | face down on the smooth plate, turned corner to corner (needs 191 × 191 of a 220 bed). No overhang, longest bridge 5 mm |
| `head_back` | flat plate, tip to keel line; 4 display posts, the wheel's well, lips inside the walls | outside down |
| `key_back` | flat plate, keel line to the end = the battery door; flat battery deck (v7.1; three ribs in v7.0), lips, 2 tongues | outside down |

Unchanged from v6: wheel, caps and rockers, D-pad ring, contact plates A/B, dock and its plates (the dock pocket is recut from the keel envelope).
Gone: head body, key body, both face panels, collar frame, ridge, TPU grip pad, tenons.

Why this way up: a V back cannot lie on the bed, so a one-piece back tray (the mockup's wording) was not printable. Each half of the V is a plane, so each back plate prints flat; the shell prints on its face, which gives a face with no panel seams.

## 4. Rules applied (FDM guidelines: Prusa "Modeling with 3D printing in mind", Hubs/Protolabs enclosure guide, Hackaday enclosure tips)

- Sliding fits between printed parts `fit` 0.25 a side; locating lips `lip_clr` 0.3 with a stepped lead-in.
- Self-tap pilots for M2 drawn 1.9 (96 % of the thread), 48-gon, with a lead-in cone; clearance 2.6; countersink 4.2.
- Every bed edge is a chamfer, not a round: the plates' foot is 35° (so it stays under 45° when the plate is tilted flat); the face edge is the roll (41°).
- Horizontal holes in the shell have their teardrop roof towards the back (print-up). The USB-C notch is open to the wall's edge, so it has no roof.
- Nothing under 1.2 mm except the named features in `case/tests/test_v7.py` `EXCEPT`.
- Face-down export is a rotation about y. `test_shell_is_a_true_flip_not_a_mirror` guards it.

## 5. Fasteners: 8 × M2 countersunk, all from the back (v6: 10)

- 4 × M2 × 12 through the head plate's posts and the display's corner holes into the face bosses. All four heads sit at z 1.5 (`z_seat`), sunk deeper at the antenna end, so one length fits all: 3.0 mm of thread in each boss.
- 2 × M2 × 8 from the head plate into the cheeks beside the wheel.
- 2 × M2 × 8 from the key plate into the end block.

## 6. Assembly: everything from the back, shell lying on its face

1. Caps, rockers and the D-pad ring into the face.
2. IR LEDs: dome into the hole in the tip wall, body pressed into its saddle.
3. Button board (mic module on it) pressed onto its 4 clips until they click.
4. Display board down onto its 4 bosses, USB-C to the tip.
5. EC11 soldered to its carrier, nut and wheel on; drop the bushing into the U-slot, tighten the nut.
6. Lay the wires into the notches of the two cross walls (battery pair and inter-board set on −x, the roller's three on +x).
7. Contact plate into the end slot.
8. Head plate on: 4 × M2 × 12, 2 × M2 × 8.
9. Battery taped to the key plate's deck (v7.1; it lay on foam over ribs in v7.0), its wires long enough to open the door. Key plate: tongues in at 45° under the cheeks, lay it down, 2 × M2 × 8.

Battery change later: 2 screws, key plate off along its 45° line.

## 7. Verification

- `case/v7/export.sh all`, then `python3 -m pytest case/tests/test_v7.py` (49 tests) and `python3 case/fit_check_v7.py`.
- The fit check covers: bought parts against the case (grown 0.15), wires, every part going in from the back, the head plate lifting straight off, the key plate going along its 45° line (and not lifting straight off), keys pressed, rocker tipped, wheel turning.
- Test pieces: `t0_screw_gauge` (five pilots 1.7 to 2.1, pick the one that bites), `t1_wheel_zone`, `t2_bottom_end`.

## 8. Not confirmed on hardware [CHECK]

- The right pilot size on the user's printer (T0). 1.9 is the guideline value.
- The bed: the shell needs 191 × 191 mm.
- Display bosses are now Ø5 (Ø4 in v6), flat on the LCD side at the antenna end. Assumes nothing else stands on the board's front within 2.5 mm of the corner holes.
- IR LEDs sit 0.25 higher than v6 (z 12.46) so their flange clears the display PCB without the bend; the skin over them is about 0.9 at its thinnest.
- Carried from v6: EC11 clone body and nut size, wheel press fit, IR through the skin (IR-transparent filament), contact plate B connector size.
- The viewer was built but not opened in a browser here.
