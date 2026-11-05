// umote case v6: the wheel zone. Assembled (key) coordinates.
// Two parts: the collar FRAME (the black cap across the face, its inner walls, the bulkhead that
// carries the EC11) and the RIDGE plate (the back ridge, the collar floor and the wheel well).
// The key body's rails stand either side of the frame (|x| >= rail_x); the head's tenons run into
// slots in the rails. Four M2 from the ridge's underside hold the lot: two into the tenons, two up
// through the rails into bosses under the cap.
// Frame prints cap down; ridge prints bottom down.

// the head's end plane in key coordinates, at height z: y of the plane (it leans with the bend)
function head_face_y(z) = y_head_end - (T - z) * tan(theta);
cap_z = T - min_panel;                // cap underside = room ceiling (14.6)
room_x = col_x - col_wall;            // room half-width inside the frame's side walls
room_y1 = y_key_start - col_wall;
win = [whl_w + 0.8, 2 * sqrt(pow(whl_d / 2 + whl_gap, 2) - pow(cap_z - axle_z, 2))];   // wheel window: x, y
groove_x = [[-22.4, -19.6], [19.6, 22.4]];  // key-panel tongue grooves (x ranges), in the rails' key ends (1.25 to the rail's inner face)
tongue_h = 2.0;                       // tongue: reach = height (45 deg)
s1 = [for (sx = [-1, 1]) [sx * 20.0, y_head_end + 3.0]];   // ridge -> head tenon (a pin across the joint)
s2 = [for (sx = [-1, 1]) [sx * 20.2, cy + 6.5]];           // ridge -> rail
s3 = [[6.75, y_head_end + 2.5], [6.75, y_key_start - 3.6]];  // ridge -> frame (bosses on the bulkhead's legs)
s3_d = 4.6;

// ---------- the slice helpers ----------
// a box from the head's end plane (head_face_y + off) to y1, x +-hx, z z0..z1
module from_head_plane(off, y1, hx, z0, z1) intersection() {
  translate([-hx, -50, z0]) cube([2 * hx, 400, z1 - z0]);
  head_xf() translate([-100, y_head_end + off, -100]) cube([200, 300, 300]);
  translate([-100, -100, -100]) cube([200, y1 + 100, 300]);
}

// ---------- real parts (for the fit check, the tests and the viewer) ----------
// EC11 on its side: frame top at x = ec11_xf, body +x of it, shaft along -x
module ec11_model() {
  translate([ec11_xf, cy - ec11_d / 2, axle_z - ec11_w / 2]) cube([ec11_h, ec11_d, ec11_w]);                  // body
  translate([ec11_xf + 0.01, cy, axle_z]) rotate([0, -90, 0]) cylinder(d = ec11_bush[0], h = ec11_bush[1] + 0.01, $fn = 48);   // bushing
  translate([ec11_xf, cy, axle_z]) rotate([0, -90, 0]) difference() {                                              // D shaft
    cylinder(d = ec11_shaft[0], h = ec11_shaft[1], $fn = 48);
    translate([-10, ec11_shaft[2] - ec11_shaft[0] / 2, ec11_shaft[1] - ec11_shaft[3]]) cube([20, 10, 20]);
  }
  // pins: out of the body's side, bent back through the carrier, trimmed 1.0 past it
  for (r = [0, 1], k = r == 0 ? [-1, 0, 1] : [-1, 1]) let(py = cy + ec11_rows[r], pz = axle_z + k * ec11_pitch * (r == 0 ? 1 : 1)) {
    translate([ec11_xf + ec11_h - 0.01, py - 0.4, pz - 0.4]) cube([carrier[0] + 1.0, 0.8, 0.8]);
    hull() { translate([ec11_xf + ec11_h - 0.8, py - 0.4, pz - 0.4]) cube([0.8, 0.8, 0.8]);
             translate([ec11_xf + ec11_h - 0.8, cy + sign(ec11_rows[r]) * (ec11_d / 2 - 0.5) - 0.4, pz - 0.4]) cube([0.8, 0.8, 0.8]); }
  }
}
module ec11_nut_model() translate([ec11_xf - bulk_t - ec11_nut[1], cy, axle_z]) rotate([0, 90, 0])
  rotate(30) cylinder(d = ec11_nut[0] / cos(30), h = ec11_nut[1], $fn = 6);
module carrier_model() translate([ec11_xf + ec11_h, cy - 8.75, floor_t + 0.1]) cube([carrier[0], carrier[1], carrier[2]]);

