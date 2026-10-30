// ESP32-32E 2.4" universal remote - parametric case, v3
// Front shell + sculpted back plate + ring D-pad caps.
// Units: mm. Origin: centre of the tip, z = 0 at the back edge plane, front face at z = T.
// +y runs from the tip (USB-C, IR, mic) towards the bottom; +x is the user's LEFT
// when holding it face-up with the tip pointing away.
//
// Print orientation (no supports anywhere; exported this way):
//   shell.stl  front face DOWN       back.stl  inner (flat) face DOWN
//   caps.stl   flange DOWN
// Every downward surface is a 45 deg chamfer or a short flat bridge.
//
// Render:  openscad -D 'part="shell"' -o shell.stl remote_case.scad   (shell | back | caps)
// Values marked [CHECK] are measured from LCDwiki's board renders; confirm with calipers.

part = "assembly";
$fn = 96;

// ---------- form ----------
T        = 16.8;     // shell depth (back edge to front face)
wall     = 2.2;
skin     = 1.2;      // wall left beside the back plate
top_t    = 1.6;
plate_t  = 1.6;
corner_r = 9;        // bottom corners in plan
tip_b    = 8;        // how far the curved tip bulges
bevel    = 2.0;      // 45 deg bevel round the front face
back_ch  = 0.8;      // chamfer on the shell's back edge
clr      = 0.3;
swell_d  = 4.0;      // palm swell depth on the back plate
groove_d = 1.2;      // index-finger groove depth

// ---------- display board: LCDwiki E32R24P ----------
db_w = 42.89;  db_l = 74.33;  db_pcb = 1.6;
db_front = 3.84;  db_back = 4.63;
db_hole_off = 4.0;  db_hole_d = 3.2;
lcd_l = 60.0;  lcd_from_ant = 6.34;   // LCD backlight outline, from the antenna end (drawing)
win_w = 38.6;  win_l = 51.0;  win_r = 2.0;  win_cham = 1.0;
usb_w = 9.2;  usb_h = 3.6;          // receptacle opening (USB-C on the back)
usb_x = -0.33;                      // drawing: 21.78 mm from one edge = 0.33 off centre
plug_w = 12.8; plug_h = 7.0;        // recess for the cable's plug body
led_from_edge = 12.0;               // RGB LED: from the board's long edge [CHECK]
led_from_usb  = 40.7;               //          from the USB-C end      [CHECK]

// ---------- button board ----------
bb_w = 43.0;  bb_l = 96.0;  bb_pcb = 1.6;
sw_body = 3.5;  sw_total = 7.0;  smd_h = 0.8;  top_parts = 4.4;
batt = [34, 50, 6];
foam = 0.5;

// ---------- layout along y ----------
tip_zone = 3.0;  board_gap = 6.0;  bottom_zone = 9.0;   // tip_zone clears the USB-C overhang (2.7 on the drawing)

// ---------- buttons (button-board coordinates, from board.py) ----------
dpad_c = [21.5, 25.5];              // OK switch; the ring's centre
dpad_sw = 13.0;                     // arrow switches sit 13 mm from it
ring_in = 6.3;  ring_out = 17.5;  ring_web = 2.2;  ok_d = 10.0;
singles = [  // [x, y, name, mark]
  [ 7.5,  6.0, "POWER", 6],
  [ 8.5, 50.0, "BACK",  8],
  [21.5, 50.0, "HOME",  9],
  [34.5, 50.0, "VOICE", 7],
];
cap_d = 8.6;  cap_hole = 9.2;  cap_proud = 2.0;  cap_flange = 0.8;  flange_x = 0.6;
stem_d = 3.8;  cap_top_cham = 0.6;

// ---------- mic (INMP441 module glued under the tip, above the screen) ----------
mic_y = 4.5;                        // from the display board's USB-end edge

