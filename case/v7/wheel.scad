// umote case v7: the roller's bought parts (for the fit check and the viewer) and the printed wheel.
// Unchanged from v6: EC11 on its side, shaft along -x, bushing through a bulkhead with its nut.
win = [whl_w + 0.8, 2 * sqrt(pow(whl_d / 2 + whl_gap, 2) - pow(pz0 - axle_z, 2))];   // wheel window in the face: x, y
room_y1 = y_key_start - col_wall;
s2 = [for (sx = [-1, 1]) [sx * 20.2, cy + 6.5]];           // head plate -> cheeks

module ec11_model() {
  translate([ec11_xf, cy - ec11_d / 2, axle_z - ec11_w / 2]) cube([ec11_h, ec11_d, ec11_w]);                  // body
  translate([ec11_xf + 0.01, cy, axle_z]) rotate([0, -90, 0]) cylinder(d = ec11_bush[0], h = ec11_bush[1] + 0.01, $fn = 48);   // bushing
  translate([ec11_xf, cy, axle_z]) rotate([0, -90, 0]) difference() {                                              // D shaft
    cylinder(d = ec11_shaft[0], h = ec11_shaft[1], $fn = 48);
    translate([-10, ec11_shaft[2] - ec11_shaft[0] / 2, ec11_shaft[1] - ec11_shaft[3]]) cube([20, 10, 20]);
  }
  // pins: out of the body's side, bent back through the carrier, trimmed 1.0 past it
  for (r = [0, 1], k = r == 0 ? [-1, 0, 1] : [-1, 1]) let(py = cy + ec11_rows[r], pz = axle_z + k * ec11_pitch) {
    translate([ec11_xf + ec11_h - 0.01, py - 0.4, pz - 0.4]) cube([carrier[0] + 1.0, 0.8, 0.8]);
    hull() { translate([ec11_xf + ec11_h - 0.8, py - 0.4, pz - 0.4]) cube([0.8, 0.8, 0.8]);
             translate([ec11_xf + ec11_h - 0.8, cy + sign(ec11_rows[r]) * (ec11_d / 2 - 0.5) - 0.4, pz - 0.4]) cube([0.8, 0.8, 0.8]); }
  }
}
module ec11_nut_model() translate([ec11_xf - bulk_t - ec11_nut[1], cy, axle_z]) rotate([0, 90, 0])
  rotate(30) cylinder(d = ec11_nut[0] / cos(30), h = ec11_nut[1], $fn = 6);
module carrier_model() translate([ec11_xf + ec11_h, cy - 8.75, 0.1]) cube([carrier[0], carrier[1], carrier[2]]);

// knurled wheel, D-bore for the EC11 shaft
module wheel() { difference() {
  rotate([0, 90, 0]) cylinder(d = whl_d, h = whl_w, center = true, $fn = 96);
  for (a = [0 : 10 : 359]) rotate([a, 0, 0]) translate([0, 0, whl_d / 2]) cube([whl_w + 1, 0.9, 0.9], center = true);
  rotate([0, 90, 0]) difference() { cylinder(d = ec11_shaft[0] + 0.15, h = whl_w + 2, center = true, $fn = 48);
    translate([ec11_shaft[2] - ec11_shaft[0] / 2 + 0.075, -5, -10]) cube([10, 10, 20]); }       // D flat
} }
module wheel_at() translate([whl_x, cy, axle_z]) wheel();
module wheel_room() translate([whl_x, cy, axle_z]) rotate([0, 90, 0]) cylinder(r = whl_d / 2 + whl_gap, h = whl_w + 2 * whl_gap, center = true, $fn = 96);
