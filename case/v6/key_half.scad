// umote case v6: key half (button board + battery) body and face panel. Assembled = model coordinates.
// The body runs from the head's end plane: through the wheel zone it is two solid rails (|x| >=
// rail_x, under the frame's cap) that take the head's tenons; past y_key_start it is the shell with
// a solid 2.0 floor. The battery goes in from the front (panel off, board lifted with it).

batt_end = batt_y0 + batt[1];
bb_end = bb_y0 + bb_l;
y_inner_end = L - end_wall;
bz_top = 6.0;                       // the floor is solid up to here past the battery (bottom zone)
pad_x = 3.5;  pad_z = 7.9;          // brass-insert contact pads in the bottom end
dmag_x = 12.5;  dmag_z = 7.3;     // 12.5 (11 in v5): 1.9 between a magnet and a pad hole         // dock magnets in the bottom end wall (axis along y)
end_block_y = L - 6.6;               // 1.2 in front of the pad inserts (5.0 deep from the end face)
eye = [-20.0, L - 5.0, 4.0];        // strap eyelet: in through the end face (along y), out through the back (along z)
clip_y = [bb_y0 + 20, bb_y0 + 100];  clip_w = 6;
stop_y = bb_end + 0.1;
ps = [for (sx = [-1, 1]) [sx * 19, bb_end + 2.5]];   // the key panel's 2 screws
ps_boss = [5.0, 4.5];               // panel boss d, length below the panel

// the key half's own region: past the head's end plane
module past_head_plane() head_xf() translate([-100, y_head_end, -100]) cube([200, 400, 300]);
module head_xf_inv() translate([0, y_head_end, T]) rotate([theta, 0, 0]) translate([0, -y_head_end, -T]) children();

// straight 2.4 walls up to the panel: the opening stays 47.2 wide, so the battery goes in from the
// front (the outer roll thins the wall to ~1.6 at its top edge)
module key_cavity() intersection() {
  translate([0, 0, floor_t]) linear_extrude(pz0 - floor_t + 0.01) plan(wall);
  translate([-60, y_key_start, -1]) cube([120, L - y_key_start - end_wall + 0.01 + 1, 40]);
}
// horizontal holes, teardrop roofs (+z)
module td_y(d, y0, y1) translate([0, y0, 0]) rotate([-90, 0, 0]) linear_extrude(y1 - y0)
  polygon(concat([for (k = [0 : 23]) let(t = -38.7 + 257.4 * k / 23) [d / 2 * cos(t), d / 2 * sin(t)]], [[0, -d / 2 * 1.6]]));
module td_x(d, x0, x1) translate([x0, 0, 0]) rotate([0, 90, 0]) linear_extrude(x1 - x0)
  polygon(concat([for (k = [0 : 23]) let(t = 231.3 + 257.4 * k / 23) [d / 2 * cos(t), d / 2 * sin(t)]], [[-d / 2 * 1.6, 0]]));
