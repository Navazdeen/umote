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
module yslice(y) ycut(y - 0.01, y) envelope();
module inner_slice(y) ycut(y - 0.01, y) union() {
  translate([0, 0, floor_t]) linear_extrude(roll_z - floor_t) plan(wall);
  stack(roll_z, T - top_skin, 6, 1.8);
}
module collar_shell() { difference() {
  hull() { head_xf() yslice(y_head_end); yslice(y_key_start); }
  hull() { head_xf() translate([0, -0.5, 0]) inner_slice(y_head_end); translate([0, 0.5, 0]) inner_slice(y_key_start); }
} }

module wheel_envelope(grow = 0) { translate([whl_x, cy, axle_z]) rotate([0, 90, 0])
  cylinder(d = whl_d + 2 * grow, h = whl_w + 2 * grow, center = true, $fn = 96); }
module ec11_envelope(grow = 0) { translate([ec11_x0 - grow, cy - ec11[1] / 2 - grow, axle_z - ec11[0] / 2 - grow])
  cube([ec11[2] + 2 * grow, ec11[1] + 2 * grow, ec11[0] + 2 * grow]); }

module collar_core() { difference() {
  union() {
    collar_shell();
    // pivot bosses with open-top U slots for the cradle's pins, both ends of the crossbar
    for (x = [-15.6, 15.6]) translate([x, piv[0], floor_t - 0.01]) boss_block();
  }
  // wheel window in the top skin, and the wheel's own room (it is nearly as tall as the body)
  translate([whl_x, cy, T - top_skin - 0.5]) linear_extrude(top_skin + 1) square([whl_w + 0.8, whl_d + 0.8], center = true);   // square: its top edge bridges when printed standing
  wheel_envelope(0.4);           // its bottom stops at z 0.4: the back stays closed under the wheel
  // floor pocket under the cradle
  hull() {                       // its head end ramps at 45 deg (that end faces down when printed standing)
    translate([-14, piv[0] - 1, floor_t - floor_pocket]) cube([28, tact_c[1] + tact[1] / 2 + 3.5 - piv[0], 0.01]);
    translate([-14, piv[0] - 1 - floor_pocket - 0.6, floor_t + 0.6]) cube([28, tact_c[1] + tact[1] / 2 + 3.5 - piv[0] + floor_pocket + 0.6, 0.01]);
  }
  // tab slots, open towards the face: 0.2 a side round the 1.6 x 1.0 tabs, 0.4 tall for the rock
  for (x = [-15.6, 15.6]) translate([x - 2, piv[0] - 1.0, piv[1] - cradle_t / 2 - 0.05]) cube([4, 2.0, 10]);
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
