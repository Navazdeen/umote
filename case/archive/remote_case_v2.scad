// ESP32-32E 2.4" universal remote - parametric case, v2 (support-free)
// Units: mm. Origin: centre of the tip end, back outer surface at z = 0.
// +y runs from the tip (IR LEDs, USB-C) towards the bottom of the remote.
//
// Print orientation (no supports anywhere):
//   cover.stl  front face DOWN on the bed (exported that way)
//   tub.stl    floor DOWN on the bed
//   caps.stl   flange DOWN on the bed
// Every overhang is <= 45 deg or a short flat bridge; bed edges are chamfered.
//
// Render:  openscad -D 'part="tub"' -o tub.stl remote_case.scad   (tub | cover | caps)
// Values marked [CHECK] are best guesses; measure your board and adjust.

part = "assembly";   // tub | cover | caps | assembly
$fn = 96;

// ---------- shell ----------
T        = 17.4;     // overall thickness
wall     = 2.2;
floor_t  = 1.6;
top_t    = 1.6;
corner_r = 8;        // plan-view corner radius
cham     = 1.0;      // 45 deg chamfer on front and back perimeter
clr      = 0.3;      // board-to-wall clearance
split_z  = 6.0;      // parting line (tub below, cover above)
lip_h    = 1.4;  lip_t = 0.9;  lip_clr = 0.15;   // locating lip on the tub
reveal   = 0.4;      // V-groove along the parting line

// ---------- display board: LCDwiki E32R24P (ESP32-32E 2.4") ----------
db_w = 42.89;  db_l = 74.33;  db_pcb = 1.6;
db_front = 3.84;               // LCD + touch above the PCB
db_back  = 4.63;               // tallest part on the back
db_hole_off = 4.0;             // hole centres from each edge [CHECK]
db_hole_d   = 3.2;
lcd_l   = 60.0;
lcd_gap = 1.0;                 // LCD to the board edge away from USB-C [CHECK]
win_w = 38.6;  win_l = 51.0;  win_r = 2.0;  win_cham = 1.0;
win_shift = 0.0;               // nudge the window along y [CHECK]
usb_x = 0;                     // USB-C centre across the board [CHECK]
usb_w = 9.6;   usb_h = 3.8;
usb_on_back = true;            // receptacle on the back of the PCB [CHECK]

// ---------- button board (one-sided, 1.6 mm) ----------
bb_w = 43.0;  bb_l = 96.0;  bb_pcb = 1.6;
sw_body  = 3.5;                // 6x6 switch body
sw_total = 7.0;                // 6x6x7 switch: PCB to actuator top
smd_h    = 0.8;
top_parts = 4.4;               // DIP-28 soldered flat, no socket

// ---------- battery (LiPo pouch) ----------
batt = [34, 50, 6];            // 603450 ~1100 mAh

// ---------- layout along y ----------
tip_zone    = 2.0;
board_gap   = 3.0;
bottom_zone = 9.0;

// ---------- buttons (button-board coordinates, from board.py) ----------
// [x, y, name, mark]  mark: 0 none, 1 up, 2 left/back, 3 right, 4 down, 5 OK ring, 6 power, 7 mic
buttons = [
  [ 7.5,  6.0, "POWER", 6],
  [21.5, 12.5, "UP",    1],
  [ 8.5, 25.5, "LEFT",  2],
  [21.5, 25.5, "OK",    5],
  [34.5, 25.5, "RIGHT", 3],
  [21.5, 38.5, "DOWN",  4],
  [ 8.5, 50.0, "BACK",  2],
  [21.5, 50.0, "HOME",  0],
  [34.5, 50.0, "VOICE", 7],
];
// INMP441 module on the button board's J4 header; port centre in board coordinates [CHECK]
mic_pos = [32.4, 9.0];
cap_d = 8.6;  cap_hole = 9.2;  cap_proud = 2.0;
cap_flange = 0.8;  flange_extra = 1.0;
stem_d = 3.8;
cap_top_cham = 0.6;

