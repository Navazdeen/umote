// umote case v6: the wheel zone. Assembled (key) coordinates.
// Three parts: the collar FRAME (the black cap across the face, its inner walls, the bulkhead that
// carries the EC11), the RIDGE (the finger-rest hump on the back: the collar's floor, the wheel well)
// and the GRIP PAD that covers the ridge's 4 screws.
// The key body's rails stand either side of the frame (|x| >= rail_x); the head's tenons run into
// slots in the rails. The frame drops in from the top (its cap rests on the rails) and is held down
// by two lips under the panels' ends. Four M2 from the ridge's underside: two pin the tenons, two go
// into the rails; the pad presses in over them.
// Frame prints cap down; ridge prints upside down (its flat top on the bed, the hump up); pad flat.

// the head's end plane in key coordinates, at height z: y of the plane (it leans with the bend)
function head_face_y(z) = y_head_end - (T - z) * tan(theta);
cap_z = T - min_panel;                // cap underside = room ceiling (14.6)
room_x = col_x - col_wall;            // room half-width inside the frame's side walls
room_y1 = y_key_start - col_wall;
win = [whl_w + 0.8, 2 * sqrt(pow(whl_d / 2 + whl_gap, 2) - pow(cap_z - axle_z, 2))];   // wheel window: x, y
groove_x = [[-22.4, -19.6], [19.6, 22.4]];  // key-panel tongue grooves (x ranges), in the rails' key ends (1.25 to the rail's inner face)
tongue_h = 2.0;                       // tongue: reach = height (45 deg)
s1 = [for (sx = [-1, 1]) [sx * 20.0, y_head_end + 3.6]];   // ridge -> head tenon (a pin across the joint)
s2 = [for (sx = [-1, 1]) [sx * 20.2, cy + 6.5]];           // ridge -> rail

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
module carrier_model() translate([ec11_xf + ec11_h, cy - 8.75, 0.1]) cube([carrier[0], carrier[1], carrier[2]]);

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
  from_head_plane(0, y_key_start, col_x, 0, cap_z + 0.01);       // stands on the ridge's flat top (z 0)
  from_head_plane(col_wall, room_y1, room_x, -1, cap_z);
}
// bulkhead: the bushing goes in a U-slot open to the bottom (the EC11 drops in with nut and wheel on)
module bulkhead() difference() {
  intersection() { from_head_plane(0, y_key_start, 60, 0, cap_z + 0.01); translate([ec11_xf - bulk_t, -50, 0]) cube([bulk_t, 400, 30]); }
  translate([ec11_xf - bulk_t - 1, cy, axle_z]) rotate([0, 90, 0]) linear_extrude(bulk_t + 2) {
    circle(d = ec11_bush[0] + 0.3, $fn = 48);
    translate([0, -(ec11_bush[0] + 0.3) / 2]) square([20, ec11_bush[0] + 0.3]);   // rotated: +local x = -z (down)
  }
}
module tongue2d(grow = 0) offset(delta = grow) polygon([[y_key_start + 0.4, pz0 - tongue_h], [y_key_start + 0.4, pz0 + 0.01], [y_key_start, pz0 + 0.01], [y_key_start - tongue_h, pz0 - tongue_h]]);   // root 0.3 into the panel
// lips that tuck under the panels' ends and hold the frame down: 45 deg tops (they print cap down),
// the head one steeper for the 8 deg bend
lip_x = [-10, -3];
module frame_lips() {
  translate([lip_x[0], 0, 0]) rotate([90, 0, 90]) linear_extrude(lip_x[1] - lip_x[0])
    polygon([[y_key_start - 0.5, pz0 - 1.5], [y_key_start - 0.5, pz0 - 0.05], [y_key_start, pz0 - 0.05], [y_key_start + 1.45, pz0 - 1.5]]);
  head_xf() translate([lip_x[0], 0, 0]) rotate([90, 0, 90]) linear_extrude(lip_x[1] - lip_x[0])
    polygon([[y_head_end + 0.5, pz0 - 1.5], [y_head_end + 0.5, pz0 - 0.05], [y_head_end, pz0 - 0.05], [y_head_end - 1.0, pz0 - 1.5]]);
}
module frame() difference() {
  union() { frame_cap(); frame_walls(); bulkhead(); frame_lips(); }
  translate([whl_x - win[0] / 2, cy - win[1] / 2, cap_z - 1]) cube([win[0], win[1], 10]);   // wheel window
  wheel_room();
  // wire notches, open at the bottom: the battery / inter-board bundle on -x (through both end
  // walls), the roller's on +x (key end only)
  translate([-15.3, -50, -1]) cube([5.3, 400, 11.2 + 1]);
  translate([13.2, room_y1 - 1, -1]) cube([2.3, 10, 12.0 + 1]);
  translate(concat(bpos(mic_b), [bb_top - 0.5])) cylinder(d = mic_mod[0] + 1.0, h = mic_mod[1] + 1.2, $fn = 64);   // the mic module overhangs the board's top edge
}

