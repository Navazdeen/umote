// umote case v7 "Keel": every number and derived value. Nothing renders here.
// Coordinates as v5/v6: origin at the centre of the tip; the face is the plane z = T; +y from the tip
// towards the bottom; +x is the user's LEFT (face up, tip away) = the BOOT side.
// v7 is straight (no bend) and built the other way up from v6: ONE front shell (the face and the
// walls, printed face down) and TWO flat back plates that meet at the keel line. The back is a
// shallow V, deepest under the wheel: zb(y) below is the back surface, zs(y) the seam (the plates'
// inner face = the shell walls' edge). z = 0 is where v6's flat back was (and is the back at y = L).
// Values marked [CHECK] want calipers on the real part.

// ---------- form ----------
W        = 52;       // 46 mm battery + 0.6 a side + 2.4 walls
wall     = 2.4;      // side walls (6 lines at 0.4)
tip_wall = 2.4;
end_wall = 2.4;
T        = 16.6;     // 2.0 floor + battery + button board stack + 2.0 face (15.8 in v5 with 1.6 floor and face)
tip_r    = 3.5;  corner_r = 9;
clr      = 0.3;
theta    = 0;        // v7 is straight (kept for the fit check, which shares v6's component models)
// cross-section: lower ellipse into a flat back, straight band, upper roll (5 mm tall, as v5)
ea = 3.0;  eb = 7.0;  bed_ch = 1.0;  foot_k = 0.7;   // bed foot: 35 deg, so the plates stay under 45 when tilted flat
roll_z = T - 5.0;  roll = 2.2;
land = 0;  pan_t = 2.0;  pcl = 0.15;   // v6: the panels are full-width caps (the top 2.0 of the shell), so the body's
                                       // opening is the full 47.2 and the 46 mm battery goes in from the front
top_t = pan_t;       // v4 name for the face thickness (the cap system uses it)
floor_t = 2.0;       // back thickness, solid under the battery
min_wall = 2.4;  min_panel = 2.0;  min_land = 3.0;  min_skin = 1.2;   // spec v6 section 3

// ---------- display board: LCDwiki E32R24P ----------
db_w = 42.89;  db_l = 74.33;  db_pcb = 1.6;
db_front = 3.84;  db_back = 4.63;
db_hole_off = 4.0;  db_hole_d = 3.2;
lcd_l = 60.0;  lcd_from_ant = 6.34;
aa_w = 36.2;  aa_l = 49.0;
aa_from_ant = 10.0;
win_m = 0.5;
win_w = aa_w + 2 * win_m;  win_l = aa_l + 2 * win_m;  win_r = 1.5;  win_cham = 1.0;
usb_x = 0.22;
usb_in = 1.0;
usb_body_h = 3.2;
usb_w = 12.7;  usb_h = 6.7;  usb_r = 2.0;
usb_flare = 45;
usb_floor = 1.85;
usb_skin = 0.6;
usb_hole = [9.6, 3.3, 1.4];
led_from_edge = 12.04;
led_from_usb  = 40.58;

// ---------- button board ----------
bb_w = 43.0;  bb_l = 112.0;  bb_pcb = 1.6;
sw_body = 3.5;  sw_total = 7.0;  smd_h = 0.8;  top_parts = 4.4;
batt = [46, 105, 5];
foam = 0.5;

// ---------- layout along y ----------
board_gap = 25.0;  bottom_zone = 9.0;   // the O18.6 wheel + 0.5 all round, between two 2.0 cross walls with 0.2 to spare (24 in v6, where the bend gave the room)
ir_x = 12;
ir_wire = [9.0, 2.0, 1.0];          // groove: y start, width, depth (1.4 of the 2.4 wall left)
ir_skin = 1.4;                      // tip skin in front of each IR LED (it thins to ~1.0 under the top roll)

// ---------- buttons (button-board coordinates, from board.py) ----------
dpad_c = [21.5, 25.5];
dpad_sw = 13.0;
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
cap_d = 8.6;  cap_hole = 9.8;  cap_proud = 3.0;  cap_flange = 0.8;  flange_x = 0.9;
// 0.6 a side round the caps (0.45 in v5 rubbed on the print, user 2026-11-05)
cap_top_cham = 0.6;
rib_w = 1.2;  rib_out = 1.0;  rib_clr = 0.25;  rib_skin = 0.6;  flange_clr = 0.35;
flange_d = cap_d + 2 * flange_x + 0.6;
grip_af = 3.4;
cap_rib_w = 1.0;
cap_rib_h = cap_flange + top_t - rib_skin - 0.45;
flange_shrink = 0.2;
ef = 0.3;
side_clr = 0.6;                      // D-pad / OK gap to the plate opening, per side (0.45 in v5)