// magnet pocket: ends min_skin inside the end face at its top (the face rolls in above roll_z)
mag_y1 = L - min_skin - max(e_in(dmag_z + magnet[0] / 2 + 0.1), e_in(dmag_z - magnet[0] / 2 - 0.1)) - 0.2;
end_top = pz0 - 0.05;               // end block top: the panel's bottom end rests on it
module key_body() { difference() {
  union() {
    difference() {
      intersection() { envelope(); past_head_plane(); }
      // the wheel zone: only the rails stay, under the cap
      translate([-rail_x, -10, -1]) cube([2 * rail_x, y_key_start + 10, 40]);
      translate([-60, -10, cap_z]) cube([120, y_key_start + 10, 40]);
      key_cavity(); translate([-60, -10, pz0]) cube([120, L + 20, 20]);   // the panel is the top pan_t
    }
    intersection() { translate([0, 0, -1]) linear_extrude(T) plan(wall - 0.01);
      union() {
        translate([-30, batt_end + 0.5, floor_t - 0.01]) cube([60, 30, bz_top - floor_t]);              // bottom-zone floor
        translate([-19.5, end_block_y, bz_top - 0.01]) cube([39, 10, end_top - bz_top]);                    // end block: pads + magnets
        translate([-30, L - 9.5, bz_top - 0.01]) cube([30 - 17.5, 10, 12 - bz_top]);                    // eyelet pillar (-x corner)
        for (p = ps) translate([p[0], p[1], floor_t - 0.01]) cylinder(d = ps_boss[0], h = pz0 - ps_boss[1] - 0.3 - floor_t + 0.01, $fn = 40);
      } }
  }
  // slots for the head's tenons (0.15 round them), opened down through the rails' bottom (the ridge
  // closes them) by an extension kept 2.4 inside the outer surface
  tenons_xf(0.15);
  for (sx = [-1, 1]) intersection() {
    hull() { head_xf() tenon_one(sx, 0.15); translate([0, 0, -3]) head_xf() tenon_one(sx, 0.15); }
    union() { env_inset(2.4); translate([0, 0, -5]) linear_extrude(5.01) plan(e_in(0) + 2.4); }
  }
  for (g = groove_x) translate([g[0] - 0.2, 0, 0]) rotate([90, 0, 90]) linear_extrude(g[1] - g[0] + 0.4) {
    tongue2d(0.15); translate([y_key_start - 1.2, pz0 - 1.2]) square([1.5, 2]); }   // the key panel's tongues; no feathered rail edge above them (the cap covers it)
  for (p = ps) translate([p[0], p[1], pz0 - ps_boss[1] - 0.3]) cylinder(d = ps_boss[0] + 0.6, h = 10, $fn = 40);              // the panel's bosses
  translate([0, 0, pz0 - cap_flange - 0.7]) linear_extrude(5) offset(r = 0.3) key_collars2d();                              // the cap collars under the panel
  for (p = s2) translate([p[0], p[1], -1]) cylinder(d = m2[0], h = 1 + 8, $fn = 24);                 // the ridge's screws, self-tapping
  for (p = ps) translate([p[0], p[1], 0]) m2_csk(30);
  for (sx = [-1, 1]) {
    translate([sx * pad_x, 0, pad_z]) { td_y(pad_insert[0], L - pad_insert[1], L + 1); td_y(2.0, end_block_y - 1, L - pad_insert[1] + 0.1); }
    translate([sx * dmag_x, 0, dmag_z]) intersection() { td_y(magnet[0] + 0.2, end_block_y - 0.1, mag_y1);
      translate([-10, end_block_y - 1, -10]) cube([20, 10, end_top - 1.4 - dmag_z + 10]); }   // flat roof, 1.4 under the block top
  }
  translate([eye[0], 0, eye[2]]) td_y(2.2, eye[1] - 1.1, L + 2);
  translate([eye[0], eye[1], -1]) cylinder(d = 2.2, h = eye[2] + 1, $fn = 24);
} }

