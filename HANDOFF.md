# ESP32 universal remote: handoff

A battery-powered remote built around the **LCDwiki E32R24P** (ESP32-32E, 2.4" ST7789, XPT2046 resistive touch, from MakerBazar). It replaces three remotes (Android TV, Sony soundbar on optical, set-top box) and adds whole-home control through Home Assistant.

## Status at a glance

| Piece | State | Notes |
|---|---|---|
| Case v3 (`case/stl_v3/`) | Done and checked | Watertight, single body, support-free in the exported orientation. Superseded by v4 for looks. |
| Case v4 (`case/remote_case.scad`) | **Exported and checked** (`case/stl_v4/`) | All parts watertight, one body each. Only overhang: 3 mm² per tip corner at 42°. Battery bay clear. IR LEDs now behind a 0.6 mm skin; print `ir_test` first. Caliper [CHECK]s still open. |
| Firmware (`firmware/remote.yaml`) | Validates in ESPHome 2026.10.1 | Not compiled or flashed. Lambdas are only type-checked at compile time. |
| Voice relay (`firmware/voice_relay.py`) | Written against androidtvremote2's real API | Not run against a TV. |
| Button PCB (`pcb/`) | **Not finished** | The auto-router reached 4 unrouted nets (INT, GND, VBAT, BTN_UP) plus 13 jumpers. The user chose a hand-planned route. |


## 2026-10-30 session: firmware rewrite (overrides "Firmware notes" below)

- `firmware/remote.yaml` (device) + `firmware/ui.yaml` (LVGL, 4 tabs: TV / Audio+STB / Home mock / Status) + `firmware/sim.yaml` (same UI in an SDL window; screenshots in `firmware/screens/`). **Compiles** for the ESP32 in ESPHome 2026.10.1 (RAM 30 %, flash 61 %); not flashed yet. The old file is `remote.yaml.bak-2026-10-30`.
- Works **without the MCP23017**: detected at boot (`mcp.is_failed()`), keys are filtered out (a failed expander reads every pin as pressed), wake is touch-only (IO36 PENIRQ, R22 pull-up; IO35 floats without the board), amber banner + HA "Button board" sensor + LED blink, I2C 0x20 probed every 2 s and the remote reboots when the chip appears.
- Fixed: `interrupt_pin` was missing on the MCP23017, so IOCON.MIRROR was off and the port-B keys (POWER, VOL, CH, MUTE) could never wake the ESP32. All 14 keys now use the pinmap.json bit numbers (wake mask 0xDDFF). IO35's ext0 wake is armed by hand in `go_to_sleep` because ESPHome won't share the pin.
- Power: WiFi off at boot (only TV keys / voice / "stay awake" start it), DFS 80–240 MHz, LCD SLPIN, pins held in zero-current states (IO19/IO23 have SD-slot 10k pull-ups: never drive them low), no ROM log on wake, ultra saver ≤ 20 %, IR-only ≤ 5 %. Power-on gives a 3-min OTA window. **Measure the sleep current**: the CH340C is the unknown.
- `[CHECK]` on hardware: LCD at 80 MHz SPI, `output_power: 13dB`, battery ×2 against a meter, all IR codes (0 = not captured, shown as a toast).
- Uploaded with `firmware/upload_to_copyparty.sh` to copyparty `/firmware/` (never uploads `secrets.yaml`).

## 2026-10-28 session: changes that override earlier sections

**Keys: 14 now.** VOL+/VOL− (left column), CH+/CH− (right column) and MUTE (between) sit below BACK/HOME/VOICE. Button-board coordinates: VOL+ (8.5, 77), VOL− (8.5, 90), MUTE (21.5, 83.5), CH+ (34.5, 77), CH− (34.5, 90). The button board is now **43 × 112 mm** and the remote 206.4 mm long. The chip stays at (20.6, 63.5): old keys enter its top row (GPA), new keys its bottom row (GPB1–5). The bottom parts (IR driver, C2, J3, J5) move to y about 95–112.

**Expander: MCP23017-E/SP (I2C), kept.** The user found the DIP-28 part (the MCP23S17 SPI version was considered for price, then dropped). Wiring is unchanged: IO1 SDA, IO5 SCL, IO35 INT, R1/R2 4.7k pull-ups. J5 keeps 7 nets: VBAT, GND, IR, 3V3, INT, SCL, SDA. The new keys use GPB1–5 (pins 2–6) on the chip's bottom row.

**Mic moved** to the button board's top-right: a round INMP441 module (Ø15, about 3 mm tall port-up [CHECK]) centred at board (34, 7), with a 3-slot grille and a Ø6 gasket ring above it. At the tip it collided with the LCD glass (only 8.7 × 4.1 mm free there). No copper is needed under it; it's wired straight to the display board as before. Remove J4 from `board.py`.

**Case fixes:**
- The screen window now follows the LCD's active area (36.2 × 49, 2.2 mm from the glass's antenna end and 8.8 mm from its USB end) plus 0.5 mm. It was centred on the glass, which showed about 4 mm of black at the tip end and cut 2 mm of pixels at the other.
- Cap flanges used to collide with the guide collars (also true in v3). The collars are now 1.2 mm flange pockets, and round caps have a key tab (pointing to the tip) in a collar slot, so the icons can't turn. Ring flanges no longer reach inwards.
- New icons: + / − (VOL), chevrons (CH), speaker-x (MUTE).
- The light-pipe guide tube was removed (it hit the display PCB edge). The wall hole stays; the filament runs under the PCB to the LED past the SPI connector [CHECK].
- The antenna-end display posts are flattened 0.4 mm clear of the LCD glass. The ribs start 16 mm into the board and the end stops sit at x ±3..9, to clear the mic module.