// ---------- mic ----------
mic_b = [34.0, 7.0];
mic_mod = [15, 2.6];

// ---------- roller: Alps EC11E flat-shaft with switch (datasheet "EC11 Series" dimensions) ----------
// Lies on its side: shaft along -x. Turned so both pin rows run along z and sit 14.5 apart in y;
// the 11.7 side is vertical (z), the 12 side runs along y. The side tabs are snipped.
ec11_w = 11.7;  ec11_d = 12.0;      // body: across the pin rows (z here), along them (y here)
ec11_h = 4.5;                       // PCB seat to frame top
ec11_pin = 3.5;                     // terminals past the seat
ec11_bush = [7.0, 7.0];             // M7 x 0.75 bushing: d, length from the frame top
ec11_shaft = [6.0, 20.0, 4.5, 10.0]; // d, length from the frame top, across the flat, flat length
ec11_rows = [-7.5, 7.0];            // pin rows (A C B, D E) from the shaft axis, along y
ec11_pitch = 2.5;                   // A C B pitch (along z); D E are 5 apart
ec11_nut = [10.0, 2.0];             // M7 thin nut: across flats, thickness [CHECK: not on the drawing]
ec11_detent_steps = 4;
carrier = [1.6, 17.0, 14.3];        // perfboard behind the EC11: thickness (x), length (y), height (z): the collar floor (z 0) to its cap
bulk_t = 2.5;                       // bulkhead the bushing passes through (nut on the wheel side)
whl_d = 18.6;  whl_w = 9;  whl_proud = 1.2;
whl_x = -4;                         // wheel centre across; off centre so the EC11 + carrier stay inside the collar
ec11_gap = 0.2;  whl_gap = 0.5;     // clearance round the EC11 body; round the wheel
// x stations along the shaft (shaft points -x): frame top, bushing end, wheel faces
ec11_xf = whl_x + whl_w / 2 + 0.5 + ec11_bush[1];   // the bushing ends 0.5 short of the wheel's inner face
bush_end = ec11_xf - ec11_bush[1];

// ---------- fasteners, dock ----------
m2 = [1.9, 2.6, 4.2, 0.3];          // M2 self-tap hole (96 % of the thread; printed holes come out ~0.15 small; 1.7 in v6 was too
                                    // tight), clearance hole, countersink d at the surface, head recess below it
fit = 0.25;                         // sliding fit between printed parts, per side (0.15 in v6 stopped the joint closing)
lip_clr = 0.3;  lip_w = 1.8;  lip_h = 1.6;   // the back plates' locating lips inside the shell walls
// every back screw is an M2 countersunk (DIN 965 / ISO 7046 flat head, 90 deg), sunk 0.3 below the surface
module m2_csk(h) { cylinder(d = m2[1], h = h, $fn = 48); translate([0, 0, -0.01]) cylinder(d = m2[2], h = m2[3] + 0.01, $fn = 32);
  translate([0, 0, m2[3]]) cylinder(d1 = m2[2], d2 = m2[1], h = (m2[2] - m2[1]) / 2, $fn = 32); }
pad_insert = [4.0, 5.0];
// ---------- charging contacts: a swappable plate in the bottom end ----------
// The key body's end has a slot open to the top; a plate drops in (a T-rib on its back, in a T-slot,
// stops it falling out of the end face) and the key panel holds it down. Plate A: two brass-insert pads + two 10 x 2
// magnets. Plate B: a ready-made magnetic pogo connector (housing size [CHECK] on the part bought).
pp_w = 34.4;  pp_z0 = 2.0;  pp_t = 5.3;  pp_tee = [2.0, 2.0, 5.0, 1.4];   // plate width (inside the end's flat part), bottom z, thickness (y);
                                                           // T-rib on its back: stem w, stem depth, flange w, flange depth
conn_b = [14.0, 6.0, 5.0, 20.0, 1.7];  // plate B connector: housing w (x), h (z), depth (y), ear hole spacing, ear screw hole [CHECK]
magnet = [10, 2];
pogo_d = 1.0;  pogo_l = 15.85;