// ---------- derived ----------
in_w  = max(db_w, bb_w) + 2 * clr;
out_w = in_w + 2 * wall;
db_y0 = tip_b + tip_zone;            // board starts where the tip curve reaches full width
bb_y0 = db_y0 + db_l + board_gap;
out_l = bb_y0 + bb_l + bottom_zone + wall;

front_in = T - top_t;
touch_z  = front_in - 0.3;
db_top = touch_z - db_front;  db_z0 = db_top - db_pcb;
batt_z0 = plate_t + foam;
bb_z0  = batt_z0 + batt[2] + smd_h;  bb_top = bb_z0 + bb_pcb;
act_top = bb_top + sw_total;
assert(bb_top + max(sw_body, top_parts) + 0.3 <= front_in, "button board parts hit the front");
assert(db_z0 - db_back >= plate_t + 0.3, "display back parts hit the back plate");

lcd_c  = db_y0 + db_l - lcd_from_ant - lcd_l / 2;   // USB end faces the tip
win_y0 = lcd_c - win_l / 2;
holes = [for (sx = [-1, 1], sy = [0, 1]) [sx * (db_w / 2 - db_hole_off), db_y0 + db_hole_off + sy * (db_l - 2 * db_hole_off)]];
plate_screws = [for (sx = [-1, 1]) for (y = [bb_y0 - board_gap / 2, out_l - wall - bottom_zone / 2]) [sx * (in_w / 2 - 3.6), y]];
led = [db_w / 2 - led_from_edge, db_y0 + led_from_usb];
function bpos(b) = [bb_w / 2 - b[0], bb_y0 + b[1]];
dc = bpos(dpad_c);

// ---------- plan shapes ----------
module base2d() {
  hull() {
    translate([0, tip_b]) scale([1, tip_b / (out_w / 2)]) circle(r = out_w / 2, $fn = 192);
    translate([-out_w / 2, tip_b]) square([out_w, 1]);
    for (sx = [-1, 1]) translate([sx * (out_w / 2 - corner_r), out_l - corner_r]) circle(r = corner_r);
  }
}
module plan(inset = 0) { if (inset == 0) base2d(); else offset(r = -inset) base2d(); }

// ---------- shell ----------
module shell_outer() {
  hull() {
    translate([0, 0, back_ch]) linear_extrude(T - bevel - back_ch) plan(0);
    linear_extrude(0.01) plan(back_ch);
    translate([0, 0, T - 0.01]) linear_extrude(0.01) plan(bevel);
  }
}
module shell_body() {
  difference() {
    shell_outer();
    translate([0, 0, -1]) linear_extrude(plate_t + 1) plan(skin);         // plate seat
    translate([0, 0, plate_t - 0.01]) linear_extrude(front_in - plate_t + 0.01) plan(wall);
  }
}

// D-pad ring opening, split into four sectors by diagonal webs
module ring2d(grow = 0) {
  difference() {
    circle(r = ring_out + grow, $fn = 192);
    circle(r = ring_in - grow, $fn = 128);
    for (a = [45 : 90 : 315]) rotate(a) translate([0, -(ring_web / 2 - grow)]) square([ring_out + 5, ring_web - 2 * grow]);
  }
}
module sector2d(i, grow = 0) {       // i: 0 left(+x), 1 down(+y), 2 right(-x), 3 up(-y)
  intersection() {
    ring2d(grow);
    rotate(i * 90) polygon([[0, 0], [40, -40], [40, 40]]);
  }
}
module rr2d(w, l, r) { offset(r = r) square([w - 2 * r, l - 2 * r], center = true); }