// ---------- derived ----------
in_w  = max(db_w, bb_w) + 2 * clr;
out_w = in_w + 2 * wall;
db_y0 = wall + tip_zone;
bb_y0 = db_y0 + db_l + board_gap;
in_l  = tip_zone + db_l + board_gap + bb_l + bottom_zone;
out_l = in_l + 2 * wall;

front_in = T - top_t;
touch_z  = front_in - 0.3;          // gap so the bezel never presses the resistive panel
db_top   = touch_z - db_front;
db_z0    = db_top - db_pcb;

bb_z0  = floor_t + batt[2] + 1.0 + smd_h;
bb_top = bb_z0 + bb_pcb;
act_top = bb_top + sw_total;
assert(bb_top + max(sw_body, top_parts) + 0.3 <= front_in, "parts hit the front: raise T");
assert(db_z0 - db_back >= floor_t + 0.3, "display back parts hit the floor");

lcd_y0 = db_y0 + db_l - lcd_gap - lcd_l;
win_y0 = lcd_y0 + (lcd_l - win_l) / 2 + win_shift;

holes = [for (sx = [-1, 1], sy = [0, 1])
           [sx * (db_w / 2 - db_hole_off), db_y0 + db_hole_off + sy * (db_l - 2 * db_hole_off), sy]];
bot_bosses = [for (sx = [-1, 1]) [sx * (in_w / 2 - 5.0), out_l - wall - bottom_zone / 2]];

// viewed from the front with the tip up, +x is the user's LEFT, so board x is mirrored
function bpos(b) = [bb_w / 2 - b[0], bb_y0 + b[1]];

// ---------- 2D helpers ----------
module rrect(w, l, r) {        // rounded rectangle, y from 0 to l, centred in x
  translate([0, l / 2]) offset(r = r) square([w - 2 * r, l - 2 * r], center = true);
}
module plan(inset = 0) { translate([0, inset]) rrect(out_w - 2 * inset, out_l - 2 * inset, max(0.5, corner_r - inset)); }

// outer solid: straight walls with 45 deg chamfers on the front and back perimeter
module outer() {
  hull() {
    linear_extrude(0.01) plan(cham);
    translate([0, 0, cham]) linear_extrude(T - 2 * cham) plan(0);
    translate([0, 0, T - 0.01]) linear_extrude(0.01) plan(cham);
  }
}
module cavity() { translate([0, 0, floor_t]) linear_extrude(T - floor_t - top_t) plan(wall); }

// ---------- openings ----------
module flat_slot(w, h, depth) {   // stadium with flat long sides: prints as a bridge
  hull() for (dx = [-(w - h) / 2, (w - h) / 2]) translate([dx, 0, 0]) cylinder(d = h, h = depth, $fn = 32);
}
module screw_hole(h) {            // M2.5 clearance with a 45 deg tapered counterbore (no overhang)
  translate([0, 0, -1]) cylinder(d = 2.8, h = h + 1);
  translate([0, 0, -1]) cylinder(d = 5.4, h = 1 + 1.4);
  translate([0, 0, 1.4]) cylinder(d1 = 5.4, d2 = 2.8, h = 1.3);
}