// ---------- ridge: a finger-rest hump ----------
// The body's own cross-section with its lower part let down by hump_d(y): the back bulges smoothly
// below the wheel and the sides keep the body's curve. At the head end it starts with a 1.4 step under
// the head's back edge and rounds to full depth in 4; the plateau carries the grip pad; towards the
// bottom it tapers out over 13 under the key half's back.
ridge_in = e_in(0);
hy0 = head_face_y(0) - 0.3;  hya = hy0 + 3.6;  hyp = y_key_start - 3;  hy1 = y_key_start + 10;
function hump_d(y) = y < hy0 ? 0 : y < hya ? 1.4 + (ridge_h - 1.4) * sin(90 * (y - hy0) / (hya - hy0))
  : y < hyp ? ridge_h : y < hy1 ? 1.2 + (ridge_h - 1.2) * 0.5 * (1 + cos(180 * (y - hyp) / (hy1 - hyp))) : 0;   // a 1.2 lip at the end, no knife edge
// the head tenons' bottom (the head's back plane) in key coordinates, at y
function tenon_bot(y) = T * (1 - cos(theta)) - (y - (y_head_end - T * sin(theta))) * tan(theta);
function sec_in(z, d) = z < eb - d ? e_in(z + d) : z < roll_z ? 0 : e_in(z);
module section2d(d) let(zs = concat([for (i = [0 : 24]) -d + eb * i / 24], [for (i = [1 : 10]) roll_z + (T - roll_z) * i / 10]))
  polygon(concat([for (z = zs) [W / 2 - sec_in(z, d), z]], [for (i = [len(zs) - 1 : -1 : 0]) [-(W / 2 - sec_in(zs[i], d)), zs[i]]]));
hys = concat([for (i = [0 : 8]) hy0 + (hya - hy0) * i / 8], [hyp], [for (i = [1 : 16]) hyp + (hy1 - hyp) * i / 16]);
module hslice(y) translate([0, y, 0]) rotate([90, 0, 0]) linear_extrude(0.01, center = true) section2d(hump_d(y));
module hump_env() for (i = [0 : len(hys) - 2]) hull() { hslice(hys[i]); hslice(hys[i + 1]); }
// the grip pad: flat, on the plateau, over the 4 screws; 4 pegs press into the recess floor
pad = [45.2, hyp - hya - 0.05, 2.0];  pad_c = [0, (hya + hyp) / 2];
pegs = [for (sx = [-1, 1], y = [hya + 3, hyp - 3]) [sx * 12, y]];
module pad2d(g = 0) translate(pad_c) rr2d(pad[0] + 2 * g, pad[1] + 2 * g, pad[2] + g);
module grip_pad() {   // assembled position
  translate([0, 0, -ridge_h]) linear_extrude(pad_t - 0.1) pad2d(-0.15);
  for (p = pegs) translate([p[0], p[1], -ridge_h + pad_t - 0.11]) cylinder(d = 2.0, h = 1.0, $fn = 24);
}
module ridge() difference() {
  intersection() { hump_env(); translate([-60, hy0 - 1, -20]) cube([120, hy1 - hy0 + 2, 20]); }   // below the back only
  // flat-roofed pockets (the ridge prints upside down, so these roofs are short bridges): the wheel's
  // well, and the head tenons' dip in 1.25 steps
  translate([whl_x - whl_w / 2 - whl_gap, cy - 4.9, whl_well]) cube([whl_w + 2 * whl_gap, 9.8, -whl_well + 0.01]);
  for (sx = [-1, 1], i = [0 : 8]) let(ya = hy0 + 1.25 * i, zb = tenon_bot(ya + 1.25) - 0.15, x0 = rail_x - 0.15, x1 = W / 2 - e_in(1.2) - 2.55 + 0.15)   // the bend tips the tenon's clip: below the key back it reaches the clip at head z ~1.1
    if (zb < 0) translate([sx > 0 ? x0 : -x1, ya, zb]) cube([x1 - x0, 1.25, -zb + 0.01]);
  translate([0, 0, -ridge_h - 1]) linear_extrude(1 + pad_t) pad2d();                          // grip pad recess
  for (p = pegs) translate([p[0], p[1], -ridge_h + pad_t - 0.01]) cylinder(d = 2.2, h = 1.2, $fn = 24);
  for (p = concat(s1, s2)) translate([p[0], p[1], -ridge_h + pad_t]) m2_csk(30);         // heads under the pad
}