module shell_cuts() {
  // screen window + 45 deg bezel
  translate([0, win_y0 + win_l / 2, front_in - 0.5]) linear_extrude(top_t + 1) rr2d(win_w, win_l, win_r);
  translate([0, win_y0 + win_l / 2, T - win_cham]) hull() {
    linear_extrude(0.01) rr2d(win_w, win_l, win_r);
    translate([0, 0, win_cham + 0.01]) linear_extrude(0.01) rr2d(win_w + 2 * win_cham, win_l + 2 * win_cham, win_r + win_cham);
  }
  // D-pad: ring sectors + OK
  translate(concat(dc, [front_in - 3])) {
    linear_extrude(top_t + 4) ring2d(0);
    cylinder(d = ok_d + 0.6, h = top_t + 4);
  }
  // single buttons, 0.4 mm edge chamfer
  for (b = singles) translate(concat(bpos(b), [front_in - 3])) {
    cylinder(d = cap_hole, h = 10);
    translate([0, 0, top_t + 3 - 0.4]) cylinder(d1 = cap_hole, d2 = cap_hole + 0.81, h = 0.41);
  }
  // accent groove circling the D-pad (prints as a 0.8 mm bridge)
  translate(concat(dc, [T - 0.5])) linear_extrude(1) difference() { circle(r = ring_out + 2.6, $fn = 192); circle(r = ring_out + 1.8, $fn = 192); }
  // mic grille: five short slots above the screen
  for (dx = [-3.2 : 1.6 : 3.2]) translate([dx, db_y0 + mic_y, front_in - 3]) hull() for (dy = [-1.4, 1.4]) translate([0, dy, 0]) cylinder(d = 0.9, h = top_t + 4, $fn = 16);
  // USB-C: receptacle opening plus a recess for the plug body
  uz = db_z0 - usb_h / 2 - 0.15;
  translate([usb_x, -1, uz]) rotate([-90, 0, 0]) linear_extrude(tip_b + 2) rr2d(usb_w, usb_h, 1.2);
  translate([usb_x, -1, uz]) rotate([-90, 0, 0]) linear_extrude(tip_b + 1 - 1.2) rr2d(plug_w, plug_h, 2);
  // IR LEDs (3 mm) through the tip, teardrop-shaped so they print clean
  for (sx = [-1, 1]) translate([sx * 10, -1, (db_top + front_in) / 2]) rotate([-90, 0, 0])
    linear_extrude(tip_b + 3) hull() { circle(d = 3.15, $fn = 32); translate([0, 3.15 / 2 * 1.414]) square(0.01, center = true); }
  // RGB LED light pipe (clear 1.75 mm filament) through the left wall
  translate([out_w / 2 + 1, led[1], db_z0 - 1.2]) rotate([0, -90, 0])
    linear_extrude(wall + 4) hull() { circle(d = 1.9, $fn = 24); translate([-1.9 / 2 * 1.414, 0]) square(0.01, center = true); }
}

module shell_features() {
  // display board posts (M2.5 x 6 self-tapping from the board's back)
  for (h = holes) translate([h[0], h[1], db_top + 0.05]) difference() {
    cylinder(d = h[1] > db_y0 + db_l / 2 ? 4.4 : 4.8, h = front_in - db_top);
    translate([0, 0, -1]) cylinder(d = 2.1, h = front_in - db_top - 0.4);
  }
  // back-plate screw posts (M2.5 self-tapping)
  for (p = plate_screws) translate([p[0], p[1], plate_t + 0.2]) difference() {
    cylinder(d = 5.0, h = front_in - plate_t - 0.2 + 0.05);
    translate([0, 0, -1]) cylinder(d = 2.1, h = 9);
  }
  // ribs pressing the button board's long edges
  for (sx = [-1, 1]) translate([sx * (in_w / 2 - 0.75) - 0.75, bb_y0 + 6, bb_top + 0.05]) cube([1.5, bb_l - 12, front_in - bb_top]);
  // end stops for the button board (hang past its edges)
  for (y = [bb_y0 - 1.6, bb_y0 + bb_l + 0.1]) for (sx = [-1, 1])
    translate([sx * 12 - 4, y, bb_z0 + 0.5]) cube([8, 1.5, front_in - bb_z0 - 0.45]);
  // guide collars under the caps
  translate(concat(dc, [front_in - 2])) linear_extrude(2.05) {
    difference() { ring2d(1.0); ring2d(0); }
    difference() { circle(d = ok_d + 0.6 + 2.4); circle(d = ok_d + 0.6); }
  }
  for (b = singles) translate(concat(bpos(b), [front_in - 2])) difference() {
    cylinder(d = cap_hole + 2.4, h = 2.05);
    translate([0, 0, -1]) cylinder(d = cap_hole, h = 5);
  }
  // mic module cradle (foam-gasket ring round the grille)
  translate([0, db_y0 + mic_y, front_in - 1.2]) difference() { cylinder(d = 9.5, h = 1.25); translate([0, 0, -1]) cylinder(d = 7.5, h = 5); }
  // light-pipe guide tube from the wall towards the LED
  translate([in_w / 2 + 0.05, led[1], db_z0 - 1.2]) rotate([0, -90, 0]) linear_extrude(3) difference() {
    // keel points to the front (print-down) so the tube's underside is 45 deg
    hull() { circle(d = 3.6, $fn = 32); translate([3.6 / 2 * 1.414, 0]) square(0.01, center = true); }
    hull() { circle(d = 1.9, $fn = 24); translate([-1.9 / 2 * 1.414, 0]) square(0.01, center = true); }
  }
}

