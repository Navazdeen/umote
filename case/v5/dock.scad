// umote case v5: the battery door (part name magnet_plate) and the charging dock.

// ---------- battery door ----------
// Over the key body: fills the back window, flush, 1.6 thick, its long edges following the body's
// 42 deg foot. Over the collar: 0.8 thick in the collar's recess, hooked under its 45 deg ramp.
// Two detent bumps on its bottom end click into the bottom-zone floor.
det_x = 12;  det = [3, 0.35];       // detent bumps: x positions, [width, protrusion]
module door_key_part() intersection() {
  envelope();
  translate([0, 0, -1]) linear_extrude(floor_t + 1 - 0.0) door2d(0);
  translate([-50, y_key_start, -1]) cube([100, door_y1 - y_key_start, 30]);
}
module door_collar_part() intersection() {
  translate([0, 0, -0.01]) hull() {
    translate([-50, plate_y0, 0]) cube([100, y_key_start - plate_y0 + 0.01, plate_d]);
    translate([-50, plate_y0 - plate_d, 0]) cube([100, y_key_start - plate_y0 + plate_d + 0.01, 0.01]);
  }
  translate([0, 0, -1]) linear_extrude(3) plate2d();
}
module door_detents(grow = 0) for (sx = [-1, 1]) translate([sx * det_x - det[0] / 2 - grow, door_y1, 0.8]) rotate([0, 90, 0])
  linear_extrude(det[0] + 2 * grow) polygon([[0.45 + grow, -0.01], [0, det[1] + grow], [-0.45 - grow, -0.01]]);
module magnet_plate() union() { door_key_part(); door_collar_part(); door_detents(); }

// ---------- dock ----------
// Holds the remote upright on its bottom end, leaning back dock_lean, screen towards the user. Two
// P75-B1 probes stand pogo_proud out of the pocket floor (the remote's end face), so they compress
// that much onto the brass pads; two 10 x 2 magnets face the remote's. Built in remote coordinates.
dock_lean = 15;  pogo_proud = 0.75;  dock_pocket = 16;  dock_g = 0.4;
usbc_bo = [13, 11, 4];              // USB-C breakout board pocket [CHECK]
module remote_to_world() rotate([dock_lean - 90, 0, 0]) translate([0, -L, 0]) children();
module world_to_remote() translate([0, L, 0]) rotate([90 - dock_lean, 0, 0]) children();
module env_grown(g) union() {        // the envelope grown by g (for the pocket)
  slab(-g, bed_ch, e_in(0) - g, e_in(bed_ch) - g); stack(bed_ch, eb, 12, -g); slab(eb, roll_z, -g, -g); stack(roll_z, T, 10, -g); slab(T - 0.01, T + g, e_in(T) - g, e_in(T) - g);
}
// one straight press-fit hole per probe, right through to the wire channel under the floor (a wider
// wire hole below would leave a ledge facing down); glue if the press fit is loose
module pogo_holes() for (sx = [-1, 1]) translate([sx * pad_x, L - 0.5, pad_z]) rotate([-90, 0, 0]) cylinder(d = pogo_d, h = 40, $fn = 24);
module pogo_tips() for (sx = [-1, 1]) translate([sx * pad_x, L - pogo_proud, pad_z]) rotate([-90, 0, 0]) cylinder(d = 0.74, h = pogo_l, $fn = 16);
module dock() difference() {
  world_to_remote() translate([-32, -16, -20]) cube([64, 34, 20 + 12]);
  intersection() { translate([0, 0, 0]) env_grown(dock_g); translate([-50, L - dock_pocket - 30, -20]) cube([100, dock_pocket + 30, 60]); }
  pogo_holes();
  for (sx = [-1, 1]) translate([sx * dmag_x, L - 0.5, dmag_z]) rotate([-90, 0, 0]) cylinder(d = magnet[0] + 0.2, h = magnet[1] + 0.6, $fn = 64);
  world_to_remote() translate([-usbc_bo[0] / 2, 18 - usbc_bo[1] + 0.01, -20 - 0.01]) cube([usbc_bo[0], usbc_bo[1], usbc_bo[2]]);   // breakout, port at the back
  world_to_remote() translate([-1, -2, -20]) cube([2, 20, usbc_bo[2] - 1]);                                                         // wires under the floor
}
