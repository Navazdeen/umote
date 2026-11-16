// umote case v7: the outer form (plan outline, cross-section, the keel). Include after params.scad.

module base2d() { hull() {
  for (sx = [-1, 1]) translate([sx * (W / 2 - tip_r), tip_r]) circle(r = tip_r);
  for (sx = [-1, 1]) translate([sx * (W / 2 - corner_r), L - corner_r]) circle(r = corner_r);
} }
module plan(i = 0) { if (i == 0) base2d(); else offset(r = -i) base2d(); }   // negative i grows it
module rr2d(w, l, r) { offset(r = r) square([w - 2 * r, l - 2 * r], center = true); }

// plan inset of the outer surface. Below eb: z is the height above the local back (a 35 deg bed
// foot, then a quarter ellipse into the side). From roll_z up: the roll round the face.
foot_in = ea * (1 - sqrt(1 - pow((eb - bed_ch) / eb, 2)));
function e_in(z) = z < bed_ch ? foot_in + foot_k * (bed_ch - z)
  : z < eb ? ea * (1 - sqrt(1 - pow((eb - z) / eb, 2)))
  : z < roll_z ? 0 : roll * pow((z - roll_z) / (T - roll_z), 2);

// one hull between two plan slices; a stack of them follows e_in() (each band is convex)
module slab(z0, z1, i0, i1) { hull() {
  translate([0, 0, z0]) linear_extrude(0.01) plan(i0);
  translate([0, 0, z1 - 0.01]) linear_extrude(0.01) plan(i1);
} }
module stack(z0, z1, n, extra = 0) {
  for (k = [0 : n - 1]) { a = z0 + (z1 - z0) * k / n; b = z0 + (z1 - z0) * (k + 1) / n;
    slab(a, b, e_in(a) + extra, e_in(b) + extra); }
}
// the lower half standing on z = 0: the bed foot and the ellipse, then straight up. Sheared along y
// it becomes the head's or the key half's back: vertical lines stay vertical, so the outline and the
// walls are untouched and every cross-section is the same shape let down by zb(y).
module cup(g = 0) union() {
  slab(-g, bed_ch, e_in(0) - g, e_in(bed_ch) - g);
  stack(bed_ch, eb, 12, -g);
  translate([0, 0, eb - 0.01]) linear_extrude(60) plan(-g);
}
module shear_h() multmatrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, kh, 1, zb_tip], [0, 0, 0, 1]]) children();
module shear_k() multmatrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, kk, 1, z_ap - kk * y_ap], [0, 0, 0, 1]]) children();
module upper(g = 0) union() {
  translate([0, 0, -30]) linear_extrude(30 + roll_z) plan(-g);
  stack(roll_z, T, 10, -g);
  if (g > 0) slab(T - 0.01, T + g, e_in(T) - g, e_in(T) - g);
}
// the whole remote's outer form; g grows it all round (the dock's pocket)
module envelope(g = 0) intersection() { upper(g); shear_h() cup(g); shear_k() cup(g); }

// everything d above the back surface (d = back_t: above the seam between the shell and the plates)
module slabs_up() translate([-100, -200, 0]) cube([200, 700, 100]);
module above_back(d) intersection() { shear_h() translate([0, 0, d]) slabs_up(); shear_k() translate([0, 0, d]) slabs_up(); }
module above_seam() above_back(back_t);
module band(d0, d1) difference() { above_back(d0); above_back(d1); }      // between two offsets of the back

// the face: the envelope's top pan_t
module ycut(y0, y1) { intersection() { children(); translate([-60, y0, -40]) cube([120, y1 - y0, 80]); } }

// horizontal holes with a teardrop roof: towards +z, or towards -z (down = true) for the shell,
// which prints face down
module td_y(d, y0, y1, down = false) translate([0, y0, 0]) rotate([-90, 0, 0]) linear_extrude(y1 - y0) mirror([0, down ? 1 : 0])
  polygon(concat([for (k = [0 : 23]) let(t = -38.7 + 257.4 * k / 23) [d / 2 * cos(t), d / 2 * sin(t)]], [[0, -d / 2 * 1.6]]));
module td_x(d, x0, x1, down = false) translate([x0, 0, 0]) rotate([0, 90, 0]) linear_extrude(x1 - x0) mirror([down ? 1 : 0, 0])
  polygon(concat([for (k = [0 : 23]) let(t = 231.3 + 257.4 * k / 23) [d / 2 * cos(t), d / 2 * sin(t)]], [[-d / 2 * 1.6, 0]]));