module shell() {
  difference() {
    union() {
      shell_body();
      tip_lip();
      intersection() { translate([0, 0, plate_t]) linear_extrude(T) plan(wall - 0.01); shell_features(); }
    }
    shell_cuts();
  }
}

// tip dovetail: the plate's tip edge tucks under a 45 deg lip, so only the
// four screws further down are needed and the tip can't lift
dt = 0.8;                                    // dovetail depth
tip_region_y = db_y0 - 1;
module tip_region() { translate([-100, -50, -20]) cube([200, 50 + tip_region_y, 50]); }
module tip_frustum(c) {                      // inner boundary of the lip, grown by c
  hull() {
    translate([0, 0, -0.01]) linear_extrude(0.01) plan(skin + 0.15 + dt - c);
    translate([0, 0, dt]) linear_extrude(0.01) plan(skin + 0.15 - c);
  }
}
module tip_lip() {
  intersection() {
    tip_region();
    difference() { linear_extrude(dt) plan(back_ch); tip_frustum(0); }
  }
}

// ---------- back plate ----------
module back() {
  pw = in_w + 2 * (wall - skin) - 0.3;
  difference() {
    union() {
      linear_extrude(plate_t) plan(skin + 0.15);
      // palm swell: hull of the plate edge and a flattened ellipsoid under the grip
      intersection() {
        hull() {
          linear_extrude(0.01) plan(skin + 0.15 + 1.2);
          translate([0, bb_y0 + 40, 0]) scale([pw / 2 - 5, 62, swell_d]) sphere(1, $fn = 96);
        }
        translate([-100, -1, -swell_d - 1]) cube([200, out_l + 2, swell_d + 1]);
      }
    }
    // tip edge chamfered to slide under the shell's lip (0.15 mm clearance)
    intersection() {
      tip_region();
      difference() { translate([0, 0, -swell_d - 1]) linear_extrude(swell_d + 1 + dt + 0.01) plan(0); tip_frustum(0.15); translate([0, 0, dt]) linear_extrude(5) plan(0); }
    }
    // index-finger rest across the swell, behind the D-pad
    translate([0, dc[1] + 4, -swell_d - 40 + groove_d]) rotate([0, 90, 0]) cylinder(r = 40, h = 100, center = true, $fn = 256);
    // screw holes; 45 deg countersink opens on the outer side
    for (p = plate_screws) translate([p[0], p[1], 0]) {
      translate([0, 0, -swell_d - 1]) cylinder(d = 2.8, h = 20);
      translate([0, 0, -swell_d - 1]) cylinder(d = 5.4, h = swell_d + 1);
      cylinder(d1 = 5.4, d2 = 2.8, h = 1.3);
    }
  }
}

