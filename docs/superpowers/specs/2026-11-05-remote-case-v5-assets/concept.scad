// umote v5 CONCEPT (throwaway spike for the look): two-tone face + back tub, D-pad accent ring.
// Same coordinates as case/remote_case.scad: y from the tip, z from the back face (z=0) to the front face.
view = "asm";       // asm | explode | section
$fn = 64;

W = 51;  L = 206.03;  T = 15.8;
tip_r = 3.5;  corner_r = 9;
seam_z = 11.3;            // colour break / seam, 4.5 below the face
ea = 3.0;  eb = 7.0;      // back edge: quarter ellipse (3 across, 7 up)
bed_ch = 0.57;            // 45 deg flat where the ellipse passes 45 deg (prints back-down, no overhang)
top_ch = 0.8;             // crisp front edge
gch = 0.4;                // seam chamfer on both parts -> 0.8 wide V groove

module base2d() { hull() {
  for (sx = [-1, 1]) translate([sx * (W / 2 - tip_r), tip_r]) circle(r = tip_r);
  for (sx = [-1, 1]) translate([sx * (W / 2 - corner_r), L - corner_r]) circle(r = corner_r);
} }
module plan(i) { if (i <= 0) base2d(); else offset(r = -i) base2d(); }
function e_in(z) = z < bed_ch ? 1.82 + (bed_ch - z) : (z >= eb ? 0 : ea * (1 - sqrt(1 - pow((eb - z) / eb, 2))));
module slab(z0, z1, i0, i1) { hull() { translate([0, 0, z0]) linear_extrude(0.01) plan(i0); translate([0, 0, z1 - 0.01]) linear_extrude(0.01) plan(i1); } }

module envelope() { union() {
  zs = concat([0, bed_ch], [for (k = [1 : 12]) bed_ch + (eb - bed_ch) * k / 12]);
  for (k = [0 : len(zs) - 2]) slab(zs[k], zs[k + 1], e_in(zs[k]), e_in(zs[k + 1]));
  slab(eb, T - top_ch, 0, 0);
  slab(T - top_ch, T, 0, top_ch);
} }

// ---- face features (from remote_case.scad)
bb_w = 43;  bb_y0 = 82.83;
function bpos(b) = [bb_w / 2 - b[0], bb_y0 + b[1]];
dc = bpos([21.5, 25.5]);
ring_in = 6.3;  ring_out = 17.5;  ring_web = 2.2;  ok_d = 10;
singles = [[7.5, 6, "POWER"], [8.5, 50], [21.5, 50], [34.5, 50], [8.5, 77], [8.5, 90], [21.5, 83.5], [34.5, 77], [34.5, 90]];
win_w = 37.2;  win_l = 50;  win_c = 42.33;
module rr2d(w, l, r) { offset(r = r) square([w - 2 * r, l - 2 * r], center = true); }
module ring2d(g = 0) { difference() {
  circle(r = ring_out + g, $fn = 128); circle(r = ring_in - g, $fn = 96);
  for (a = [45 : 90 : 315]) rotate(a) translate([0, -(ring_web / 2 - g)]) square([ring_out + 5, ring_web - 2 * g]);
} }
acc_in = ring_out;  acc_out = ring_out + 1.5;   // accent ring = the D-pad opening's rim (HOME hole edge is 2.25 out)

