// umote v5 CONCEPT B (throwaway spike): N9-style colour-through unibody + flush dark face panel.
// The body is one piece, printed back-down. The face panel carries the boards and drops in from
// the front (the N9's "inside-out" assembly); screws from the back pull it into the rim.
view = "p_body";
$fn = 48;
W = 51;  L = 206.03;  T = 15.8;  tip_r = 3.5;  corner_r = 9;
ea = 3.0;  eb = 7.0;  bed_ch = 0.57;     // lower edge: as concept A (clears the 46 mm battery)
roll_z = 10.8;  roll = 2.2;              // upper edge rolls in 2.2 mm over the top 5 mm (41 deg at the rim)
land = 1.4;                              // body-colour land round the panel
pcl = 0.15;  pan_t = 1.6;

module base2d() { hull() {
  for (sx = [-1, 1]) translate([sx * (W / 2 - tip_r), tip_r]) circle(r = tip_r);
  for (sx = [-1, 1]) translate([sx * (W / 2 - corner_r), L - corner_r]) circle(r = corner_r);
} }
module plan(i) { if (i <= 0) base2d(); else offset(r = -i) base2d(); }
function e_in(z) = z < bed_ch ? 1.82 + (bed_ch - z)
  : z < eb ? ea * (1 - sqrt(1 - pow((eb - z) / eb, 2)))
  : z < roll_z ? 0 : roll * pow((z - roll_z) / (T - roll_z), 2);
module slab(z0, z1, i0, i1) { hull() { translate([0, 0, z0]) linear_extrude(0.01) plan(i0); translate([0, 0, z1 - 0.01]) linear_extrude(0.01) plan(i1); } }
module stack(z0, z1, n, extra) { for (k = [0 : n - 1]) { a = z0 + (z1 - z0) * k / n; b = z0 + (z1 - z0) * (k + 1) / n; slab(a, b, e_in(a) + extra, e_in(b) + extra); } }
module envelope() { union() { slab(0, bed_ch, e_in(0), e_in(bed_ch)); stack(bed_ch, eb, 12, 0); slab(eb, roll_z, 0, 0); stack(roll_z, T, 10, 0); } }

// ---- face features (same positions as remote_case.scad)
bb_w = 43;  bb_y0 = 82.83;
function bpos(b) = [bb_w / 2 - b[0], bb_y0 + b[1]];
dc = bpos([21.5, 25.5]);
ring_in = 6.3;  ring_out = 17.5;  ring_web = 2.2;
singles = [[7.5, 6], [8.5, 50], [21.5, 50], [34.5, 50], [8.5, 77], [8.5, 90], [21.5, 83.5], [34.5, 77], [34.5, 90]];
win_w = 37.2;  win_l = 50;  win_c = 42.33;
module rr2d(w, l, r) { offset(r = r) square([w - 2 * r, l - 2 * r], center = true); }
module ring2d(g = 0) { difference() {
  circle(r = ring_out + g, $fn = 128); circle(r = ring_in - g, $fn = 96);
  for (a = [45 : 90 : 315]) rotate(a) translate([0, -(ring_web / 2 - g)]) square([ring_out + 5, ring_web - 2 * g]);
} }
acc_in = ring_out;  acc_out = ring_out + 1.5;

pz0 = T - pan_t;
module panel_zone(extra) { stack(pz0, T + 0.01, 4, land + extra); }
module body() { difference() {
  envelope();
  translate([0, 0, 1.6]) linear_extrude(roll_z - 1.6 + 0.01) plan(2.0);        // cavity (vertical inner wall)
  stack(roll_z, pz0 + 0.01, 6, 1.8);                                           // follows the roll
  panel_zone(0);
  for (y = [20, L - 30]) translate([0, y, -0.01]) linear_extrude(0.8) rr2d(30, 8, 3.5);
} }
module panel() { difference() {
  panel_zone(pcl);
  translate([0, win_c, T - 3]) linear_extrude(5) rr2d(win_w, win_l, 1.5);
  translate(concat(dc, [T - 3])) cylinder(r = acc_out + 0.1, h = 5, $fn = 128);
  for (b = singles) translate(concat(bpos(b), [T - 3])) cylinder(d = 9.5, h = 5);
  for (dx = [-1.6 : 1.6 : 1.6]) translate(concat(bpos([34, 7]) + [dx, 0], [T - 3])) hull() for (dy = [-0.9, 0.9]) translate([0, dy, 0]) cylinder(d = 0.9, h = 5, $fn = 12);
} }
module accent() { translate(concat(dc, [T - 1.6 - 0.8])) difference() {
  union() { cylinder(r = acc_out, h = 1.6 + 0.8 + 0.2, $fn = 128); cylinder(r = acc_out + 1.2, h = 0.8, $fn = 128); }
  translate([0, 0, -1]) cylinder(r = acc_in, h = 5, $fn = 128);
} }
module caps() {
  for (i = [0 : 3]) translate(concat(dc, [T - 1.6])) linear_extrude(1.6 + 2.2) intersection() { offset(r = -0.45) ring2d(); rotate(i * 90) polygon([[0, 0], [40, -40], [40, 40]]); }
  translate(concat(dc, [T - 1.6])) cylinder(d = 9.7, h = 1.6 + 2.2);
  for (b = singles) translate(concat(bpos(b), [T - 1.6])) { cylinder(d = 8.6, h = 1.6 + 2.4); translate([0, 0, 1.6 + 2.4]) cylinder(d1 = 8.6, d2 = 7.4, h = 0.6); }
}
module screen() { translate([0, win_c, T - 0.35]) linear_extrude(0.3) rr2d(win_w + 0.2, win_l + 0.2, 1.5); }
module feet() { for (y = [20, L - 30]) translate([0, y, -0.6]) linear_extrude(1.4) rr2d(29.6, 7.6, 3.3); }

if (view == "p_body") body();
if (view == "p_panel") panel();
if (view == "p_accent") accent();
if (view == "p_caps") caps();
if (view == "p_screen") screen();
if (view == "p_feet") feet();