// ---------- wheel: knurled, D-bore for the EC11 shaft ----------
module wheel() { difference() {
  rotate([0, 90, 0]) cylinder(d = whl_d, h = whl_w, center = true, $fn = 96);
  for (a = [0 : 10 : 359]) rotate([a, 0, 0]) translate([0, 0, whl_d / 2]) cube([whl_w + 1, 0.9, 0.9], center = true);
  rotate([0, 90, 0]) difference() { cylinder(d = ec11_shaft[0] + 0.15, h = whl_w + 2, center = true, $fn = 48);
    translate([ec11_shaft[2] - ec11_shaft[0] / 2 + 0.075, -5, -10]) cube([10, 10, 20]); }       // D flat
} }
module wheel_at() translate([whl_x, cy, axle_z]) wheel();
module wheel_room() translate([whl_x, cy, axle_z]) rotate([0, 90, 0]) cylinder(r = whl_d / 2 + whl_gap, h = whl_w + 2 * whl_gap, center = true, $fn = 96);

// ---------- frame ----------
// the cap: the envelope's top 2.0 across the full width, from the head's end plane to y_key_start
module frame_cap() intersection() {
  envelope();
  from_head_plane(0, y_key_start, 60, cap_z, T + 1);
}
module frame_walls() difference() {
  from_head_plane(0, y_key_start, col_x, floor_t, cap_z + 0.01);
  from_head_plane(col_wall, room_y1, room_x, floor_t - 1, cap_z);
}
// bulkhead: the bushing goes in a U-slot open to the bottom (the EC11 drops in with nut and wheel on)
module bulkhead() difference() {
  intersection() { from_head_plane(0, y_key_start, 60, floor_t, cap_z + 0.01); translate([ec11_xf - bulk_t, -50, 0]) cube([bulk_t, 400, 30]); }
  translate([ec11_xf - bulk_t - 1, cy, axle_z]) rotate([0, 90, 0]) linear_extrude(bulk_t + 2) {
    circle(d = ec11_bush[0] + 0.3, $fn = 48);
    translate([0, -(ec11_bush[0] + 0.3) / 2]) square([20, ec11_bush[0] + 0.3]);   // rotated: +local x = -z (down)
  }
}
module tongue2d(grow = 0) offset(delta = grow) polygon([[y_key_start + 0.4, pz0 - tongue_h], [y_key_start + 0.4, pz0 + 0.01], [y_key_start, pz0 + 0.01], [y_key_start - tongue_h, pz0 - tongue_h]]);   // root 0.3 into the panel
module s3_bosses() for (p = s3) translate([p[0], p[1], floor_t]) cylinder(d = s3_d, h = cap_z - floor_t + 0.01, $fn = 40);
module frame() difference() {
  union() { frame_cap(); frame_walls(); bulkhead(); s3_bosses(); }
  translate([whl_x - win[0] / 2, cy - win[1] / 2, cap_z - 1]) cube([win[0], win[1], 10]);   // wheel window
  wheel_room();
  // wire notches, open at the bottom: the battery / inter-board bundle on -x (through both end
  // walls), the roller's on +x (key end only)
  translate([-15.3, -50, floor_t - 1]) cube([5.3, 400, 11.2 - floor_t + 1]);
  translate([13.2, room_y1 - 1, floor_t - 1]) cube([2.3, 10, 12.0 - floor_t + 1]);
  translate(concat(bpos(mic_b), [bb_top - 0.5])) cylinder(d = mic_mod[0] + 1.0, h = mic_mod[1] + 1.2, $fn = 64);   // the mic module overhangs the board's top edge
  for (p = s3) translate([p[0], p[1], floor_t - 1]) cylinder(d = m2[0], h = 1 + 7, $fn = 24);
}

// ---------- ridge ----------
ridge_in = e_in(0);                   // the body's plan inset at the back (2.33): the ridge's sides drop straight from it
module ridge_shape() {
  y0 = head_face_y(0) - 0.3;  y1 = y_key_start + 3.0;   // runs 3 on under the key half's back (clear of the frame screw's countersink)   // 0.3 under the head's back edge (it is 0.16 up there): no shared edge with the floor block
  hull() {
    translate([0, 0, -0.01]) linear_extrude(0.01) intersection() { plan(ridge_in); translate([-50, y0]) square([100, y1 - y0]); }
    translate([0, 0, -1.0]) linear_extrude(0.01) intersection() { plan(ridge_in); translate([-50, y0]) square([100, y1 - y0]); }   // 1.0 straight before the ramps: no knife edge
    translate([0, 0, -ridge_h + 0.5]) linear_extrude(0.01) intersection() { plan(ridge_in); translate([-50, y0 + ridge_h - 1.5]) square([100, y1 - y0 - 2 * (ridge_h - 1.5)]); }
    translate([0, 0, -ridge_h]) linear_extrude(0.01) intersection() { plan(ridge_in + 0.5); translate([-50, y0 + ridge_h - 1.0]) square([100, y1 - y0 - 2 * (ridge_h - 1.0)]); }
  }
}
module ridge() difference() {
  union() {
    ridge_shape();
    from_head_plane(0, y_key_start, col_x, -0.01, floor_t);          // collar floor under the room
  }
  wheel_room();
  tenons_xf(0.15);                                                   // the head tenons dip into the wings
  for (p = concat(s1, s2, s3)) translate([p[0], p[1], -ridge_h]) m2_csk(30);
}
