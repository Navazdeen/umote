// umote case v7: the charging dock (as v6, with the pocket cut from the keel envelope) and its swappable contact plates (A: P75 probes + magnets, B: a
// ready-made magnetic connector's other half).

// ---------- dock ----------
// Holds the remote upright on its bottom end, leaning back dock_lean, screen towards the user. Two
// P75-B1 probes stand pogo_proud out of the pocket floor (the remote's end face), so they compress
// that much onto the brass pads; two 10 x 2 magnets face the remote's. Built in remote coordinates.
dock_lean = 15;  pogo_proud = 0.75;  dock_pocket = 16;  dock_g = 0.4;
usbc_bo = [13, 11, 4];              // USB-C breakout board pocket [CHECK]
module remote_to_world() rotate([dock_lean - 90, 0, 0]) translate([0, -L, 0]) children();
module world_to_remote() translate([0, L, 0]) rotate([90 - dock_lean, 0, 0]) children();
// one straight press-fit hole per probe, right through to the wire channel under the floor (a wider
// wire hole below would leave a ledge facing down); glue if the press fit is loose
module pogo_holes() for (sx = [-1, 1]) translate([sx * pad_x, L - 0.5, pad_z]) rotate([-90, 0, 0]) cylinder(d = pogo_d, h = 40, $fn = 24);
module pogo_tips() for (sx = [-1, 1]) translate([sx * pad_x, L - pogo_proud, pad_z]) rotate([-90, 0, 0]) cylinder(d = 0.74, h = pogo_l, $fn = 16);
module dock_raw() difference() {
  world_to_remote() translate([-32, -16, -20]) cube([64, 34, 20 + 12]);
  intersection() { envelope(dock_g); translate([-50, L - dock_pocket - 30, -20]) cube([100, dock_pocket + 30, 60]); }
  world_to_remote() translate([-usbc_bo[0] / 2, 18 - usbc_bo[1] + 0.01, -20 - 0.01]) cube([usbc_bo[0], usbc_bo[1], usbc_bo[2]]);   // breakout, port at the back
  world_to_remote() translate([-1, -2, -20]) cube([2, 20, usbc_bo[2] - 1]);                                                         // wires under the floor
}
// the dock's half of the contacts is a swappable plate too: a block under the remote's end, its top
// the pocket floor; it drops into the dock from the pocket (press fit, a drop of glue if loose)
dp_t = 6.0;
module dp_region(g = 0) translate([-pp_w / 2 - g, L - 2, pp_z0 - g]) cube([pp_w + 2 * g, 2 + dock_g + dp_t + g, pz0 - 0.05 - pp_z0 + 2 * g]);
module dock() difference() { dock_raw(); dp_region(0.2); pogo_holes(); }
module dock_plate_a() difference() {   // P75 probes onto plate A's pads, 10 x 2 magnets facing plate A's
  intersection() { dock_raw(); dp_region(0); }
  pogo_holes();
  for (sx = [-1, 1]) translate([sx * dmag_x, L - 0.5, dmag_z]) rotate([-90, 0, 0]) cylinder(d = magnet[0] + 0.2, h = magnet[1] + 0.6, $fn = 64);
}
module dock_plate_b() difference() {   // the connector's other half, flush with the pocket floor
  intersection() { dock_raw(); dp_region(0); }
  translate([-conn_b[0] / 2 - 0.15, L - 1, pad_z - conn_b[1] / 2 - 0.15]) cube([conn_b[0] + 0.3, dp_t + 5, conn_b[1] + 0.3]);
  for (sx = [-1, 1]) translate([sx * conn_b[3] / 2, L + dock_g + dp_t + 0.01, pad_z]) rotate([90, 0, 0]) cylinder(d = conn_b[4], h = 4.0, $fn = 24);
}
