// umote v5 CONCEPT D (throwaway spike): everything the user kept.
// N9 profile (flush dark face panel, rolled upper edge, curved back) + 8110 bend at the board gap
// + 7110 Navi-roller in the crease + VOL/CH rockers + key islands + raised D-pad rim + OK nub
// + strap eyelet + magnet/dock plate over the screws + pogo pads in the bottom end.
include <concept_n9.scad>
view = "d_none";
theta = 8;  y_cut = 78.83;  shift = 8;  y_b0 = y_cut + 2;     // body starts at old y 80.83
whl_d = 12;  whl_w = 18;  whl_proud = 1.2;
module head_xf() { translate([0, y_cut, T]) rotate([-theta, 0, 0]) translate([0, -y_cut, -T]) children(); }
module body_xf() { translate([0, shift, 0]) children(); }
module ycut(y0, y1) { intersection() { children(); translate([-60, y0, -10]) cube([120, y1 - y0, 40]); } }

vol = [bpos(singles[4]), bpos(singles[5])];  ch = [bpos(singles[7]), bpos(singles[8])];
round_keys = [0, 1, 2, 3, 6];                                   // POWER BACK HOME VOICE MUTE
module capsule(p, d) { hull() for (q = p) translate(q) circle(d = d); }
module nav_island() { hull() { translate(dc) circle(r = 20.2, $fn = 128); for (k = [1, 3]) translate(bpos(singles[k])) circle(d = 13); } }
module media_island() { offset(r = 2.2) hull() { capsule(vol, 9.5); capsule(ch, 9.5); } }

module panel_d() { difference() {
  panel_zone(pcl);
  translate([0, win_c, T - 3]) linear_extrude(5) rr2d(win_w, win_l, 1.5);
  translate(concat(dc, [T - 3])) cylinder(r = acc_out + 0.1, h = 5, $fn = 128);
  for (k = round_keys) translate(concat(bpos(singles[k]), [T - 3])) cylinder(d = 9.5, h = 5);
  translate([0, 0, T - 3]) linear_extrude(5) { capsule(vol, 9.5); capsule(ch, 9.5); }
  for (dx = [-1.6 : 1.6 : 1.6]) translate(concat(bpos([34, 7]) + [dx, 0], [T - 3])) hull() for (dy = [-0.9, 0.9]) translate([0, dy, 0]) cylinder(d = 0.9, h = 5, $fn = 12);
  translate([0, 0, T - 0.5]) linear_extrude(1) { nav_island(); media_island(); }   // 0.5 mm wells
} }
module accent_d() { translate(concat(dc, [T - 1.6 - 0.8])) difference() {     // stands 0.5 proud of the face
  union() { cylinder(r = acc_out, h = 1.6 + 0.8 + 0.5, $fn = 128); cylinder(r = acc_out + 1.2, h = 0.8, $fn = 128); }
  translate([0, 0, -1]) cylinder(r = acc_in, h = 5, $fn = 128);
} }
module caps_d() {
  for (i = [0 : 3]) translate(concat(dc, [T - 1.6])) linear_extrude(1.6 + 2.2) intersection() { offset(r = -0.45) ring2d(); rotate(i * 90) polygon([[0, 0], [40, -40], [40, 40]]); }
  translate(concat(dc, [T - 1.6])) { cylinder(d = 9.7, h = 1.6 + 2.2); translate([0, 0, 1.6 + 2.2]) sphere(d = 1.6, $fn = 24); }   // OK + nub
  for (k = round_keys) translate(concat(bpos(singles[k]), [T - 1.6 - (k == 6 ? 0 : 0)])) {
    cylinder(d = 8.6, h = 1.6 + 2.4); translate([0, 0, 1.6 + 2.4]) cylinder(d1 = 8.6, d2 = 7.4, h = 0.6);
  }
  for (p = [vol, ch]) difference() {                               // rockers: one cap over each pair
    translate([0, 0, T - 1.6]) linear_extrude(1.6 + 2.8) capsule(p, 8.6);
    translate([(p[0][0] + p[1][0]) / 2, (p[0][1] + p[1][1]) / 2, T + 1.2 + 9]) rotate([0, 90, 0]) cylinder(r = 9, h = 12, center = true, $fn = 96);   // saddle
  }
}
// strap eyelet: a bar across the bottom corner (slot through the body)
eye_c = [W / 2 - 6.5, L - 6.5];
module eyelet_cut() { translate([eye_c[0], eye_c[1], -1]) rotate(45) linear_extrude(T + 2) rr2d(5, 2.2, 1); }
module eyelet_boss() { translate([eye_c[0], eye_c[1], 1.5]) rotate(45) linear_extrude(roll_z - 1.5) rr2d(9, 6, 2); }
// magnet / dock plate: flush in the back of the key body, over the 4 screws and 4 magnets
plate_c = [0, 150];  plate_s = [38, 96];
module plate_cut() { translate([plate_c[0], plate_c[1], -0.01]) linear_extrude(1.2) rr2d(plate_s[0] + 0.3, plate_s[1] + 0.3, 6); }
module plate()     { translate([plate_c[0], plate_c[1], 0]) linear_extrude(1.2) rr2d(plate_s[0], plate_s[1], 6); }
module body_d() { difference() { union() { body(); intersection() { envelope(); eyelet_boss(); } } eyelet_cut(); plate_cut();
  for (sx = [-1, 1]) translate([sx * 5, L - 0.6, 5]) rotate([-90, 0, 0]) cylinder(d = 3.2, h = 2, $fn = 24);   // pogo pad recesses
} }
module pogo() { for (sx = [-1, 1]) translate([sx * 5, L - 0.6, 5]) rotate([-90, 0, 0]) cylinder(d = 2.8, h = 0.55, $fn = 24); }

