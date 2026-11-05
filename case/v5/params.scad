// umote case v5: every number and derived value. Nothing renders here.
// Coordinates as v4: origin at the centre of the tip, z = 0 on the back, front face at z = T;
// +y from the tip towards the bottom; +x is the user's LEFT (face up, tip away) = the BOOT side.
// The head (screen half) is modelled straight here; head_xf() in profile.scad applies the bend.
// Values marked [CHECK] want calipers on the real part.

// ---------- form ----------
W        = 51;       // 46 mm battery + 0.5 a side + 2.0 walls
wall     = 2.0;      // side walls
tip_wall = 2.2;      // tip wall: the v4 USB-C notch and IR pockets are sized for it
end_wall = 2.2;
T        = 15.8;
tip_r    = 3.5;  corner_r = 9;
clr      = 0.3;
theta    = 8;        // bend at the board gap, face concave
// cross-section (spec section 4): lower ellipse into a flat back, straight band, upper roll
ea = 3.0;  eb = 7.0;  bed_ch = 0.57;
roll_z = 10.8;  roll = 2.2;
land = 1.4;  pan_t = 1.6;  pcl = 0.15;
top_t = pan_t;       // v4 name for the face thickness (the cap system uses it)
floor_t = 1.6;       // back thickness under the battery (v4 plate_t)
// ---------- display board: LCDwiki E32R24P ----------
db_w = 42.89;  db_l = 74.33;  db_pcb = 1.6;
db_front = 3.84;  db_back = 4.63;
db_hole_off = 4.0;  db_hole_d = 3.2;
lcd_l = 60.0;  lcd_from_ant = 6.34;   // LCD backlight outline, from the antenna end (drawing) [CHECK]
// Active (lit) area: centred across, but NOT along the glass: 2.2 mm of black border at the
// antenna end, 8.8 mm at the USB/FPC end (measured off the vector drawing). The window
// follows the active area, so no black band shows at the tip end.
aa_w = 36.2;  aa_l = 49.0;
aa_from_ant = 10.0;                 // first lit row from the board's antenna-end edge (measured)
win_m = 0.5;                        // window overlap past the active area, each side
win_w = aa_w + 2 * win_m;  win_l = aa_l + 2 * win_m;  win_r = 1.5;  win_cham = 1.0;
usb_x = 0.22;                       // +x is the BOOT side. v4's second print (-0.78) sat ~2 mm the wrong way;
                                    // v4 moved it 2 mm (1.22), v5 moves it 1 mm instead (user, 2026-11-05)
usb_in = 1.0;                       // receptacle face sits this far INSIDE the PCB edge (measured)
usb_body_h = 3.2;                   // receptacle height off the PCB's back (measured)
// The face ends up wall + clr + usb_in = 3.5 mm in from the tip, so the cable's plug body has
// to enter the opening: sized for the USB-C spec maximum overmold (12.35 x 6.5) + clearance.
usb_w = 12.7;  usb_h = 6.7;  usb_r = 2.0;
usb_flare = 45;                     // notch sides (top view): angle from the wall's normal
usb_floor = 1.85;                   // notch depth; its floor is a skin in front of the board edge
usb_skin = 0.6;                     // floor thickness (runs into the 0.3 board clearance)
usb_hole = [9.6, 3.3, 1.4];         // receptacle-only hole in the floor: w, h, r (top at the PCB back);
                                    // 0.33 a side round the 8.94 socket takes up the board's screw play
led_from_edge = 12.04;              // RGB LED (5050, faces the back plate): from the long edge
led_from_usb  = 40.58;              //   and the USB end (measured: near edge 31.5 from the antenna end).
                                    //   No light pipe: it would cross the SPI connector and only catch
                                    //   side-glow. Status shows on the screen instead.

// ---------- button board ----------
bb_w = 43.0;  bb_l = 112.0;  bb_pcb = 1.6;
sw_body = 3.5;  sw_total = 7.0;  smd_h = 0.8;  top_parts = 4.4;
batt = [46, 105, 5];                // 46 x 105 x 5 total, protection board included (user); leads at the tip end
foam = 0.5;