module cutouts() {
  // screen window with a 45 deg bezel chamfer at the front face
  translate([0, win_y0, front_in - 0.5]) linear_extrude(top_t + 1) rrect(win_w, win_l, win_r);
  translate([0, win_y0, T - win_cham])
    hull() {
      linear_extrude(0.01) rrect(win_w, win_l, win_r);
      translate([0, -win_cham, win_cham + 0.01]) linear_extrude(0.01) rrect(win_w + 2 * win_cham, win_l + 2 * win_cham, win_r + win_cham);
    }
  // button holes, 0.4 mm chamfer at the front face
  for (b = buttons) translate(concat(bpos(b), [front_in - 1])) {
    cylinder(d = cap_hole, h = 10);
    translate([0, 0, top_t + 1 - 0.4]) cylinder(d1 = cap_hole, d2 = cap_hole + 0.8 + 0.01, h = 0.41);
  }
  // USB-C opening in the tip wall
  uz = usb_on_back ? db_z0 - usb_h / 2 - 0.1 : db_top + usb_h / 2 + 0.1;
  translate([usb_x, -1, uz]) rotate([-90, 0, 0]) flat_slot(usb_w, usb_h, wall + 2);
  // two 3 mm IR LEDs in the tip wall, between the display board and the front
  for (sx = [-1, 1]) translate([sx * 14, -1, (db_top + front_in) / 2]) rotate([-90, 0, 0])
    linear_extrude(wall + 2) hull() { circle(d = 3.15, $fn = 32); translate([0, 3.15 / 2 * 1.414]) square(0.01, center = true); }
  // microphone port above the INMP441 module
  for (dx = [-1.6, 0, 1.6]) translate(concat(bpos(mic_pos) + [dx, 0], [front_in - 1])) cylinder(d = 1.0, h = top_t + 2, $fn = 16);
  // closing screws from the back
  for (h = holes) if (h[2] == 0) translate([h[0], h[1], 0]) screw_hole(db_z0);
  for (p = bot_bosses) translate([p[0], p[1], 0]) screw_hole(split_z + lip_h);
  // reveal: small V-groove along the parting line
  translate([0, 0, split_z]) difference() {
    translate([0, 0, -reveal]) linear_extrude(2 * reveal) plan(-1);
    hull() {
      translate([0, 0, -reveal]) linear_extrude(0.01) plan(0);
      linear_extrude(0.01) plan(reveal);
      translate([0, 0, reveal - 0.01]) linear_extrude(0.01) plan(0);
    }
  }
}

// ---------- internal features ----------
module tub_features() {
  // display board standoffs: pins at the LCD end, screws at the USB end
  for (h = holes) translate([h[0], h[1], 0]) {
    cylinder(d = 6, h = db_z0);
    if (h[2] == 1) {
      cylinder(d = db_hole_d - 0.3, h = db_z0 + db_pcb - 0.2);
      translate([0, 0, db_z0 + db_pcb - 0.2]) cylinder(d1 = db_hole_d - 0.3, d2 = 1.6, h = 0.6);   // lead-in
    }
  }
  // ledges under the button board edges (battery sits between them)
  for (sx = [-1, 1]) translate([sx * (in_w / 2 - 0.75) - 0.75, bb_y0, 0]) cube([1.5, bb_l, bb_z0]);
  // closing screw bosses
  for (p = bot_bosses) translate([p[0], p[1], 0]) cylinder(d = 6.5, h = split_z + lip_h);
  // battery end stops
  for (yy = [bb_y0 + 8 - 1.2, bb_y0 + 8 + batt[1] + 0.6]) translate([-batt[0] / 2, yy, 0]) cube([batt[0], 1.2, 3]);
  // locating lip: stands on the inner half of the tub wall and rises into the cover
  translate([0, 0, split_z - 0.01]) linear_extrude(lip_h) difference() { plan(wall - lip_t); plan(wall); }
}

module cover_features() {
  // posts onto the display board's USB-end holes (blind pilot for M2.5 self-tapping)
  for (h = holes) if (h[2] == 0) translate([h[0], h[1], db_top + 0.05]) difference() {
    cylinder(d = 5.5, h = front_in - db_top);
    translate([0, 0, -1]) cylinder(d = 2.1, h = front_in - db_top);
  }
  // ribs pressing the button board edges onto the ledges
  for (sx = [-1, 1]) translate([sx * (in_w / 2 - 0.75) - 0.75, bb_y0 + 4, bb_top + 0.05]) cube([1.5, bb_l - 8, front_in - bb_top]);
  // closing screw posts
  for (p = bot_bosses) translate([p[0], p[1], split_z + lip_h + lip_clr]) difference() {
    cylinder(d = 6.5, h = front_in - split_z - lip_h - lip_clr + 0.05);   // fuse into the roof
    translate([0, 0, -1]) cylinder(d = 2.1, h = front_in - split_z - lip_h - 1);
  }
  // foam-gasket ring round the mic port (seals the module to the port)
  translate(concat(bpos(mic_pos), [front_in - 1.2])) difference() { cylinder(d = 8, h = 1.25); translate([0, 0, -1]) cylinder(d = 6, h = 5); }
  // collars guide the caps
  for (b = buttons) translate(concat(bpos(b), [front_in - 2.0])) difference() {
    cylinder(d = cap_hole + 2.4, h = 2.05);
    translate([0, 0, -1]) cylinder(d = cap_hole, h = 5);
  }
}