// ---------- derived ----------
in_w  = W - 2 * wall;
db_y0 = tip_wall + clr;
db_end = db_y0 + db_l;
bb_y0 = db_end + board_gap;
L = bb_y0 + bb_l + bottom_zone + end_wall;
front_in = T - pan_t;
touch_z  = front_in - 0.3;
db_top = touch_z - db_front;  db_z0 = db_top - db_pcb;
batt_foam = 0.2;
batt_z0 = floor_t + batt_foam;
bb_z0  = floor_t + foam + batt[2] + smd_h;  bb_top = bb_z0 + bb_pcb;
act_top = bb_top + sw_total;
pz0 = T - pan_t;
axle_z = T + whl_proud - whl_d / 2;
y_head_end = db_end + 0.5;          // the wheel zone starts here (0.5 past the display board)
y_key_start = bb_y0 - 0.5;          // and ends here (0.5 before the button board)
cy = (y_head_end + y_key_start) / 2;   // wheel axle y
batt_y0 = bb_y0 + 6.5;             // 7 mm clear under the board's start: every wire to and from the collar crosses there
aa_c   = db_y0 + db_l - aa_from_ant - aa_l / 2;
win_y0 = aa_c - win_l / 2;
holes = [for (sx = [-1, 1], sy = [0, 1]) [sx * (db_w / 2 - db_hole_off), db_y0 + db_hole_off + sy * (db_l - 2 * db_hole_off)]];
ir_z = db_top + 2.0;                // IR LEDs over the display PCB at the tip: the 3.8 flange clears the board by 0.1 (v6 tilted them with the bend)
function bpos(b) = [bb_w / 2 - b[0], bb_y0 + b[1]];
dc = bpos(dpad_c);

// wheel zone: two solid cheeks (|x| >= room_x) and two cross walls stand on the face's inside
room_x = 15.7;                      // the wheel room's half-width
col_wall = 2.0;                     // cross walls
whl_well = axle_z - whl_d / 2 - whl_gap;          // bottom of the wheel's room

// ---------- the keel: back surface zb(y), seam zs(y) ----------
back_t = 2.0;                       // back plates
zb_tip = 1.0;                       // back at the tip (thickness there T - zb_tip = 15.6)
y_ap = y_key_start;                 // keel line: the two plates meet here, on the key-side cross wall
z_ap = -3.9;                        // back at the keel (thickness 20.5)
kh = (z_ap - zb_tip) / y_ap;        // slopes (dz/dy) of the head plate and the key plate
kk = -z_ap / (L - y_ap);
function zb(y) = y <= y_ap ? zb_tip + kh * y : z_ap + kk * (y - y_ap);
function zs(y) = zb(y) + back_t;
z_seat = 1.5;                       // the 4 display screws' heads sit here, so all four are the same M2 x 12
ec11_top = axle_z + ec11_w / 2;

assert(in_w / 2 - batt[0] / 2 >= 0.5, "battery side clearance");
assert(batt_y0 + batt[1] <= bb_y0 + bb_l, "battery under the button board");
assert(bb_top + max(sw_body, top_parts) + 0.3 <= front_in, "button board parts hit the face panel");
assert(db_z0 - db_back >= zs(db_y0) + 0.3, "display back parts hit the head plate");
assert(zs(batt_y0 + batt[1]) <= floor_t && batt_z0 >= floor_t, "battery seat above the key plate");
assert(whl_well - zb(cy) >= min_panel, "back skin under the wheel >= 2.0");
assert(T - ec11_top - ec11_gap >= min_panel, "collar skin over the EC11 >= 2.0");
assert(bush_end >= whl_x + whl_w / 2 + 0.5 - 1e-6, "bushing end clears the wheel's inner face by 0.5");
assert(ec11_xf - ec11_shaft[1] <= whl_x - whl_w / 2 + 0.01, "shaft reaches through the wheel");
assert(ec11_xf + ec11_h + carrier[0] + 1.0 <= room_x, "EC11, carrier and pin stubs inside the wheel room");
assert(whl_x - whl_d / 2 >= -50 && whl_x - whl_w / 2 - whl_gap >= -room_x + 4.0, "4 mm wire channel beside the wheel");
assert(y_key_start - col_wall - (cy + whl_d / 2 + whl_gap) >= 0.2, "wheel room inside the collar");
assert(carrier[1] <= (y_key_start - y_head_end) - 2 * col_wall - 1.0, "carrier fits between the collar end walls");
assert(axle_z - ec11_w / 2 >= zs(cy) + 0.3, "EC11 clears the head plate");
assert(carrier[2] <= T - min_panel - 0.2, "carrier spans floor to cap");