module front() { color("#e8e5de") difference() {
  intersection() { envelope(); translate([-50, -1, seam_z]) cube([100, L + 2, 20]); }
  translate([0, 0, seam_z - 1]) linear_extrude(T - 1.6 - seam_z + 1) plan(2.0);           // hollow
  translate([0, win_c, T - 3]) linear_extrude(5) rr2d(win_w, win_l, 1.5);
  translate([0, win_c, T - 1]) hull() { linear_extrude(0.01) rr2d(win_w, win_l, 1.5); translate([0, 0, 1.01]) linear_extrude(0.01) rr2d(win_w + 2, win_l + 2, 2.5); }
  translate(concat(dc, [T - 3])) cylinder(r = acc_out + 0.1, h = 5, $fn = 128);
  for (b = singles) translate(concat(bpos(b), [T - 3])) { cylinder(d = 9.5, h = 5); translate([0, 0, 2.6]) cylinder(d1 = 9.5, d2 = 10.3, h = 0.41); }
  for (dx = [-1.6 : 1.6 : 1.6]) translate(concat(bpos([34, 7]) + [dx, 0], [T - 3])) hull() for (dy = [-0.9, 0.9]) translate([0, dy, 0]) cylinder(d = 0.9, h = 5, $fn = 12);
  seam_groove();
} }
module seam_groove() {   // V groove: 0.4 chamfer on each part's outer edge at the seam
  translate([0, 0, seam_z]) difference() {
    translate([0, 0, -gch]) linear_extrude(2 * gch) offset(r = 1) base2d();
    hull() { translate([0, 0, -gch]) linear_extrude(0.01) base2d(); linear_extrude(0.01) plan(gch); }
    hull() { linear_extrude(0.01) plan(gch); translate([0, 0, gch - 0.01]) linear_extrude(0.01) base2d(); }
  }
}
module tub() { color("#2c3036") difference() {
  intersection() { envelope(); translate([-50, -1, -1]) cube([100, L + 2, seam_z + 1]); }
  translate([0, 0, 1.6]) linear_extrude(20) plan(2.0);
  seam_groove();
  // screw pockets under the two foot strips
  for (y = [20, L - 30]) translate([0, y, -0.01]) linear_extrude(0.8) rr2d(30, 8, 3.5);
}
  // feet: p_feet
}
module accent() { color("#d9772b") translate(concat(dc, [T - 1.6 - 0.8])) difference() {
  union() { cylinder(r = acc_out, h = 1.6 + 0.8 + 0.3, $fn = 128); cylinder(r = acc_out + 1.2, h = 0.8, $fn = 128); }
  translate([0, 0, -1]) cylinder(r = acc_in, h = 5, $fn = 128);
} }
module caps() {
  for (i = [0 : 3]) color("#2a2e35") translate(concat(dc, [T - 1.6])) linear_extrude(1.6 + 2.2) intersection() { offset(r = -0.45) ring2d(); rotate(i * 90) polygon([[0, 0], [40, -40], [40, 40]]); }
  color("#2a2e35") translate(concat(dc, [T - 1.6])) cylinder(d = 9.7, h = 1.6 + 2.2);
  for (k = [0 : len(singles) - 1]) color(k == 0 ? "#c94a3f" : "#2a2e35") translate(concat(bpos(singles[k]), [T - 1.6])) {
    cylinder(d = 8.6, h = 1.6 + 2.4); translate([0, 0, 1.6 + 2.4]) cylinder(d1 = 8.6, d2 = 7.4, h = 0.6);
  }
}
module screen() { color("#0d1117") translate([0, win_c, T - 1.9]) linear_extrude(0.3) rr2d(win_w + 4, win_l + 4, 1); }
module insides() {
  color("#3a7d44") translate([-21.45, 2.5, 8.46]) cube([42.89, 74.33, 1.6]);       // display PCB
  color("#3a7d44") translate([-21.5, bb_y0, 7.4]) cube([43, 112, 1.6]);             // button PCB
  color("#5b8fd9") translate([-23, 84, 2.1]) cube([46, 105, 5]);                    // LiPo 46x105x5
}

rot = 0;
rotate(rot) if (view == "asm") { tub(); front(); accent(); caps(); screen(); }
else if (view == "explode") { tub(); translate([0, 0, 22]) { front(); screen(); } translate([0, 0, 44]) accent(); translate([0, 0, 60]) caps(); }
else if (view == "section") intersection() {
  union() { tub(); front(); accent(); caps(); screen(); insides(); }
  translate([-50, 140, -5]) cube([100, 120, 40]);
}
if (view == "p_tub") tub();
if (view == "p_feet") color("#1a1c1f") for (y = [20, L - 30]) translate([0, y, -0.6]) linear_extrude(1.4) rr2d(29.6, 7.6, 3.3);
if (view == "p_front") front();
if (view == "p_accent") accent();
if (view == "p_caps") caps();
if (view == "p_screen") screen();
if (view == "p_inside") insides();