**Measured on the real board (user, 2026-10-28):** the USB-C sits about 1 mm *inside* the PCB edge (not 2.7 mm out) and is 3.2 mm tall; the tallest back part is the speaker JST at 4.6 mm; the screen area is 49 × 37; the RGB LED is 4.5 mm square, 31.5 mm from the antenna end (taken as its near edge, so the centre is 33.75, matching the drawing [CHECK]). So the display board now sits against the tip wall (db_y0 = wall + clr = 2.5) and the USB opening takes a full plug overmold (12.7 × 6.7, r 2) with a 1.5 mm 45° funnel. The board shift moved the back plate's screw holes too, so re-print the back plate if one was printed earlier.

**More user measurements and decisions (2026-10-28, later):**
- The lit area starts **10.0 mm** from the antenna-end board edge, not the 8.5 estimated from the drawing. The window now uses `aa_from_ant = 10.0` directly.
- RGB LED: 31.5 mm was to its near edge, so its centre is 33.75 mm from the antenna end. **The light pipe is dropped**: the 5050 faces the back plate, and a side pipe would cross the SPI connector and only pick up side-glow. Firmware should show status on the screen instead (a coloured flash: IR sent / WiFi sent / reconnecting / low battery).
- USB-C: a trapezoid notch (45° sides, top view) 1.85 mm deep. Its floor is a 0.6 mm skin (it extends into the board clearance) with a receptacle-only hole (9.3 × 3.3, top at the PCB back), so only the USB-C shows from outside. A thick plug overmold stops on the floor, about 1.65 mm short of the receptacle face (the bare board is already 1 mm). Test with the user's cables using `part="usb_test"`, a 0.65 mm plate with the same hole: hold it against the bare board's USB end and plug through.
- STL exports are not byte-identical between runs (checksums change while the geometry stays the same), so compare geometry, not hashes, when deciding whether a part changed.