// ---------- caps ----------
cap_h = (T + cap_proud) - (front_in - cap_flange);
sock  = act_top - (front_in - cap_flange);
module ring_cap(i) {
  difference() {
    union() {
      linear_extrude(cap_flange) offset(r = flange_x) offset(r = -0.3) sector2d(i);
      linear_extrude(cap_h - cap_top_cham) offset(r = -0.3) sector2d(i);
      translate([0, 0, cap_h - cap_top_cham]) hull() {
        linear_extrude(0.01) offset(r = -0.3) sector2d(i);
        translate([0, 0, cap_top_cham - 0.01]) linear_extrude(0.01) offset(r = -0.3 - cap_top_cham) sector2d(i);
      }
    }
    rotate(i * 90) {
      translate([dpad_sw, 0, -1]) cylinder(d = stem_d, h = 1 + sock);
      translate([dpad_sw - 0.5, 0, cap_h - 0.4]) linear_extrude(1) polygon([[-1.2, -2.0], [-1.2, 2.0], [1.4, 0]]);
    }
  }
}
module round_cap(d, m) {
  difference() {
    union() {
      cylinder(d = d + 2 * flange_x + 0.6, h = cap_flange);
      cylinder(d = d, h = cap_h - cap_top_cham);
      translate([0, 0, cap_h - cap_top_cham]) cylinder(d1 = d, d2 = d - 2 * cap_top_cham, h = cap_top_cham);
    }
    translate([0, 0, -1]) cylinder(d = stem_d, h = 1 + sock);
    translate([0, 0, cap_h - 0.4]) linear_extrude(1) mark(m);
  }
}
module mark(m) {
  if (m == 5) difference() { circle(d = 5.4); circle(d = 4.0); }
  if (m == 6) { difference() { circle(d = 5); circle(d = 3.6); translate([-0.9, -3]) square([1.8, 3]); } translate([-0.45, -3]) square([0.9, 2.8]); }
  if (m == 7) { translate([0, -0.6]) offset(r = 0.9) square([0.01, 1.8], center = true); translate([-0.3, 1.0]) square([0.6, 1.2]); }
  if (m == 8) polygon([[-1.0, -2.0], [-1.0, 2.0], [1.6, 0]]);
  if (m == 9) polygon([[0, -2.2], [2.2, 0], [1.4, 0], [1.4, 1.9], [-1.4, 1.9], [-1.4, 0], [-2.2, 0]]);
}
module caps_plate() {
  for (i = [0 : 3]) translate([i * 22 - 33, 0, 0]) translate([-dpad_sw * cos(i * 90), -dpad_sw * sin(i * 90), 0]) ring_cap(i);
  translate([-33, 24, 0]) round_cap(ok_d, 5);
  for (k = [0 : 3]) translate([-18 + k * 13, 24, 0]) round_cap(cap_d, singles[k][3]);
}

// ---------- output ----------
if (part == "shell") translate([0, 0, T]) mirror([0, 0, 1]) shell();
else if (part == "back") translate([0, 0, plate_t]) mirror([0, 0, 1]) back();
else if (part == "caps") caps_plate();
else {
  color("#e9e6df") shell();
  color("#3b4048") back();
  for (i = [0 : 3]) color("#2a2e35") translate(concat(dc, [front_in - cap_flange])) ring_cap(i);
  color("#d97a2b") translate(concat(dc, [front_in - cap_flange])) round_cap(ok_d, 5);
  for (b = singles) color(b[2] == "POWER" ? "#c94a3f" : "#2a2e35") translate(concat(bpos(b), [front_in - cap_flange])) round_cap(cap_d, b[3]);
}

echo(str("OUTER ", out_w, " x ", out_l, " x ", T, " (+", swell_d, " palm swell) mm"));
