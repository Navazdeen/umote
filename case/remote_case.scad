// ESP32-32E 2.4" universal remote - parametric case, v4
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
T        = 15.8;     // overall depth at the edges (back edge to front face)
wall     = 2.2;
top_t    = 1.6;
plate_t  = 1.6;
corner_r = 9;        // bottom corners in plan
tip_r    = 3.5;      // tip corners (small, so the USB-C end can be flat and flush)
bevel    = 2.5;      // 45 deg bevel round the front face
back_ch  = 3.0;      // 45 deg chamfer round the back; the back plate forms its lower part
                     // (3.0, not 3.5: the shell's back edge stays 0.8 mm thick over the straight cavity)
clr      = 0.3;
swell_d  = 3.0;      // palm swell depth on the back plate
groove_d = 1.0;      // index-finger rest depth

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
usb_x = 1.22;                       // +x is the BOOT side (shell.stl prints face down, so the viewer shows it
                                    // mirrored). The second print (-0.78) sat ~2 mm the wrong way (user)
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
batt = [34, 50, 5];                 // 503450, ~1000 mAh
foam = 0.5;

// ---------- layout along y ----------
board_gap = 6.0;  bottom_zone = 9.0;
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

// ---------- derived ----------
in_w  = max(db_w, bb_w) + 2 * clr;
out_w = in_w + 2 * wall;
db_y0 = wall + clr;                  // board edge against the tip wall (receptacle is inset, not overhanging)
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

aa_c   = db_y0 + db_l - aa_from_ant - aa_l / 2;                 // USB end faces the tip
win_y0 = aa_c - win_l / 2;
holes = [for (sx = [-1, 1], sy = [0, 1]) [sx * (db_w / 2 - db_hole_off), db_y0 + db_hole_off + sy * (db_l - 2 * db_hole_off)]];
// back plate screws: two at the tip go through printed spacers and the display's USB-end
// holes into the front posts; two between the boards; two at the bottom
mid_screws = [for (sx = [-1, 1]) for (y = [bb_y0 - board_gap / 2, out_l - wall - bottom_zone / 2]) [sx * 15.5, y]];
led = [db_w / 2 - led_from_edge, db_y0 + led_from_usb];
usb_holes = [for (h = holes) if (h[1] < db_y0 + db_l / 2) h];
plate_screws = concat(usb_holes, mid_screws);
ir_z = front_in - 1.9;               // IR LED centre: clear of the display PCB below
function bpos(b) = [bb_w / 2 - b[0], bb_y0 + b[1]];
dc = bpos(dpad_c);

// ---------- plan shapes ----------
module base2d() {
  hull() {
    for (sx = [-1, 1]) translate([sx * (out_w / 2 - tip_r), tip_r]) circle(r = tip_r);
    for (sx = [-1, 1]) translate([sx * (out_w / 2 - corner_r), out_l - corner_r]) circle(r = corner_r);
  }
}
module plan(inset = 0) { if (inset == 0) base2d(); else offset(r = -inset) base2d(); }