// ---------- key face panel ----------
module key_face_cuts() {
  translate(concat(dc, [pz0 - 1])) cylinder(r = acc_out + 0.1, h = pan_t + 2, $fn = 192);
  for (a = ring_tabs) translate(concat(dc, [0])) rotate(a - ring_tab_arc / 2 - 0.1 * 10) translate([0, 0, pz0 - 0.01]) ring_tab(0.1);
  for (k = round_keys) translate(concat(bpos(singles[k]), [pz0 - 3])) {
    cylinder(d = cap_hole, h = 10);
    rotate(rib_a(k)) translate([-(rib_w + 2 * rib_clr) / 2, -(cap_d / 2 + rib_out + rib_clr), 0]) cube([rib_w + 2 * rib_clr, cap_d / 2, 3 + pan_t - rib_skin]);
    translate([0, 0, pan_t + 3 - 0.4]) cylinder(d1 = cap_hole, d2 = cap_hole + 0.86, h = 0.43);
  }
  for (p = [vol, ch]) {
    translate([0, 0, pz0 - 1]) linear_extrude(pan_t + 2) capsule2d(p, cap_hole);
    translate([0, 0, T - 0.4]) hull() { linear_extrude(0.01) capsule2d(p, cap_hole); translate([0, 0, 0.43]) linear_extrude(0.01) capsule2d(p, cap_hole + 0.86); }
  }
  for (dx = [-2.1 : 2.1 : 2.1]) translate(concat(bpos(mic_b) + [dx, 0], [pz0 - 1])) hull() for (dy = [-0.9, 0.9]) translate([0, dy, 0]) cylinder(d = 0.9, h = pan_t + 2, $fn = 16);
  for (g = [0, 1]) difference() {
    hull() { translate([0, 0, T - 0.4]) linear_extrude(0.01) group2d(g, 0.4); translate([0, 0, T]) linear_extrude(0.02) group2d(g, 0.75); }
    hull() { translate([0, 0, T - 0.41]) linear_extrude(0.01) group2d(g, 0.4); translate([0, 0, T + 0.01]) linear_extrude(0.02) group2d(g, 0.05); }
  }
}
module group2d(g, grow) offset(delta = grow) {
  if (g == 0) hull() { translate(dc) circle(r = acc_out + 2.2, $fn = 128); for (k = [1, 3]) translate(bpos(singles[k])) circle(d = cap_hole + 3.4); }
  else offset(r = 2.0) hull() { capsule2d(vol, cap_hole); capsule2d(ch, cap_hole); }
}
module key_collars2d() union() {
  translate(dc) circle(r = ring_out + 1.5, $fn = 192);
  for (k = round_keys) translate(bpos(singles[k])) circle(d = flange_d + 2 * flange_clr + 2.4);
  for (p = [vol, ch]) capsule2d(p, flange_d + 2 * flange_clr + 2.4);
}
// 2D: the collar ring round each pocket, clipped to the panel's end, then opened by 1.2 so no web
// thinner than 3 lines is left (the D-pad's wall meets the HOME and POWER pockets nearly tangent)
module key_collars() translate([0, 0, pz0 - cap_flange - 0.4]) linear_extrude(cap_flange + 0.45)
  offset(r = 0.6) offset(delta = -0.6) intersection() {
    difference() {
      union() { key_collars2d(); translate(dc) circle(r = acc_out + 0.1 + 1.2, $fn = 192); }   // the D-pad's outer wall 1.2 (0.5 in v5)
      translate(dc) circle(r = acc_out + 0.1, $fn = 192);
      for (k = round_keys) translate(bpos(singles[k])) circle(d = flange_d + 2 * flange_clr);
      for (p = [vol, ch]) capsule2d(p, flange_d + 2 * flange_clr);
    }
    translate([-50, y_key_start + 0.2]) square([100, L]);
  }
module board_clip() {
  len = pz0 - bb_z0 + 0.5;
  translate([0, -clip_w / 2, 0]) rotate([90, 0, 0]) mirror([0, 0, 1]) linear_extrude(clip_w)
    polygon([[0, 0], [1.0, 0], [1.0, -len], [-0.6, -len + 0.0], [-0.6, -len + 0.5], [0, -len + 1.1]]);
}
module key_panel() { difference() {
  union() {
    panel_cap(y_key_start + 0.1, L + 1);
    key_collars();
    for (y = clip_y) for (sx = [-1, 1]) mirror([sx > 0 ? 0 : 1, 0, 0]) translate([bb_w / 2 + 0.1, y, pz0 + 0.01]) board_clip();
    for (sx = [-1, 1]) translate([sx * 6 - 3, stop_y, bb_z0 + 0.5]) cube([6, 1.5, pz0 - bb_z0 - 0.45]);
    for (p = ps) translate([p[0], p[1], pz0 - ps_boss[1]]) cylinder(d = ps_boss[0], h = ps_boss[1] + 0.01, $fn = 40);
    rk_fulcrums();
    for (g = groove_x) translate([g[0], 0, 0]) rotate([90, 0, 90]) linear_extrude(g[1] - g[0]) tongue2d(0);
  }
  key_face_cuts();
  for (p = ps) translate([p[0], p[1], pz0 - ps_boss[1] - 0.01]) cylinder(d = m2[0], h = 4.0, $fn = 24);
} }