// ---------- layout along y ----------
board_gap = 18.0;  bottom_zone = 9.0;   // gap 6 -> 18 for the crease roller
ir_x = 12;                          // IR LEDs either side of the USB-C
ir_wire = [9.0, 2.0, 1.2];          // IR LED wire groove in the -x side wall: y start, width, depth.
                                    // The display PCB fills the width, so the LED leads bend sideways
                                    // behind the corner post (y < 10.89, clear of the LCD) and drop
                                    // down this groove past the board's edge to the back side.
ir_skin = 1.0;                      // wall left over the IR LEDs (0 = open hole); 1.0 > two 0.45 wall lines, so
                                    // the slicer runs the outer walls straight past (0.6 printed a visible outline). Needs an
                                    // IR-transparent filament: not carbon-black PLA [CHECK]

// ---------- buttons (button-board coordinates, from board.py) ----------
dpad_c = [21.5, 25.5];              // OK switch; the ring's centre
dpad_sw = 13.0;                     // arrow switches sit 13 mm from it
ring_in = 6.3;  ring_out = 17.5;  ring_web = 2.2;  ok_d = 10.0;
singles = [  // [x, y, name, mark]
  [ 7.5,  6.0, "POWER", 6],
  [ 8.5, 50.0, "BACK",  8],
  [21.5, 50.0, "HOME",  9],
  [34.5, 50.0, "VOICE", 7],
  [ 8.5, 77.0, "VOL+", 10],
  [ 8.5, 90.0, "VOL-", 11],
  [21.5, 83.5, "MUTE", 14],
  [34.5, 77.0, "CH+",  12],
  [34.5, 90.0, "CH-",  13],
];
cap_d = 8.6;  cap_hole = 9.5;  cap_proud = 3.0;  cap_flange = 0.8;  flange_x = 0.9;   // cap_hole 9.5 confirmed by cap_fit_test
// cap_hole - cap_d = clearance: 9.2 printed too tight, so 0.45 per side now; confirm with cap_fit_test [CHECK]
cap_top_cham = 0.6;
// round caps are keyed so their icons can't turn: a rib on the cap's side runs in a blind
// notch cut from inside the plate, stopping rib_skin short of the face, so nothing shows from
// the front. ~0.9 mm of engagement, more than the 0.3 mm press travel the switch allows.
// The rib points towards the tip (-y).
rib_w = 1.2;  rib_out = 1.0;  rib_clr = 0.25;  rib_skin = 0.6;  flange_clr = 0.35;
flange_d = cap_d + 2 * flange_x + 0.6;
// ---- caps (v2, print-tuned; the shell's holes, notches and collars above are unchanged) ----
// Solid caps, printed flange down, with one hex bore from below for the switch plunger: a round
// plunger in a hex bore bears on six flats backed by solid plastic (no thin sleeve, slits or
// ribs, no roof over a hollow). Every feature is at least 2 line widths (0.8 mm).
grip_af = 3.4;                       // hex bore across flats: 3.4 fits well on the real switch (grip_test, 2026-10-29)
cap_rib_w = 1.0;                     // key rib: 0.35 a side in its 1.7 notch
cap_rib_h = cap_flange + top_t - rib_skin - 0.45;   // 0.45 short of the notch's blind end, so it can't bottom out
flange_shrink = 0.2;                 // flanges 0.2 a side smaller than the collars were drawn for
ef = 0.3;                            // elephant's-foot chamfer on each flange's bed edge
side_clr = 0.45;                     // D-pad / OK gap to the plate opening, per side (as 9.5 on 8.6)

// ---------- mic (INMP441 module on the button board's top-right, mirroring POWER) ----------
mic_b = [34.0, 7.0];                // button-board coordinates of the module's centre (port)
mic_mod = [15, 2.6];                // round module: diameter, height: 2.1 measured (pins removed) + 0.5 solder
// Placement is tight: clear of the D-pad's flange pockets, the accent groove, the mid
// screw post and the UP switch. It overhangs the board's top edge by 0.5 mm.

