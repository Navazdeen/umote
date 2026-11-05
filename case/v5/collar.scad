// umote case v5: the crease collar (accent part joining the halves), the roller wheel and its cradle.
// Assembled coordinates. The collar prints on its side (the -x side down).

top_skin = skin_min;                // collar top over the EC11
whl_x = 0;                          // wheel centre across
ec11_x0 = whl_x + whl_w / 2 + 1.5;  // EC11 body face (shaft side); body runs +x from here, off centre
ec11_c = [ec11_x0 + ec11[2] / 2, cy, axle_z];
piv = [79.1, axle_z - ec11[0] / 2 - cradle_t / 2];  // cradle pivot axis: y, z
tact_c = [-10, 89];                 // 6x6 tact switch on the collar floor, the other side of the wheel
floor_pocket = 0.6;                 // the collar floor thins under the cradle so it can swing down

// a pivot boss: 3 x 4 block on the floor; its +y face slopes 45 deg (it faces down when the collar
// stands on its key face)
module boss_block() { h = piv[1] - floor_t + 1.2;
  translate([-1.5, -2, 0]) hull() { cube([3, 4, h]); translate([0, 0, 0]) cube([3, 4 + h, 0.01]); } }
// a thin slice of the envelope at y (for hulling the collar between the two halves)
module yslice(y, side = 1) ycut(side > 0 ? y : y - 0.01, side > 0 ? y + 0.01 : y) envelope();   // side +1: just past y
module inner_slice(y) ycut(y - 0.01, y) union() {
  translate([0, 0, floor_t]) linear_extrude(roll_z - floor_t) plan(wall);
  stack(roll_z, T - top_skin, 6, 1.8);
}
module collar_shell() { difference() {
  hull() { head_xf() yslice(y_head_end, 1); yslice(y_key_start, -1); }
  hull() { head_xf() translate([0, -0.5, 0]) inner_slice(y_head_end); translate([0, 0.5, 0]) inner_slice(y_key_start); }
} }

module wheel_envelope(grow = 0) { translate([whl_x, cy, axle_z]) rotate([0, 90, 0])
  cylinder(d = whl_d + 2 * grow, h = whl_w + 2 * grow, center = true, $fn = 96); }
module ec11_envelope(grow = 0) { translate([ec11_x0 - grow, cy - ec11[1] / 2 - grow, axle_z - ec11[0] / 2 - grow])
  cube([ec11[2] + 2 * grow, ec11[1] + 2 * grow, ec11[0] + 2 * grow]); }

// wheel window in the top skin (square: its edge bridges when printed standing), and the wheel's
// own room; the room's bottom stops at z 0.4, so the back stays closed under the wheel
module wheel_cuts() {
  translate([whl_x, cy, T - top_skin - 0.5]) linear_extrude(top_skin + 1) square([whl_w + 0.8, whl_d + 0.8], center = true);
  intersection() { wheel_envelope(0.5); translate([-50, 0, 0.4]) cube([100, L, 30]); }   // closed 0.4 skin under the wheel
}
// a hole along z whose cross-section points to -y: the collar prints standing on its key face,
// so these holes lie on their side and -y is up
module td_hole(d, h) linear_extrude(h) polygon(concat([for (k = [0 : 23]) let(t = -38.7 + 257.4 * k / 23) [d / 2 * cos(t), d / 2 * sin(t)]], [[0, -d / 2 * 1.6]]));   // 39 deg sides
module collar_core() { difference() {
  union() {
    collar_shell();
    // pivot bosses with open-top U slots for the cradle's pins, both ends of the crossbar
    for (x = [-15.6, 15.6]) translate([x, piv[0], floor_t - 0.01]) boss_block();
  }
  wheel_cuts();
  // floor pocket under the cradle
  difference() {                 // the tact switch keeps its floor at floor_t
    hull() {                     // the pocket's head end ramps at 45 deg (it faces down when printed standing)
      translate([-14, piv[0] - 1, floor_t - floor_pocket]) cube([28, tact_c[1] + tact[1] / 2 + 3.5 - piv[0], 0.01]);
      translate([-14, piv[0] - 1 - floor_pocket - 0.6, floor_t + 0.6]) cube([28, tact_c[1] + tact[1] / 2 + 3.5 - piv[0] + floor_pocket + 0.6, 0.01]);
    }
    translate([tact_c[0] - tact[0] / 2 - 0.3, tact_c[1] - tact[1] / 2 - 0.3, 0]) cube([tact[0] + 0.6, tact[1] + 0.6, 5]);
  }
  // tab slots, open towards the face: 0.2 a side round the 1.6 x 1.0 tabs, 0.4 tall for the rock
  for (x = [-15.6, 15.6]) translate([x - 2, piv[0] - 1.0, piv[1] - cradle_t / 2 - 0.05]) cube([4, 2.0, 10]);
  // the bend tilts the collar's inner floor up towards the head (1.66 at the tact): flatten it to
  // floor_t under the tact switch and the cradle so their heights are the ones the design uses
  translate([-17, piv[0] - 3, floor_t]) cube([34, tact_c[1] + tact[1] / 2 + 3.5 - piv[0] + 3, 0.3]);
} }