// crease collar (accent), houses the roller
module prof(y) { translate([0, y, 0]) rotate([90, 0, 0]) linear_extrude(0.01) projection(cut = true) rotate([-90, 0, 0]) translate([0, -y, 0]) envelope(); }
module inner(y) { translate([0, y, 0]) rotate([90, 0, 0]) linear_extrude(0.01) translate([0, 1.6 + (T - 3.2) / 2]) square([47, T - 3.2], center = true); }
cy = (y_cut + y_b0 + shift) / 2;
module collar() { difference() {
  hull() { head_xf() prof(y_cut); body_xf() prof(y_b0); }
  hull() { head_xf() translate([0, -0.5, 0]) inner(y_cut); body_xf() translate([0, 0.5, 0]) inner(y_b0); }
  translate([0, cy - 0.3, T - whl_d / 2 + whl_proud]) rotate([0, 90, 0]) cylinder(d = whl_d + 0.8, h = whl_w + 0.8, center = true);
} }
module wheel() { translate([0, cy - 0.3, T - whl_d / 2 + whl_proud]) rotate([0, 90, 0]) difference() {
  cylinder(d = whl_d, h = whl_w, center = true, $fn = 64);
  for (a = [0 : 12 : 359]) rotate(a) translate([whl_d / 2, 0, 0]) cube([0.8, 0.9, whl_w + 1], center = true);
} }

if (view == "d_head_body")  head_xf() ycut(-1, y_cut) union() { body(); intersection() { envelope(); translate([0, 20, -0.1]) linear_extrude(1) rr2d(31, 9, 3.6); } }
if (view == "d_head_panel") head_xf() ycut(-1, y_cut) panel_d();
if (view == "d_head_screen") head_xf() screen();
if (view == "d_body")   body_xf() ycut(y_b0, L + 1) body_d();
if (view == "d_panel")  body_xf() ycut(y_b0, L + 1) panel_d();
if (view == "d_accent") body_xf() accent_d();
if (view == "d_caps")   body_xf() caps_d();
if (view == "d_plate")  body_xf() plate();
if (view == "d_pogo")   body_xf() pogo();
if (view == "d_collar") collar();
if (view == "d_wheel")  wheel();
// ---- internals for the assembly steps (simple solids at their real positions)
module tongues() {
  // head: a fork from the collar with two standoffs under the display board's antenna-end holes
  head_xf() { translate([-21, 76.9, 1.6]) cube([42, y_cut - 76.9 + 0.5, 1.8]);
    for (sx = [-1, 1]) { translate([sx * 17.45, 72.83, 1.6]) cylinder(d = 5.2, h = 8.46 - 1.6, $fn = 32);
      hull() { translate([sx * 17.45, 72.83, 1.6]) cylinder(d = 5.2, h = 1.8, $fn = 32); translate([sx * 17.45 - 2.6, 76.9, 1.6]) cube([5.2, 0.1, 1.8]); } } }
  // key: a plate on the key floor; the two back screws clamp floor + plate + face-panel bosses
  body_xf() translate([-21, y_b0 - 0.5, 1.6]) cube([42, 7, 1.8]);
}
module tongue_screws() {
  head_xf() for (sx = [-1, 1]) for (y = [6.5, 72.83]) translate([sx * 17.45, y, 10.06]) cylinder(d = 4.2, h = 1.2, $fn = 24);   // board screws
  body_xf() for (sx = [-1, 1]) translate([sx * 14, y_b0 + 3, 3.4]) cylinder(d = 4.2, h = 1.2, $fn = 24);                  // tongue to key floor
}
module disp() head_xf() { translate([-21.45, 2.5, 8.46]) cube([42.89, 74.33, 1.6]); translate([-21.3, 10.49, 10.06]) cube([42.6, 60, 3.84]); translate([-20.9, 3.5, 3.9]) cube([41.8, 72, 4.56]); }
module bboard() body_xf() translate([-21.5, bb_y0, 7.9]) cube([43, 112, 1.6]);
module batt()   body_xf() translate([-23, 88, 2.1]) cube([46, 105, 5]);
module roller_mod() translate([-11, cy - 6.3, 3.5]) cube([22, 12.6, 1.4]);
module key_screws() body_xf() for (sx = [-1, 1]) for (y = [L - 5.5]) translate([sx * 13, y, 0.3]) cylinder(d = 4.6, h = 13.4, $fn = 24);
if (view == "d_tongues") tongues();
if (view == "d_tscrews") tongue_screws();
if (view == "d_disp") disp();
if (view == "d_bboard") bboard();
if (view == "d_batt") batt();
if (view == "d_rmod") roller_mod();
if (view == "d_kscrews") key_screws();