// ---------- roller (EC11 on its side, spec section 6) ----------
ec11 = [11.7, 12.0, 6.5];           // body: height across the shaft (z), length (y), depth along the shaft (x) [CHECK]
ec11_shaft_d = 6.0;                 // D-shaft [CHECK]
ec11_detent_steps = 4;              // quadrature steps per detent [CHECK]
whl_d = 16;  whl_w = 9;
whl_proud = 1.1;                    // 1.2 asked; 1.1 keeps the skin over the EC11 >= 0.8 and the pressed wheel 0.3 off the back
skin_min = 0.8;  ec11_gap = 0.2;
cradle_t = 1.0;  cradle_travel = 0.3;
tact = [6, 6, 3.5];                 // 6x6 tact switch beside the encoder
key_tongue = 6.5;                   // collar tongue on the key floor (7 in the spec's sketch; 6.5 keeps the battery under the board)

// ---------- fasteners, dock ----------
insert_m25 = [4.0, 4.0];            // hole d, insert length (CNC Kitchen M2.5 x 4)
insert_wall = 1.6;
pad_insert = [4.0, 5.0];            // M3 short brass insert as a contact pad: hole d, length [CHECK]
magnet = [10, 2];                   // N35 disc
pogo_d = 1.0;  pogo_l = 15.85;      // P75-B1 [CHECK] press-fit hole

// ---------- snaps (coupon-tuned in Task 3) ----------
snap_uc = 0.4;  snap_len = 9;  snap_t = [1.2, 0.8];  snap_w = 5;

// ---------- derived ----------
in_w  = W - 2 * wall;
db_y0 = tip_wall + clr;
db_end = db_y0 + db_l;
bb_y0 = db_end + board_gap;
L = bb_y0 + bb_l + bottom_zone + end_wall;
front_in = T - pan_t;
touch_z  = front_in - 0.3;
db_top = touch_z - db_front;  db_z0 = db_top - db_pcb;
batt_foam = 0.2;                    // under the battery: 0.3 less than foam, so the pouch clears the button board's SMDs by 0.3
batt_z0 = floor_t + batt_foam;
bb_z0  = floor_t + foam + batt[2] + smd_h;  bb_top = bb_z0 + bb_pcb;
act_top = bb_top + sw_total;
pz0 = T - pan_t;
cy = (db_end + bb_y0) / 2;          // wheel axle y
axle_z = T + whl_proud - whl_d / 2;
y_head_end = cy - whl_d / 2 - 0.4 - 0.4;     // collar face starts here
y_key_start = cy + whl_d / 2 + 0.4 + 0.4;
batt_y0 = y_key_start + key_tongue + 0.5;
aa_c   = db_y0 + db_l - aa_from_ant - aa_l / 2;
win_y0 = aa_c - win_l / 2;
holes = [for (sx = [-1, 1], sy = [0, 1]) [sx * (db_w / 2 - db_hole_off), db_y0 + db_hole_off + sy * (db_l - 2 * db_hole_off)]];
fork_y = db_end - db_hole_off;  fork_x = db_w / 2 - db_hole_off;
ir_z = front_in - 1.9;
function bpos(b) = [bb_w / 2 - b[0], bb_y0 + b[1]];
dc = bpos(dpad_c);

assert(in_w / 2 - batt[0] / 2 >= 0.3, "battery side clearance");
assert(abs(bb_y0 - db_end - board_gap) < 1e-6, "board gap");
assert(whl_d / 2 + 0.4 <= min(bb_y0 - cy, cy - db_end), "wheel clears both board ends");
assert(batt_y0 + batt[1] <= bb_y0 + bb_l, "battery under the button board");
assert(L <= 219, "length");
assert(T - (axle_z + ec11[0] / 2) - ec11_gap >= skin_min, "collar skin over the EC11");
assert(axle_z - ec11[0] / 2 >= floor_t + cradle_travel + cradle_t - 0.05, "cradle room under the EC11");
assert(bb_top + max(sw_body, top_parts) + 0.3 <= front_in, "button board parts hit the face panel");
assert(db_z0 - db_back >= floor_t + 0.3, "display back parts hit the floor");