// ---------- wheel: knurled, D-bore for the EC11 shaft ----------
module wheel() { difference() {
  rotate([0, 90, 0]) cylinder(d = whl_d, h = whl_w, center = true, $fn = 96);
  for (a = [0 : 10 : 359]) rotate([a, 0, 0]) translate([0, 0, whl_d / 2]) cube([whl_w + 1, 0.9, 0.9], center = true);
  rotate([0, 90, 0]) difference() { cylinder(d = ec11_shaft_d + 0.15, h = whl_w + 2, center = true, $fn = 48);
    translate([ec11_shaft_d / 2 - 1.5 + 0.1, -5, -10]) cube([10, 10, 20]); }       // D flat 1.5 deep
} }

// ---------- cradle: holds the EC11 on its side, rocks on its crossbar's end tabs, presses the tact ----------
// No round pins: the crossbar's end tabs rock in open slots in the pivot bosses. At rest it lies on
// the tact plunger (touching, not pressed), like a mouse wheel: the tact needs ~1.6 N, the cradle
// and encoder weigh a few grams. Prints flat: every part starts at the plate's underside, and the
// arm over the tact is a short bridge between two risers.
cr_z0 = piv[1] - cradle_t / 2;      // underside of the plate, crossbar and risers
cr_ys = [piv[0] - 0.8, piv[0] + 0.8];   // crossbar
arm_x = [tact_c[0] - 2.5, tact_c[0] + 2.5];
riser2_y = tact_c[1] + tact[1] / 2 + 0.5;
module cradle() {
  translate([ec11_x0 - 0.5, cr_ys[0], cr_z0]) cube([ec11[2] + 1, cy + ec11[1] / 2 - cr_ys[0], cradle_t]);   // plate
  translate([-17, cr_ys[0], cr_z0]) cube([34, 1.6, cradle_t]);                                              // crossbar + end tabs
  arm_z = floor_t + tact[2];
  for (y = [cr_ys[0], riser2_y]) translate([arm_x[0], y, cr_z0]) cube([5, 1.6, arm_z + 1 - cr_z0]);         // risers
  translate([arm_x[0], cr_ys[0], arm_z]) cube([5, riser2_y + 1.6 - cr_ys[0], 1.0]);                         // arm (bridge)
}

