# umote case v5: bent two-half body, Navi-roller, flush face, dock

Date: 2026-11-05. Status: design, approved in conversation, pending review of this document.
Concept models (throwaway, for the look only): `2026-11-05-remote-case-v5-assets/concept_d.scad` (it includes `concept_n9.scad` and `concept.scad`; render a part with `-D 'view="d_body"'` etc.). Step-by-step assembly view: `2026-11-05-remote-case-v5-assets/v5-assembly.html` (open in a browser).
Research behind it: `reports/Remote enclosure design research.md` and `research_notes/Remote enclosure design research/`.

## 1. Intent

The v4 case (`case/remote_case.scad`) was sized for a 34 × 50 × 5 mm LiPo. The user now has a **46 × 105 × 5 mm** LiPo, which doesn't fit the 43.6 mm cavity. Rather than only widening v4, the user asked for a case that looks and feels like the inventive handhelds of the late 90s and early 2000s (Nokia, Sony): innovation in **form and interaction, not colour**. It must still print on a home FDM printer without supports and assemble cleanly.

The chosen direction combines:
- **Nokia 8110**: the body bends at the gap between the two boards, so the screen half tilts toward the user's eyes and thumb.
- **Nokia 7110 Navi-roller**: a thumb roller in the crease, just below the screen.
- **Nokia N9 / Lumia**: a flush dark face panel that the screen sits in with no visible frame, inside a rolled body rim.

## 2. Goals, non-goals, anti-goals