// ---------- shell ----------
module outer_all() {               // whole outer envelope (shell + plate edge)
  hull() {
    linear_extrude(0.01) plan(back_ch);
    translate([0, 0, back_ch]) linear_extrude(T - bevel - back_ch) plan(0);
    translate([0, 0, T - 0.01]) linear_extrude(0.01) plan(bevel);
  }
}
module cavity() {                  // straight walls down to the open back, so both boards (43 wide)
  // slide in from behind; the outer chamfer just thins the wall towards the back edge
  translate([0, 0, plate_t - 0.01]) linear_extrude(front_in - plate_t + 0.01) plan(wall);
}
module shell_body() {
  difference() {
    intersection() { outer_all(); translate([-100, -1, plate_t]) cube([200, out_l + 2, 50]); }
    cavity();
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
  // single buttons, 0.4 mm edge chamfer, and the key notch for the cap's rib
  for (b = singles) translate(concat(bpos(b), [front_in - 3])) {
    cylinder(d = cap_hole, h = 10);
    translate([-(rib_w + 2 * rib_clr) / 2, -(cap_d / 2 + rib_out + rib_clr), 0]) cube([rib_w + 2 * rib_clr, cap_d / 2, 3 + top_t - rib_skin]);
    translate([0, 0, top_t + 3 - 0.4]) cylinder(d1 = cap_hole, d2 = cap_hole + 0.81, h = 0.41);
  }
  // accent groove circling the D-pad (prints as a 0.8 mm bridge); it stops short of the
  // POWER hole, which sits closer to the ring than the groove's outer edge
  translate(concat(dc, [T - 0.5])) linear_extrude(1) difference() {
    circle(r = ring_out + 2.6, $fn = 192); circle(r = ring_out + 1.8, $fn = 192);
    translate(bpos(singles[0]) - dc) circle(d = cap_hole + 0.81 + 2.4);
  }
  // mic grille: five short slots over the module, top-right of the keys
  for (dx = [-1.6 : 1.6 : 1.6]) translate(concat(bpos(mic_b) + [dx, 0], [front_in - 3])) hull() for (dy = [-0.9, 0.9]) translate([0, dy, 0]) cylinder(d = 0.9, h = top_t + 4, $fn = 16);
  // USB-C: the receptacle sits behind the tip wall; the opening takes the plug's overmold.
  // Its edge (z 3.5) lands just above the back chamfer's crease.
  uz = db_z0 - usb_body_h / 2;
  // Trapezoid notch (top view): the wall steps in round the plug with angled sides. Its floor
  // is a thin skin with a receptacle-only hole, so nothing but the USB-C shows from outside.
  // A thick plug overmold stops on the floor, about 1.65 mm short of the receptacle face.
  ux = usb_floor * tan(usb_flare);
  translate([usb_x, 0, uz]) rotate([-90, 0, 0]) hull() {
    translate([0, 0, -1]) linear_extrude(1) rr2d(usb_w + 2 * ux, usb_h, usb_r);
    linear_extrude(usb_floor) rr2d(usb_w, usb_h, usb_r);
  }
  translate([usb_x, usb_floor - 0.5, db_z0 - usb_hole[1] / 2]) rotate([-90, 0, 0]) linear_extrude(usb_skin + 2) rr2d(usb_hole[0], usb_hole[1], usb_hole[2]);
  // IR LED wire groove (from below the display PCB up to the LED pocket); starts above the
  // back chamfer so the wall keeps at least 0.7 mm everywhere
  translate([-in_w / 2 - ir_wire[2], ir_wire[0], back_ch + 1]) cube([ir_wire[2] + 0.01, ir_wire[1], front_in - back_ch - 1.6]);
  // IR LEDs (3 mm) behind a thin skin of the tip wall, so they're hidden; teardrop-shaped
  // so the pocket roof prints clean. The LED dome seats against the skin.
  for (sx = [-1, 1]) translate([sx * ir_x, ir_skin > 0 ? ir_skin : -1, ir_z]) rotate([-90, 0, 0])
    linear_extrude(wall + 6) hull() { circle(d = 3.15, $fn = 32); translate([0, 3.15 / 2 * 1.414]) square(0.01, center = true); }
}

module shell_features() {
  // display board posts: LCD end M2.5 x 5 from the board's back; USB end takes the
  // long back-plate screws (M2.5 x 14) through a spacer and the board
  // USB floor skin past the wall's inner face (the hole is cut in shell_cuts)
  translate([usb_x, wall - 0.01, db_z0 - usb_body_h / 2]) rotate([-90, 0, 0])
    linear_extrude(usb_floor + usb_skin - wall + 0.01) rr2d(usb_w + 2, usb_h + 2, usb_r + 1);
  // the antenna-end posts are flattened on the LCD side: 0.4 mm clear of the glass
  lcd_end = db_y0 + db_l - lcd_from_ant;
  for (h = holes) translate([h[0], h[1], db_top + 0.05]) difference() {
    cylinder(d = h[1] > db_y0 + db_l / 2 ? 4.4 : 4.8, h = front_in - db_top);
    translate([0, 0, -1]) cylinder(d = 2.1, h = front_in - db_top - 0.4);
    if (h[1] > db_y0 + db_l / 2) translate([-5, lcd_end + 0.4 - h[1] - 10, -1]) cube([10, 10, 20]);
  }
  // IR LED clips: C-shaped saddles hanging from the front, open towards the board
  for (sx = [-1, 1]) translate([sx * ir_x, wall - 0.05, 0]) difference() {
    translate([-2.4, 0, ir_z - 0.6]) cube([4.8, 5.0, front_in - ir_z + 0.65]);
    translate([0, -1, ir_z]) rotate([-90, 0, 0]) cylinder(d = 3.1, h = 7, $fn = 32);
    translate([-1.3, -1, ir_z - 3]) cube([2.6, 7, 3]);       // snap-in opening
  }
  // back-plate screw posts (M2.5 self-tapping)
  for (p = mid_screws) translate([p[0], p[1], plate_t + 0.2]) difference() {
    cylinder(d = 5.0, h = front_in - plate_t - 0.2 + 0.05);
    translate([0, 0, -1]) cylinder(d = 2.1, h = 9);
  }
  // ribs pressing the button board's long edges
  for (sx = [-1, 1]) translate([sx * (in_w / 2 - 0.75) - 0.75, bb_y0 + 16, bb_top + 0.05]) cube([1.5, bb_l - 22, front_in - bb_top]);
  // end stops for the button board (hang past its edges)
  for (y = [bb_y0 - 1.6, bb_y0 + bb_l + 0.1]) for (sx = [-1, 1])
    translate([sx * 6 - 3, y, bb_z0 + 0.5]) cube([6, 1.5, front_in - bb_z0 - 0.45]);
  // collars under the front: pockets the cap flanges sit and slide in. Round caps get a
  // key slot so they can't turn; the ring sectors can't turn anyway, and OK's mark is a ring.
  // 1.2 mm deep: the flange sits at front_in - 0.8 and moves 0.3 when pressed
  translate([0, 0, front_in - cap_flange - 0.4]) linear_extrude(cap_flange + 0.45) difference() {
    union() {
      translate(dc) circle(r = ring_out + 1.5, $fn = 192);
      for (b = singles) translate(bpos(b)) circle(d = flange_d + 2 * flange_clr + 2.4);
    }
    translate(dc) {
      difference() { ring2d(flange_x - 0.3 + flange_clr); circle(r = ring_in, $fn = 128); }
      circle(r = ring_in + 0.15, $fn = 128);       // OK flange (r 6.2) pocket; ring flanges start at 6.6
    }
    for (b = singles) translate(bpos(b)) {
      circle(d = flange_d + 2 * flange_clr);
    }
  }
  // mic module cradle (foam-gasket ring round the grille)
  translate(concat(bpos(mic_b), [front_in - 1.2])) difference() { cylinder(d = 6.0, h = 1.25); translate([0, 0, -1]) cylinder(d = 4.0, h = 5); }
}

module shell() {
  difference() {
    union() {
      shell_body();
      intersection() { translate([0, 0, plate_t]) linear_extrude(T) plan(wall - 0.01); shell_features(); }
    }
    shell_cuts();
  }
}

// ---------- back plate ----------
module back() {
  pw = out_w - 2 * back_ch;
  difference() {
    union() {
      // the plate is the bottom slice of the chamfered envelope
      intersection() { outer_all(); translate([-100, -1, 0]) cube([200, out_l + 2, plate_t]); }
      // palm swell: hull of the plate edge and a flattened ellipsoid under the grip
      intersection() {
        hull() {
          linear_extrude(0.01) plan(back_ch + 1.0);
          translate([0, bb_y0 + 40, 0]) scale([pw / 2 - 4, 62, swell_d]) sphere(1, $fn = 96);
        }
        translate([-100, -1, -swell_d - 1]) cube([200, out_l + 2, swell_d + 1]);
      }
    }
    // index-finger rest across the swell, behind the D-pad
    translate([0, dc[1] + 4, -swell_d - 40 + groove_d]) rotate([0, 90, 0]) cylinder(r = 40, h = 100, center = true, $fn = 256);
    // screw holes; 45 deg countersink opens on the outer side
    for (p = plate_screws) translate([p[0], p[1], 0]) {
      translate([0, 0, -swell_d - 1]) cylinder(d = 2.8, h = swell_d + 1 + plate_t + 1);
      translate([0, 0, -swell_d - 1]) cylinder(d = 5.4, h = swell_d + 1);
      cylinder(d1 = 5.4, d2 = 2.8, h = 1.3);
    }
  }
}

// ---------- caps ----------
cap_h = (T + cap_proud) - (front_in - cap_flange);
sock  = act_top - (front_in - cap_flange);
// a flange layer with its bed edge stepped in by ef (three 0.1 steps, ~45 deg) for elephant's foot
module ef_flange(h) {
  for (k = [0 : 2]) translate([0, 0, k * ef / 3]) linear_extrude(ef / 3 + 0.01) offset(delta = -ef * (3 - k) / 3) children();
  translate([0, 0, ef]) linear_extrude(h - ef) children();
}
// blind hex bore for the plunger, with a 0.4 lead-in; its small flat ceiling is the only bridge
module bore() {
  translate([0, 0, -1]) rotate(30) cylinder(d = grip_af / cos(30), h = 1 + sock, $fn = 6);
  translate([0, 0, -0.01]) cylinder(d1 = grip_af / cos(30) + 0.8, d2 = grip_af / cos(30), h = 0.4, $fn = 6);
}
module ring_cap(i) {
  difference() {
    union() {
      // flange 0.4 past the opening (collar pocket is 0.95 past it), body side_clr inside it
      ef_flange(cap_flange) difference() { offset(r = 0.4) sector2d(i); circle(r = ring_in + side_clr, $fn = 128); }
      linear_extrude(cap_h - cap_top_cham) offset(r = -side_clr) sector2d(i);
      translate([0, 0, cap_h - cap_top_cham]) hull() {
        linear_extrude(0.01) offset(r = -side_clr) sector2d(i);
        translate([0, 0, cap_top_cham - 0.01]) linear_extrude(0.01) offset(r = -side_clr - cap_top_cham) sector2d(i);
      }
    }
    rotate(i * 90) translate([dpad_sw, 0, 0]) bore();
    rotate(i * 90) translate([dpad_sw - 0.5, 0, cap_h - 0.4]) linear_extrude(1) polygon([[-1.2, -2.0], [-1.2, 2.0], [1.4, 0]]);
  }
}
// d: the visible diameter; fd: flange diameter
module round_cap(d, m, key = true, fd = flange_d - 2 * flange_shrink) {
  difference() {
    union() {
      ef_flange(cap_flange) circle(d = fd);
      if (key) translate([0, -(d / 2 + rib_out), 0]) hull() {    // key rib, outer top edge chamfered
        translate([-cap_rib_w / 2, 0, 0]) cube([cap_rib_w, rib_out + 1, cap_rib_h - 0.3]);
        translate([-cap_rib_w / 2, 0.3, 0]) cube([cap_rib_w, rib_out + 0.7, cap_rib_h]);
      }
      cylinder(d = d, h = cap_h - cap_top_cham);
      translate([0, 0, cap_h - cap_top_cham]) cylinder(d1 = d, d2 = d - 2 * cap_top_cham, h = cap_top_cham);
    }
    bore();
    translate([0, 0, cap_h - 0.4]) linear_extrude(1) mark(m);
  }
}
// OK sits in a d = ok_d + 0.6 opening: body side_clr inside it, flange 0.55 past it (pocket r 6.45)
module ok_cap() { round_cap(ok_d + 0.6 - 2 * side_clr, 5, key = false, fd = ok_d + 0.6 + 1.1); }
module mark(m) {
  if (m == 5) difference() { circle(d = 5.4); circle(d = 4.0); }
  if (m == 6) { difference() { circle(d = 5); circle(d = 3.6); translate([-0.9, -3]) square([1.8, 3]); } translate([-0.45, -3]) square([0.9, 2.8]); }
  if (m == 7) { translate([0, -0.6]) offset(r = 0.9) square([0.01, 1.8], center = true); translate([-0.3, 1.0]) square([0.6, 1.2]); }
  if (m == 8) polygon([[-1.0, -2.0], [-1.0, 2.0], [1.6, 0]]);
  if (m == 9) polygon([[0, -2.2], [2.2, 0], [1.4, 0], [1.4, 1.9], [-1.4, 1.9], [-1.4, 0], [-2.2, 0]]);
  // -y is "up" (towards the tip) on every cap
  if (m == 10 || m == 11) square([3.6, 0.9], center = true);                       // VOL+ / VOL-
  if (m == 10) square([0.9, 3.6], center = true);
  if (m == 12) chevron();                                                         // CH+
  if (m == 13) mirror([0, 1]) chevron();                                          // CH-
  if (m == 14) {                                                                  // MUTE: speaker + x
    polygon([[-2.6, -0.8], [-1.6, -0.8], [-0.4, -2.0], [-0.4, 2.0], [-1.6, 0.8], [-2.6, 0.8]]);
    for (s = [-1, 1]) hull() { translate([0.7, -0.9 * s]) circle(d = 0.7, $fn = 16); translate([2.5, 0.9 * s]) circle(d = 0.7, $fn = 16); }
  }
}
module chevron() {
  for (s = [-1, 1]) hull() { translate([0, -0.9]) circle(d = 0.9, $fn = 16); translate([1.9 * s, 1.0]) circle(d = 0.9, $fn = 16); }
}
module caps_plate() {
  for (i = [0 : 3]) translate([i * 22 - 33, 0, 0]) translate([-dpad_sw * cos(i * 90), -dpad_sw * sin(i * 90), 0]) ring_cap(i);
  translate([-33, 24, 0]) ok_cap();
  for (k = [0 : len(singles) - 1]) translate([-18 + (k % 5) * 13, 24 + floor(k / 5) * 14, 0]) round_cap(cap_d, singles[k][3]);
}

// spacers between the back plate and the display board's USB-end holes
spacer_l = db_z0 - plate_t - 0.1;
module spacer() { difference() { cylinder(d = 4.6, h = spacer_l); translate([0, 0, -1]) cylinder(d = 2.8, h = spacer_l + 2); } }

// ---------- output ----------
if (part == "shell") translate([0, 0, T]) mirror([0, 0, 1]) shell();
else if (part == "back") translate([0, 0, plate_t]) mirror([0, 0, 1]) back();
else if (part == "caps") { caps_plate(); for (i = [0, 1]) translate([-40 + i * 7, 40, 0]) spacer(); }
else if (part == "cap_fit_test") {   // front-plate thickness, print face down like the shell:
  // holes 9.2 / 9.35 / 9.5 / 9.65 / 9.8 (left to right) for the 8.6 caps, each with the rib
  // notch; the small marks along the edge count them
  ds = [9.2, 9.35, 9.5, 9.65, 9.8];
  difference() {
    translate([-4, -8, 0]) cube([len(ds) * 13 - 5, 16, top_t]);
    for (i = [0 : len(ds) - 1]) translate([i * 13 + 2.5, 0, -1]) {
      cylinder(d = ds[i], h = top_t + 2);
      cylinder(d1 = ds[i] + 0.81, d2 = ds[i], h = 1.41);          // the face's 0.4 chamfer (face down)
      translate([-(rib_w + 2 * rib_clr) / 2, -(cap_d / 2 + rib_out + rib_clr), 1 + rib_skin]) cube([rib_w + 2 * rib_clr, cap_d / 2, top_t + 2]);
      for (k = [0 : i]) translate([-2 + k * 1.2, 6.2, 0]) cube([0.6, 2, top_t + 2]);
    }
  }
}
else if (part == "grip_test") {   // print flange down like the caps; push each onto a bare switch.
  // Hex bores across flats 3.4 / 3.5 / 3.6 / 3.7 / 3.8 (left to right); grooves on top count them
  afs = [3.4, 3.5, 3.6, 3.7, 3.8];
  for (i = [0 : len(afs) - 1]) translate([i * 11, 0, 0]) difference() {
    union() { ef_flange(cap_flange) circle(d = 9.0); cylinder(d = 7.0, h = sock + 1.6); }
    translate([0, 0, -1]) rotate(30) cylinder(d = afs[i] / cos(30), h = 1 + sock, $fn = 6);
    translate([0, 0, -0.01]) cylinder(d1 = afs[i] / cos(30) + 0.8, d2 = afs[i] / cos(30), h = 0.4, $fn = 6);
    for (k = [0 : i]) translate([-2.4 + k * 1.2, -1.5, sock + 1.2]) cube([0.6, 3, 1]);
  }
}
else if (part == "usb_test") {  // hold flat against the bare board's USB end, plug a cable through:
  // it adds the same offset the case floor does (floor face 0.65 mm in front of the board edge)
  difference() {
    translate([-10, -6, 0]) cube([20, 12, db_y0 - usb_floor]);
    translate([0, 0, -1]) linear_extrude(5) rr2d(usb_hole[0], usb_hole[1], usb_hole[2]);
  }
}
else if (part == "ir_test") {   // prints standing up like the tip wall: skins 0.4 / 0.6 / 0.8 / 1.0 mm
  skins = [0.4, 0.6, 0.8, 1.0];
  translate([0, 0, 8]) mirror([0, 0, 1]) difference() {   // teardrop points up, as in the shell
    cube([len(skins) * 8, wall + 4, 8]);
    for (i = [0 : len(skins) - 1]) translate([4 + i * 8, skins[i], 4]) rotate([-90, 0, 0])
      linear_extrude(wall + 6) hull() { circle(d = 3.15, $fn = 32); translate([0, 3.15 / 2 * 1.414]) square(0.01, center = true); }
  }
}
else if (part == "caps_asm") {   // caps where they sit in the case (for the fit check); press = travel
  press = 0;
  for (i = [0 : 3]) translate(concat(dc, [front_in - cap_flange - press])) ring_cap(i);
  translate(concat(dc, [front_in - cap_flange - press])) ok_cap();
  for (b = singles) translate(concat(bpos(b), [front_in - cap_flange - press])) round_cap(cap_d, b[3]);
}
else {
  color("#e9e6df") shell();
  color("#3b4048") back();
  for (i = [0 : 3]) color("#2a2e35") translate(concat(dc, [front_in - cap_flange])) ring_cap(i);
  color("#d97a2b") translate(concat(dc, [front_in - cap_flange])) ok_cap();
  for (b = singles) color(b[2] == "POWER" ? "#c94a3f" : "#2a2e35") translate(concat(bpos(b), [front_in - cap_flange])) round_cap(cap_d, b[3]);
}

echo(str("OUTER ", out_w, " x ", out_l, " x ", T, " (+", swell_d, " palm swell) mm; spacer ", spacer_l, "; db_z0 ", db_z0, "; JST room behind display ", db_z0 - plate_t));