**After the first test prints (2026-10-28, later still):**
- The screen window matches the pixels ✓.
- The boards wouldn't go in: the cavity followed the back chamfer, so the open back was only 39.8 mm wide (boards 42.9 / 43). The cavity is now straight down to the back, and `back_ch` is 3.0 so the shell's back edge stays 0.8 mm thick. `fit_check.py` now also sweeps each part up from the open back (the insertion test); it reproduces the old failure and passes now.
- The IR LEDs had no wire path past the display PCB (it fills the width). There's now a 2 × 1.2 mm groove in the -x side wall at y 9–11 (`ir_wire`): the leads bend sideways behind the corner post, drop down the groove, and run along the plate.
- The caps were tight at 9.2 (0.3/side), too short, and the flange tab lost its slot when pressed. Now: `cap_hole` 9.5 (confirmed 2026-10-29 with `cap_fit_test`: 9.5 slides well, 9.65 is too loose), `cap_proud` 3.0, flange 0.8 thick with a 0.9 overlap, and a **rib in a blind notch** cut from inside, 0.6 mm short of the face so nothing shows (`rib_*`) instead of the flange tab. A 1.0 flange made a pressed cap touch the switch body, so it stays 0.8.
- USB-C: photos of the first print (`reference/photos/`) seemed to show the socket about 0.45 mm towards BOOT, so `usb_x` went to -0.78 (wrong direction, see below) and the floor hole is 9.6 wide (0.33 a side for the board's screw play). The user measured 17 mm from the RESET-side board edge to the socket's edge.
- USB-C, second print (2026-10-29): **+x is the BOOT side.** shell.stl is exported face down, so the viewer's top view is mirrored, and the 0.45 mm photo fix (-0.33 → -0.78) went the wrong way (the second print was worse, about 2 mm off). `usb_x` is now **+1.22** (2 mm towards the real BOOT side from the second print). Check the third print before changing it again, and judge left/right in the viewer's assembled view, not the print-orientation shell.
- **Caps v2 (2026-10-29), print-tuned after the hollow caps failed:** the user reported a messy grip sleeve, a sagging roof, the side rib tilting the cap, weak inner ribs and a tight D-pad. The caps are now **solid with a hex bore** from below (`grip_af` **3.4** across flats: the user's grip_test, 2026-10-29, fitted well at 3.4, the 1-groove plug). There's no hollow, sleeve or slits: every feature is at least 0.8 mm, and the only bridges are the 3.6 mm bore ceilings. The key rib is 1.0 wide and stops 0.45 short of the notch's blind end, with a chamfered tip. Flanges are 0.2 a side smaller, with a 0.3 elephant's-foot chamfer (`ef_flange`). The D-pad sectors and OK have 0.45 a side to the plate (`side_clr`), the same as 9.5 on 8.6. **Shell unchanged** (the holes, notches and collars are as printed).
- Mic module (user's photo): the common round INMP441 with header pins already soldered. The pins must come off (they'd hit the front plate). Measured 2.1 mm thick with the pins removed (2.6 with solder): it clears the D-pad collar by 0.65 mm and pressed caps by 0.95, and leaves 0.85 under the gasket ring for a ~1 mm foam ring.

**PCB: layout "pads" (2026-10-29).** At the user's request every wire lands on one row of 10 **hole-less copper pads** (J5, 2.54 mm, y 108.8) along the bottom edge. Component side, left to right: GND, LED1- (K1), LED2- (K2), IR, LED+ (VBAT), VBAT, 3V3, INT, SCL, SDA (mirrored in the copper-side guide). SCL/SDA come down through the SW13/SW14 interiors, the only way past the bottom keys' GND line. INT (pin 20) and 3V3 (pin 9) are boxed in by the chip's lanes, so they reach the row on **2 insulated jumper wires** (`hand_route.PADS_JUMPERS`). The IR driver is hand-laid on the bottom left; QB loops over Q1, and the row's GND comes in through Q1's emitter. Q1 sits at (12.5, 99.3), clear of the VOL- cap collar (now in `fit_check.py`). SMDs can be flipped end for end with a 4th layout item. DRC clean, all nets connected. The old layout is kept in `best_wires.pkl` / `board_wires.png`. `pcb/guide.py` draws `stl/button_board_copper_guide.png`. The printable board's copper pattern is now 1.4 mm high and its holes +0.3 (user's request).

**PCB: routed (2026-10-28).** `pcb/build_board.py` = hand route + router for the IR driver: all 18 nets connected, **0 jumpers, DRC clean** (`pcb/board.png`, `pcb/best.pkl`). `pcb/make_stl.py` makes a printable stand-in board (`pcb/stl/button_board_print.stl`): a 1.6 mm base with the copper pattern raised 0.4 mm for copper tape, holes +0.2 mm, printed copper side up (mirrored). The assembly and wire guide is `pcb/stl/button_board_copper_guide.png`. Print it in PETG/ASA, not PLA, and use low-temperature solder (Sn42Bi58). `export.py` (updated 2026-10-29) writes `pcb/fab/`: a fab Gerber zip (F/B copper, F/B mask, F/B silk, outline, PTH drill; checked by rendering it with gerbonara), KiCad pcb/pro, plotter SVGs and pinmap.json. The SMD silk goes on the copper side; the wire-pad names are on the bottom silk, reading from below. The 2 wire jumpers are dashed silk lines only (no holes).
- IR LED skin is now 1.0 mm: at 0.6 the slicer printed the pockets' outline on the outside.
- Release files are staged in `release/` and pushed to copyparty /stl/ with `release/upload_to_copyparty.sh`.

**PCB (earlier notes):** `pcb/board.py` layout `"wires"` (no connectors: wires solder to existing pads; I2C pull-ups go on the display board; INT push-pull), chip at y 65.5, SW3 rotated 180. `pcb/hand_route.py` holds the full hand route for all 14 keys, GND and 3V3: **DRC clean, no jumpers so far**. Still to route: the IR driver (Q1, R4–R7, C2) and its GND, then export. The bottom-J5 and right-J5 router experiments (8–11 failed nets each) are in `sweep_bottom.log` / `try_*.png` for the record.

**Fit check:** `case/fit_check.py [stl_dir] [grow_mm]` intersects box/cylinder models of every component (both boards, LCD, back-side parts, USB-C, IR LEDs, switches and stems, chip, mic, battery, caps at rest and pressed) with the assembled shell and back plate. Result: **no collisions** at exact size. At +0.2 mm only designed contacts remain (posts and ribs on boards, LEDs in clips, 0.18 mm round the USB-C, 0.2 mm round cap flanges).

**Viewer:** `case/stl_v4/viewer.html` (open directly, or `python3 -m http.server 8765` in that folder).

**Before printing the shell:** caliper-check `lcd_from_ant` (6.34), `usb_out` (2.7) and the LED position on the real board. Print `ir_test` in the chosen filament.

**Still to do:** update `board.py` for 14 keys, 112 mm and no J4; hand-route; update `remote.yaml` (5 new keys on GPB1–5 with their IR/HA actions).

## Hardware

- **Display board:** E32R24P, 42.89 × 74.33 × 5.44 mm, holes Ø3.2 on 66.33 × 34.89 mm (4.0 mm from each edge), pads Ø4.8. USB-C is on the back, centred within 0.33 mm, and overhangs the edge by about 2.7 mm. Charger (TP4054, about 300 mA), LDO (ME6217), CH340C, and amp (SC8002B) are all on board. See `reference/`.
- **Button board (yours, one-sided, home-etched):** 43 × 96 mm.
  - MCP23017-E/SP (DIP-28, no socket).
  - 9 × 6x6x7 mm THT tact switches.
  - S8050 TO-92 IR driver with legs bent flat.
  - All resistors and capacitors are 1206, on the copper side.
- **Mic:** INMP441 module, wired straight to the display board. In v4 it is glued under the tip, above the screen.
- **IR:** two 3 mm IR LEDs in the tip wall, held by printed clips (v4).
- **Battery:** LiPo 503450 (5 × 34 × 50 mm, about 1000 mAh). It plugs into the display board's BAT socket, and a tap off the same +/− leads goes to the button board's J5 VBAT/GND.
- **Plotter rules (pen-plotted resist, 0.4 mm Staedtler):** 1.0 mm traces, 0.8 mm clearance, 1.0 mm edge clearance. Never route between DIP pins. 0.6 mm is acceptable only as a neck-down.

## Pin map (display board ESP32)

| GPIO | Use | Where to get it |
|---|---|---|
| IO1 | I2C SDA (MCP23017) | Serial 4P connector (TX0). UART logging is off. |
| IO5 | I2C SCL | SD socket CS pad (solder). Has a 10k pull-up on board. |
| IO35 | MCP23017 INTA, deep-sleep wake (ext0, active low, 10k pull-up on button board) | Expansion connector (3.3V / IO35 / GND) |
| IO27 | IR transistor base (via 1k, 10k pull-down) | SPI 4P connector |
| IO18 / IO19 / IO23 | INMP441 SCK / WS / SD | SPI 4P connector |
| IO22 / IO16 / IO17 | On-board RGB LED R / G / B (common anode, low = on, MHP5050) | On board |
| IO34 | Battery voltage ×½ (100k/100k) | On board |
| IO4 | Amp shutdown (high = off, 10k pull-up) | On board |
| IO21 | Backlight | On board |

Button pins on the MCP23017 are chosen by the PCB layout and written to `pinmap.json`. Copy the bit numbers into `remote.yaml`, where they are marked `[CHECK]`.

## Key decisions and why

- **MCP23017 rather than direct GPIO:** only about 7 pins are free. INTCAP latches the key that woke the ESP32, so a quick tap from deep sleep isn't lost.
- **Android TV keys and voice go over WiFi** (Android TV Remote protocol v2, through HA and the relay). Android TV voice over BLE isn't standardised.
- **Soundbar and set-top box use IR from the remote itself:** it's instant from sleep, while WiFi takes 1–3 s to reconnect.
- **Voice path:** INMP441 → UDP → `voice_relay.py` on the Rock 5C → TV. Pair first with `--pair`. If the TV refuses third-party voice sessions, the voice feature is dead on that TV, so test this before building.
- **Case printing:**
  - Shell prints face-down. Back plate prints inner-face-down. Caps print flange-down.
  - Every overhang is 45° or a short bridge.
  - The front must stay flat for this to work.

## Case v4: what changed from v3, and the next step

The changes respond to the user's feedback:
- Flat tip with flush USB-C. The receptacle passes through the wall and its face sits 0.2 mm inside the surface.
- A 3.5 mm 45° back chamfer, with the back plate forming its lower part, and a 2.5 mm front bevel, so the visible side band is about 10 mm.
- Overall 15.8 mm thick, plus a 3 mm palm swell.
- C-clip holders for the IR LEDs.
- Back plate held by 6 screws:
  - 2 at the tip, through printed spacers and the display's USB-end holes into the front posts (M2.5 × 14).
  - 2 between the boards.
  - 2 at the bottom.
- The tip dovetail is removed.
- Ring D-pad, accent groove, light pipe (1.9 mm hole plus a teardrop guide), and mic grille are kept from v3.

**Done (2026-10-28):** exported shell, back, caps and ir_test to `case/stl_v4/` with previews `v4_*.png`. Results:
- shell: watertight, 1 body. The only >45° faces are 3 mm² per tip corner of the inner back chamfer (42°), which is fine. Flat bridges are the 0.8 mm accent groove and the about 6 mm USB-C roof.
- back: no overhangs. caps: 11 bodies; flat areas are the stem-socket roofs, as in v3.
- The battery (34 × 50) clears the shell at z 2.1–7.1 for any y0 from 83 to 131.
- Fixed: the accent groove used to cut 1.1 mm into the POWER hole chamfer (also true in v3). It now stops short of the hole.
- New: `ir_skin = 0.6`. The IR LEDs sit in blind teardrop pockets behind a 0.6 mm skin, so they're hidden (0 = open hole). Carbon-black PLA blocks 940 nm, so print `part="ir_test"` (0.4/0.6/0.8/1.0 mm skins) in the chosen filament and check range with the IR receiver first.

**Original steps (kept for reference):**
1. Export each part:
   ```
   openscad -D 'part="shell"' -o shell.stl case/remote_case.scad    # also: back, caps (caps include 2 spacers)
   ```
2. Run the overhang and watertight check. The snippet is in the "Checks" section.
3. Expect possible issues at:
   - the IR clip cubes against the tip wall;
   - the cavity hull at the back chamfer, which must still clear the battery (34 mm wide at z 2.1);
   - the screw posts at x ±15.5.
4. Render front and back previews before printing.

**v4 [CHECK] items:**
- `usb_out` (2.7): if it's wrong, the receptacle won't line up with the flush opening.
- LED position (12 mm from the edge, 40.7 mm from the USB end).
- `lcd_from_ant` (6.34, from the drawing).

**Known tight spot:** there are only 6.86 mm behind the display PCB, which isn't enough for JST plugs plus wire bends. Solder the wires straight to the connector pins.

## PCB: next step (hand-planned route)

**Scripts:**
- `board.py`: placement and nets.
- `route.py` + `astar.py`: numba A* router with wire jumpers.
- `check.py`: DRC and preview.
- `export.py`: writes KiCad, Gerber, drill, the plotter SVG (mirrored, copper side), and `pinmap.json`.

`partial_route_export/` holds the auto-router's best attempt, with 4 nets unrouted. It's useful in KiCad as a starting point. **The KiCad file hasn't been opened in KiCad yet.**

To finish by hand:
1. Remove the J4 mic header from `board.py`. The mic is now at the tip, wired directly.
2. Keep the top about 6 mm of the button board copper-free. The ESP32 antenna faces it.
3. Plan the topology:
   - GND daisy-chains through each switch's internally joined pad pair.
   - POWER → GPB0 runs down the left edge and around the chip's left end.
   - INT and RESET-3V3 go round the chip's right end.
   - The other 8 keys go to GPA0–7 in left-to-right order.
4. Accept 2–4 wire jumpers rather than squeezing.
5. Re-run `check.py` DRC, then `export.py`.
6. Etch a test coupon first: 0.6 / 0.8 / 1.0 / 1.5 mm lines and 0.5 / 0.8 / 1.0 mm gaps.

## Firmware notes

- `remote.yaml` includes:
  - deep sleep with wake on IO35;
  - an INTCAP read at boot;
  - GPIO holds for the IR, amp and LED pins in sleep;
  - LED feedback (green = IR sent, blue = WiFi sent, amber = reconnecting, pulsing blue = listening, red blink = battery below about 3.45 V);
  - an LVGL page;
  - Sony SIRC and NEC placeholder codes. Capture the real codes with the Wemos IR blaster using `remote_receiver: dump: all`.
- **Battery-life risk:** the CH340C runs from 3.3 V all the time. Measure sleep current at the battery lead. If it's over about 1 mA, lift the CH340C's VCC pin and use OTA updates only.
- Set a static IP and the HA entity names (`remote.android_tv`) where marked.

## Environment used

OpenSCAD 2021.01 (headless via xvfb-run), Python 3.13 with shapely, trimesh, numba, matplotlib and pygerber, ESPHome 2026.10.1, and androidtvremote2.

## Checks

The overhang check used on every STL (z is the print direction):

```python
import trimesh, numpy as np
m = trimesh.load("shell.stl"); n = m.face_normals; c = m.triangles_center; a = m.area_faces
down = (n[:,2] < -0.7072) & (c[:,2] > m.bounds[0][2] + 0.15)
print("watertight", m.is_watertight, "bodies", m.body_count,
      "overhang >45deg mm2", a[down & (n[:,2] >= -0.999)].sum(), "flat bridges mm2", a[down & (n[:,2] < -0.999)].sum())
```