**Goals** (the user's numbered picks from the idea list are in brackets)
1. Fit the 46 × 105 × 5 LiPo under the button board. The 105 mm is the total, including the protection board and lead fold (user confirmed). Its leads come out at the tip end, toward the collar and the display's BAT socket.
2. **8° bend** at the board gap [1].
3. **Roller** in the crease: roll to scroll or change volume, press to select [2].
4. Profile: crisp flush face, upper edge rolled in round the face panel, lower edge curving into a flat back [4 + 5]; **floating screen** in a flush dark panel [10].
5. **VOL and CH as rockers** [12], **key islands** [15], **D-pad ring 0.5 mm proud** [13], **nub on OK** [14], **solid key feel** [22].
6. **Strap eyelet** [8].
7. **Charging dock** with spring contacts [25] and **magnets in the back** [26].
8. **No visible screws** [28]; **seams are deliberate lines** [29].
9. Every part prints **without supports** and fits a **180 mm bed**.
10. **USB-C opening moves 1 mm** from the second print instead of 2: `usb_x` 1.22 → **0.22** (still +x = BOOT side).

**Non-goals**
- No change to either PCB, except wires soldered to two spare MCP23017 pins and the roller switch (section 6).
- Struck by the user: side jog dial [3], tapered side profile [6], pebble outline [7], IR window cap [9], concave key tops [11], glow icons [16], textured-back contrast [17], side grip texture [18], finger rest [19], soft-touch panel [20], rubber foot strips [21], light strip / glowing ring [23, 24], swappable back [27].
- Colour schemes as the "innovation". Colours are the builder's call (section 9).

**Anti-goals** (would be a failure even if it technically works)
- Anything needing supports, or a part longer than 180 mm.
- Visible screws, or seams that read as gaps or steps.
- Keys that wobble or rockers that press both switches at once.
- A roller that turns by itself when the remote is put down, or a dock that shorts the battery or USB.

## 3. Constraints carried over from v4 (all still true)

- Display board LCDwiki E32R24P 42.89 × 74.33, holes Ø3.2 on 66.33 × 34.89 (4.0 from each edge); LCD active area, window offsets, USB-C (`usb_in` 1.0, `usb_body_h` 3.2, plug-overmold notch with 0.6 skin and receptacle-only hole) and IR LED clips as in `remote_case.scad`.
- Button board 43 × 112, switch and cap positions from `pcb/board.py` (unchanged). MCP23017 DIP-28 and Q1 on top; SMDs on the copper side (0.8 mm).
- Cap system v2 (hex bore 3.4 AF, `cap_hole` 9.5, flange pockets, key ribs) as printed and confirmed.
- Thickness: 15.8 mm at the edge; stack heights `db_*`, `bb_*`, `batt_z0` as v4. No palm swell (the back must print flat).
- The display board's back is clear round all four corner holes (`reference/board_back.jpg`), so standoffs may sit under any of them.
- `fit_check.py` and `check_print.py` are the acceptance tools; HANDOFF lists the open caliper [CHECK]s.

## 4. Form

All numbers come from the concept models; the builder may refine them (section 9).

- **Plan**: 51 mm wide (inner 47, walls 2.0), same outline family as v4 (tip_r 3.5, corner_r 9).
- **Length about 218 mm**: board gap widens from 6 to about **18 mm** for the roller. Board positions inside each half are unchanged; only the button board half moves down.
- **Bend**: the head (screen half) is rotated 8° about a transverse axis on the face line at the head/collar joint, face concave. On a table the remote rests on the key half with the screen tilted up.
- **Cross-section** (both halves):
  - lower edge: quarter ellipse 3 mm across × 7 mm up into a flat back, with a 0.57 mm 45° foot where the curve passes 45°, so it prints flat and hides elephant's foot;
  - straight side band from z 7 to 10.8;
  - upper edge rolls in 2.2 mm over the top 5 mm (41° at the rim);
  - a 1.4 mm body-colour land round a **flush 1.6 mm face panel** (0.15 mm gap).
- **Face panels** (one per half), dark:
  - Head panel carries the screen window (v4 window: active area + 0.5, 1.5 radius), sitting directly over the LCD.
  - Key panel carries the cap holes, the D-pad opening and ring pocket, the mic grille slots, the cap flange collars underneath (as v4), and two **0.5 mm key-island wells**: nav (D-pad + BACK/HOME/VOICE) and media (VOL rocker, MUTE, CH rocker).
- **Collar**: an accent-colour band across the crease, the only joint visible from the side; it houses the roller.
- **Eyelet**: a strap slot through a solid boss in the key half's bottom corner.
- **Back of the key half**: a flush **magnet plate** that hides the screws and aligns in the dock.

## 5. Parts, print orientation, assembly

| Part | Prints | Notes |
|---|---|---|
| Key body | back down, textured plate | battery floor, eyelet boss, contact inserts, magnet pockets, 2 screw bosses at the bottom end, magnet-plate recess |
| Head body | back down, textured plate | display posts at the USB end, USB-C notch, IR clips **tilted 8° down** to cancel the bend |
| Collar | on its side | roller cavity and slot (top edge bridges ≤ 17 mm), head **fork** with 2 standoffs under the display's antenna-end holes, key **tongue** on the key floor, lips that the two panels hook under |
| Head face panel | face down, smooth plate | hooks under the collar lip; **4 releasable snaps** at the tip end. It must come off without damage: a plastic card in the tip-end seam pops the snaps (user's choice). No visible screw, hole or slot. |
| Key face panel | face down, smooth plate | button-board posts or clips; 2 screw bosses; hooks under the collar lip |
| Caps, rockers, OK, D-pad ring | flange down | section 7 |
| Roller wheel | on its side | 16 mm |
| Magnet plate | outer face down | |
| Dock | builder's choice | section 8 |

**Assembly order** (what makes the screws invisible):
1. Key body: press the 2 contact inserts into the bottom end, glue magnets.
2. Collar onto the key body: its tongue lies on the key floor, 2 screws down from the face side.
3. Battery on foam; roller cradle into the collar.
4. Head body hooks onto the collar fork.
5. Display board: 4 screws from the face side. The USB-end pair goes into head-floor posts; the antenna-end pair goes through the fork standoffs into the head floor. This one step locks head, collar and board together and keeps the USB-C on its notch.
6. Key face unit: caps, rockers and ring go into the key panel from inside, then the button board fixes to the panel, so switches always align with the holes. The unit hooks under the collar lip and drops in.
7. Head face panel: hook under the collar lip, snap at the tip.
8. 2 screws up through the key back's bottom end into the key panel bosses; the magnet plate covers them.

Wires run through the collar: battery → display BAT, display ↔ button board (the existing loose-wire set), roller → button board.

Fasteners: M2.5 everywhere. Heat-set inserts where a screw is removed in service (CNC Kitchen sizes: M2.5 × 4 insert, 4.0 mm hole, ≥ 1.6 mm wall, hole ≥ insert + 1 mm deep). Self-tapping into 2.1 mm holes is acceptable where it was proven on v4.

## 6. Roller (decided with the user)

- **Part**: a standard 5-pin EC11 rotary encoder (in stock at Robu), used bare: not the KY-040 board, which is 18 × 30 mm.
- **Mounting**: laid on its side so the shaft runs across the remote, encoder body beside the wheel, **off centre** (away from the ESP32 antenna at the middle of the display board's antenna end).
- **Wheel**: 16 mm, knurled, about 1.2 mm proud of the collar top.
  - Depth is tight. With the shaft at z ≈ 9.0, the EC11 body (about 11.7 × 12) spans z ≈ 3.2–14.8, leaving about 0.9 mm of collar skin above it and about 1.5 mm above the floor. The tact switch therefore sits beside the encoder, not under it.
  - If it doesn't fit, in this order (my call): first drop the wheel to 1.0 mm proud; then thin the collar top locally over the encoder. **Never** add a bump on the back at the crease, because that's where the remote rests on a table.
  - Measure the actual EC11 (body, shaft diameter and type, detents) with calipers before modelling: [CHECK]. Printed with a bore to the EC11 shaft. The user will **trim the shaft** to whatever length the design needs.
- **Press**: the EC11's own push acts along the shaft, so it isn't used. Wheel and encoder sit on a printed cradle hinged at one end; pressing down clicks a 6×6 tact switch wired **in parallel with OK**. The cradle should not let the wheel's weight or a table press trigger it.
- **Inputs**: A/B to the MCP23017's two free pins, **GPB1 (pin 2) and GPB5 (pin 6)**, soldered on the chip's legs, internal pull-ups. Common to GND.
- **Firmware**: decode quadrature in the existing MCP interrupt path (IO35, CHANGE). ESPHome's `rotary_encoder` wants internal GPIOs, so this is a lambda. Roll = scroll on lists and pages, volume elsewhere (exact mapping is the firmware plan's call). Firmware flash is already above its 85 % target, so keep the code small.
- **RF check**: after fitting, compare Wi-Fi RSSI on the diag page with and without the encoder in place.

## 7. Keys

- Round caps (POWER, BACK, HOME, VOICE, MUTE): v4 caps unchanged.
- **OK**: v4 OK cap plus a 1.6 mm dome nub.
- **Rockers**: one cap over VOL+/VOL- and one over CH+/CH- (13 mm apart), capsule-shaped with a shallow saddle top. They need a **centre fulcrum** so one end presses only its own switch.
- **D-pad ring**: accent part fitted from inside with a flange, standing 0.5 mm proud.
- **Solid feel**: keep v4's confirmed fits; the builder may add guides or a damping pad if testing shows rattle.

## 8. Dock and magnets (parts confirmed in stock by the user's checks)

- **Dock contacts**: 2 × **P75-B1 spring test probes** (Hubtronics, in stock, 100 per pack) in the dock.
- **Remote contacts**: 2 brass **heat-set inserts flush in the bottom end** as pads, each wired from inside.
- **Magnets**: **10 × 2 mm N35 discs** (Quartz Components / MakerBazar, in stock) in the remote and the dock to pull it in and align it.
  - The battery covers almost the whole key floor, so the remote's magnets sit outside its footprint (bottom zone and near the collar).
- **Electrical**: dock 5 V enters the remote through a **Schottky diode** (pad → anode, cathode → the display board's **+5V** net).
  - From the schematic text (`reference/E32R24P_schematic.pdf`): the USB-C VBUS feeds +5V, which is also the TP4054 charger's VCC (pin 4) with C20/C22 on it. Solder the diode's cathode wire to a C20/C22 pad or TP4054 pin 4, whichever is reachable; confirm with a continuity check to the USB-C VBUS. No board change. Undocked pads are then dead, a coin across them can't short anything, and USB can't back-feed the dock.
- **Dock body**: printed cradle that holds the remote on its bottom end, screen toward the user. It is fed by a USB-C breakout or 5 V adapter. Its shape is the builder's call.

## 9. Left to the builder

- Exact radii, panel and land widths, collar length and lip geometry, as long as sections 4–5 hold and the wheel clears both board ends.
- Snap geometry, starting from the research rule (8–10 mm beam, 1.2 → 0.8 mm, 0.6 undercut, PETG).
- Where the button board fixes to the key panel (posts, clips or the v4 ribs moved to the panel).
- Colours and materials (matte PLA/PETG; dark panels; one accent for the collar and ring). It is not the point of the design.
- File layout: a new `case/remote_case_v5.scad` beside v4, exports in `case/stl_v5/`.
- Dock shape.

## 10. Verification and release

1. **Test prints first**, each exported and uploaded to copyparty `/stl/` with `release/upload_to_copyparty.sh`:
   - a **snap-fit coupon** (head-panel corner with three undercuts, for example 0.4 / 0.6 / 0.8). It tests that the snaps hold and release with a card in the seam without breaking;
   - a **roller cradle coupon** (collar slice with wheel, cradle and tact switch).
2. `fit_check.py` updated for v5:
   - the new battery, the moved board, the bend;
   - roller, cradle, standoffs, inserts and dock contacts;
   - insertion paths for each step of section 5.
   Result: no collisions except designed contacts.
3. `check_print.py` on every part in its print orientation: watertight, single body, no overhang > 45° above the first layer, bridges ≤ 17 mm. Every part ≤ 180 mm in its longest bed dimension.
4. Viewer rebuilt (`case/viewer/build_viewer.py`) and previews rendered before anything goes to copyparty.
5. On hardware: USB-C plugs in square at `usb_x` 0.22; IR range with the 8° tilt; RSSI check (section 6); dock charges and nothing is live when undocked.