// ---------- joints (spec section 5, as ruled in Task 4) ----------
z_tf = floor_t + 1.8;               // top of the thickened floor under the prongs
crease_hole = [1.7, 2.3, 4.0, 1.8]; // M2: self-tap, clearance, head d, head depth
plate_d = 0.8;  plate_w = 43.2;     // magnet plate: recess depth, width (x +-21.6)
plate_y0 = y_head_end - 1.0;        // plate's crease end (on the collar's back)
module prong_sites(head) {          // M2 screw centres of the prongs (same numbers the bodies use)
  for (sx = [-1, 1]) if (head) head_xf() translate([sx * prong_x, y_head_end + prong[1] / 2, 0]) children();
                     else translate([sx * prong_x, y_key_start - prong[1] / 2, 0]) children();
}
module thick_floor() {              // pads under the prongs, inside the collar
  for (sx = [-1, 1]) {
    head_xf() translate([sx > 0 ? 17.8 : -in_w / 2 - 0.1, y_head_end - 0.01, floor_t - 0.01]) hull() {   // +y end at 45 deg (faces down in print)
      cube([in_w / 2 - 17.8 + 0.1, prong[1] + 2.6, 0.01]); cube([in_w / 2 - 17.8 + 0.1, prong[1], z_tf - floor_t]); }   // 35 deg + the 8 deg bend
    translate([sx > 0 ? 17.8 : -in_w / 2 - 0.1, y_key_start - prong[1], floor_t - 0.01]) cube([in_w / 2 - 17.8 + 0.1, prong[1] + 0.01, z_tf - floor_t]);
  }
}
module crease_screw_cuts() for (h = [true, false]) prong_sites(h) {
  translate([0, 0, -1]) td_hole(crease_hole[1], z_tf + 2);
  translate([0, 0, -1]) td_hole(crease_hole[2], 1 + plate_d + crease_hole[3]);
}
// the battery door's two tabs: from the window up the collar's back, over the 4 crease screws (x +-19.5);
// the collar's back stays whole between them (under the roller)
tab_x = [15.0, 21.6];
module tab2d(grow = 0) for (sx = [-1, 1]) translate([sx > 0 ? tab_x[0] - grow : -tab_x[1] - grow, plate_y0 - grow])
  square([tab_x[1] - tab_x[0] + 2 * grow, door_win_y0 - plate_y0 + 1 + 2 * grow]);
module plate_recess() translate([0, 0, -0.01]) intersection() {   // 45 deg ramp at its crease end
  hull() {
    translate([-50, plate_y0 - 0.15, 0]) cube([100, L, plate_d + 0.01]);
    translate([-50, plate_y0 - 0.15 - plate_d, 0]) cube([100, L, 0.01]);
  }
  linear_extrude(plate_d + 0.02) tab2d(0.15);
}
// lip over the head panel's 45 deg collar edge (in head coordinates; it is the top of the print)
module head_lip() head_xf() intersection() {
  translate([-50, 0, 0]) rotate([90, 0, 90]) linear_extrude(100)
    polygon([[y_head_end - lip + 0.2, T], [y_head_end + 3, T], [y_head_end + 0.15, T - lip + 0.05]]);   // 0.1 off the panel's chamfer; inner face slopes gently into the skin
  panel_zone(pcl);
}
// key-end blocks under the top skin, with the grooves for the key panel's wedge tongues
tongue = [10, 1.2];                 // width, reach = height: exactly 45 deg suits both prints (panel face down, collar standing)
tongue_x = 13;
module key_tongue2d(grow = 0) offset(delta = grow) polygon([[y_key_start + 0.01, pz0 - 0.8], [y_key_start + 0.01, pz0 - 0.8 + tongue[1]],
  [y_key_start - tongue[1] + 0.01, pz0 - 0.8]]);
module key_blocks() for (sx = [-1, 1]) difference() {
  translate([sx > 0 ? 6.2 : -20, y_key_start - 2.2, 12.4]) cube([13.8, 2.21, T - top_skin - 12.4 + 0.01]);
  translate([sx * tongue_x - tongue[0] / 2 - 0.2, 0, 0]) rotate([90, 0, 90]) linear_extrude(tongue[0] + 0.4) key_tongue2d(0.15);
}
module collar() { difference() {
  union() { collar_core(); thick_floor(); head_lip(); key_blocks(); }
  crease_screw_cuts(); plate_recess(); wheel_cuts();
} }

// pressed: the cradle (and what it carries) swings down about its tabs until the arm has pushed
// the tact plunger 0.25 mm
press_a = asin(0.25 / (tact_c[1] - piv[0]));
module pressed() translate([0, piv[0], piv[1]]) rotate([-press_a, 0, 0]) translate([0, -piv[0], -piv[1]]) children();