module tub() {
  difference() {
    union() {
      intersection() { difference() { outer(); cavity(); }  translate([-100, -1, -1]) cube([200, out_l + 2, split_z + 1]); }
      intersection() { linear_extrude(T) plan(wall - 0.01); tub_features(); }
    }
    cutouts();
  }
}

module cover() {
  difference() {
    union() {
      intersection() { difference() { outer(); cavity(); } translate([-100, -1, split_z]) cube([200, out_l + 2, 50]); }
      intersection() { linear_extrude(T) plan(wall - 0.01); cover_features(); }
    }
    cutouts();
    // rebate that receives the tub's lip (open end of the print, so no overhang)
    translate([0, 0, split_z - 0.01]) linear_extrude(lip_h + lip_clr) plan(wall - lip_t - lip_clr);
  }
}

// ---------- caps ----------
module cap(m) {
  cap_h = (T + cap_proud) - (front_in - cap_flange);
  difference() {
    union() {
      cylinder(d = cap_hole + flange_extra * 2, h = cap_flange);
      cylinder(d = cap_d, h = cap_h - cap_top_cham);
      translate([0, 0, cap_h - cap_top_cham]) cylinder(d1 = cap_d, d2 = cap_d - 2 * cap_top_cham, h = cap_top_cham);
    }
    // actuator socket; its 3.8 mm flat roof is a short bridge, fine without support
    translate([0, 0, -1]) cylinder(d = stem_d, h = 1 + act_top - (front_in - cap_flange));
    translate([0, 0, cap_h - 0.4]) linear_extrude(1) mark(m);
  }
}
module mark(m) {
  // shapes read correctly with the tip up; +x is the user's left
  if (m == 1) polygon([[-2.0, 1.0], [2.0, 1.0], [0, -1.6]]);
  if (m == 4) polygon([[-2.0, -1.0], [2.0, -1.0], [0, 1.6]]);
  if (m == 2) polygon([[-1.0, -2.0], [-1.0, 2.0], [1.6, 0]]);
  if (m == 3) polygon([[1.0, -2.0], [1.0, 2.0], [-1.6, 0]]);
  if (m == 5) difference() { circle(d = 5.4); circle(d = 4.0); }
  if (m == 6) { difference() { circle(d = 5); circle(d = 3.6); translate([-0.9, -3]) square([1.8, 3]); } translate([-0.45, -3]) square([0.9, 2.8]); }
  if (m == 7) { translate([0, -0.6]) offset(r = 0.9) square([0.01, 1.8], center = true); translate([-0.3, 1.0]) square([0.6, 1.2]); }
}
module caps_plate() {
  for (i = [0 : len(buttons) - 1]) translate([(i % 5) * 13, floor(i / 5) * 13, 0]) cap(buttons[i][3]);
}

// ---------- output ----------
if (part == "tub") tub();
else if (part == "cover") translate([0, 0, T]) mirror([0, 0, 1]) cover();   // front face on the bed
else if (part == "caps") caps_plate();
else {
  color("#26292e") tub();
  color("#e9ebee") cover();
  for (b = buttons) color(b[2] == "POWER" ? "#d9534f" : b[2] == "OK" ? "#5b8def" : "#3a3f47")
    translate(concat(bpos(b), [front_in - cap_flange])) cap(b[3]);
}

echo(str("OUTER ", out_w, " x ", out_l, " x ", T, " mm | db_z0=", db_z0, " bb_z0=", bb_z0, " act_top=", act_top));
