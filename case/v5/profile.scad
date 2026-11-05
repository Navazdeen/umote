// umote case v5: the outer form only (plan outline, cross-section, bend). Include after params.scad.

module base2d() { hull() {
  for (sx = [-1, 1]) translate([sx * (W / 2 - tip_r), tip_r]) circle(r = tip_r);
  for (sx = [-1, 1]) translate([sx * (W / 2 - corner_r), L - corner_r]) circle(r = corner_r);
} }
module plan(i = 0) { if (i <= 0) base2d(); else offset(r = -i) base2d(); }
module rr2d(w, l, r) { offset(r = r) square([w - 2 * r, l - 2 * r], center = true); }

// plan inset of the outer surface at height z: a 45 deg foot, the lower quarter ellipse into the
// flat back, the straight band, then the upper roll round the face panel
function e_in(z) = z < bed_ch ? 1.82 + (bed_ch - z)
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
module envelope() { union() {
  slab(0, bed_ch, e_in(0), e_in(bed_ch));
  stack(bed_ch, eb, 12);
  slab(eb, roll_z, 0, 0);
  stack(roll_z, T, 10);
} }
// the face-panel opening: the envelope's roll moved in by the land
module panel_zone(extra = 0) { stack(pz0, T + 0.01, 4, land + extra); }

// the bend: the head turns theta about a transverse axis on the face at the head end, face concave
module head_xf() { translate([0, y_head_end, T]) rotate([-theta, 0, 0]) translate([0, -y_head_end, -T]) children(); }
module ycut(y0, y1) { intersection() { children(); translate([-60, y0, -20]) cube([120, y1 - y0, 60]); } }
