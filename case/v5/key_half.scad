// umote case v5: key half (button board + battery) body and face panel. Assembled = model coordinates.

batt_end = batt_y0 + batt[1];
y_inner_end = L - wall;
bz_top = 6.0;                       // the floor is solid up to here past the battery (bottom zone)
pad_x = 3.5;  pad_z = 7.9;          // brass-insert contact pads in the bottom end
dmag_x = 11;  dmag_z = 7.9;         // dock magnets in the bottom end wall (axis along y)
end_block_y = 212.6;
eye = [-20.0, 212.0, 9.0];          // strap eyelet: holes meet here
clip_y = [bb_y0 + 20, bb_y0 + 100];  clip_w = 6;
stop_y = bb_y0 + bb_l + 0.1;
key_snaps = [[22.3, 198.0, 0], [22.3, 205.0, 0], [-22.3, 198.0, 180], [-22.3, 205.0, 180]];   // releasable, as the head's side snaps; clear of the eyelet pillar
door_y1 = batt_end + 0.3;           // the battery door window's bottom end (the bottom zone's floor is solid)


module key_cavity() { union() {
  translate([0, 0, floor_t]) linear_extrude(roll_z - floor_t + 0.01) plan(wall);
  stack(roll_z, T + 0.01, 8, 1.8);
} }
// a hole along y whose section points up (+z): horizontal holes in a back-down print
module td_y(d, y0, y1) translate([0, y0, 0]) rotate([-90, 0, 0]) linear_extrude(y1 - y0)
  polygon(concat([for (k = [0 : 23]) let(t = -38.7 + 257.4 * k / 23) [d / 2 * cos(t), d / 2 * sin(t)]], [[0, -d / 2 * 1.6]]));
module td_x(d, x0, x1) translate([x0, 0, 0]) rotate([0, 90, 0]) linear_extrude(x1 - x0)
  polygon(concat([for (k = [0 : 23]) let(t = 231.3 + 257.4 * k / 23) [d / 2 * cos(t), d / 2 * sin(t)]], [[-d / 2 * 1.6, 0]]));

module key_body() { difference() {
  union() {
    difference() { ycut(y_key_start, L + 1) envelope(); key_cavity(); panel_zone(0); }
    intersection() { ycut(y_key_start, L + 1) translate([0, 0, -1]) linear_extrude(T) plan(wall - 0.01);
      union() {
        translate([-30, batt_end + 0.5, floor_t - 0.01]) cube([60, 20, bz_top - floor_t]);            // bottom-zone floor
        translate([-17, end_block_y, bz_top - 0.01]) cube([34, 10, 13.4 - bz_top]);                    // end block: pads + magnets
        translate([-30, 208.5, bz_top - 0.01]) cube([30 - 17.5, 10, 12 - bz_top]);                     // eyelet pillar (-x corner)
      } }
    prongs(y_key_start, -1);
  }
  door_window();
  door_detents(0.1);
  for (s = key_snaps) translate([s[0], s[1], snap_root_z]) rotate(s[2]) catch(gap = 0.6);
  for (sx = [-1, 1]) {
    translate([sx * pad_x, 0, pad_z]) { td_y(pad_insert[0], L - pad_insert[1], L + 1); td_y(2.0, end_block_y - 1, L - pad_insert[1] + 0.1); }
    translate([sx * dmag_x, 0, dmag_z]) intersection() { td_y(magnet[0] + 0.2, end_block_y - 0.1, L - 0.6 - (L - y_inner_end - 2.2));
      translate([-10, end_block_y - 1, 0]) cube([20, 10, 13.6 - dmag_z]); translate([-10, end_block_y - 1, -10]) cube([20, 10, 30]); }
  }
  translate([0, 0, eye[2]]) { translate([0, eye[1], 0]) td_x(2.2, -W, eye[0] + 1.1); translate([eye[0], 0, 0]) td_y(2.2, eye[1] - 1.1, L + 2); }
} }

// battery door window through the back: 46.6 wide, so the battery goes in from the back
door_w = batt[0] + 0.6;
module door2d(grow = 0.15) translate([-door_w / 2 - grow, y_key_start - 1]) square([door_w + 2 * grow, door_y1 - y_key_start + 1 + grow]);
module door_window() translate([0, 0, -1]) linear_extrude(floor_t + 1.01) door2d();

// ---------- key face panel ----------
module key_face_cuts() {
  translate(concat(dc, [pz0 - 1])) cylinder(r = acc_out + 0.1, h = pan_t + 2, $fn = 192);      // D-pad + ring
  for (a = ring_tabs) translate(concat(dc, [0])) rotate(a - ring_tab_arc / 2 - 0.1 * 10) translate([0, 0, pz0 - 0.01]) ring_tab(0.1);   // tab pockets
  for (k = round_keys) translate(concat(bpos(singles[k]), [pz0 - 3])) {
    cylinder(d = cap_hole, h = 10);
    translate([-(rib_w + 2 * rib_clr) / 2, -(cap_d / 2 + rib_out + rib_clr), 0]) cube([rib_w + 2 * rib_clr, cap_d / 2, 3 + pan_t - rib_skin]);
    translate([0, 0, pan_t + 3 - 0.4]) cylinder(d1 = cap_hole, d2 = cap_hole + 0.81, h = 0.41);
  }
  for (p = [vol, ch]) {
    translate([0, 0, pz0 - 1]) linear_extrude(pan_t + 2) capsule2d(p, cap_hole);
    translate([0, 0, T - 0.4]) hull() { linear_extrude(0.01) capsule2d(p, cap_hole); translate([0, 0, 0.41]) linear_extrude(0.01) capsule2d(p, cap_hole + 0.81); }
  }
  for (dx = [-1.6 : 1.6 : 1.6]) translate(concat(bpos(mic_b) + [dx, 0], [pz0 - 1])) hull() for (dy = [-0.9, 0.9]) translate([0, dy, 0]) cylinder(d = 0.9, h = pan_t + 2, $fn = 16);
  // key groups: 0.8 x 0.4 V-grooves round the nav and media groups
  for (g = [0, 1]) difference() {            // a true V: both walls meet at offset 0.4, 0.4 deep
    hull() { translate([0, 0, T - 0.4]) linear_extrude(0.01) group2d(g, 0.4); translate([0, 0, T]) linear_extrude(0.02) group2d(g, 0.75); }   // 41 deg walls
    hull() { translate([0, 0, T - 0.41]) linear_extrude(0.01) group2d(g, 0.4); translate([0, 0, T + 0.01]) linear_extrude(0.02) group2d(g, 0.05); }
  }
}
module group2d(g, grow) offset(delta = grow) {
  if (g == 0) hull() { translate(dc) circle(r = acc_out + 2.2, $fn = 128); for (k = [1, 3]) translate(bpos(singles[k])) circle(d = cap_hole + 3.4); }
  else offset(r = 2.0) hull() { capsule2d(vol, cap_hole); capsule2d(ch, cap_hole); }
}
// cap flange collars under the face (v4): round keys keyed, rockers in capsule pockets
module key_collars() translate([0, 0, pz0 - cap_flange - 0.4]) linear_extrude(cap_flange + 0.45) difference() {
  union() {
    translate(dc) circle(r = ring_out + 1.5, $fn = 192);
    for (k = round_keys) translate(bpos(singles[k])) circle(d = flange_d + 2 * flange_clr + 2.4);
    for (p = [vol, ch]) capsule2d(p, flange_d + 2 * flange_clr + 2.4);
  }
  translate(dc) circle(r = acc_out + 0.1, $fn = 192);  // inside the D-pad hole the ring frame is the ceiling: only v4's outer wall stays
  for (k = round_keys) translate(bpos(singles[k])) circle(d = flange_d + 2 * flange_clr);
  for (p = [vol, ch]) capsule2d(p, flange_d + 2 * flange_clr);
}
// board clips: beams beside the board's long edges, hooks under it (45 deg both faces)
module board_clip() {
  len = pz0 - bb_z0 + 0.5;
  translate([0, -clip_w / 2, 0]) rotate([90, 0, 0]) mirror([0, 0, 1]) linear_extrude(clip_w)
    polygon([[0, 0], [1.0, 0], [1.0, -len], [-0.6, -len + 0.0], [-0.6, -len + 0.5], [0, -len + 1.1]]);
}
module key_panel() { difference() {
  union() {
    intersection() { panel_zone(pcl); translate([-50, y_key_start, 0]) cube([100, L, 30]); }
    intersection() { key_collars(); translate([-50, y_key_start + 0.2, 0]) cube([100, L, 30]); }
    for (y = clip_y) for (sx = [-1, 1]) mirror([sx > 0 ? 0 : 1, 0, 0]) translate([bb_w / 2 + 0.1, y, pz0 + 0.01]) board_clip();
    for (sx = [-1, 1]) translate([sx * 6 - 3, stop_y, bb_z0 + 0.5]) cube([6, 1.5, pz0 - bb_z0 - 0.45]);      // bottom stops
    for (s = key_snaps) translate([s[0], s[1], snap_root_z + 0.01]) rotate(s[2]) snap(gap = 0.6);
    rk_fulcrums();
    for (sx = [-1, 1]) translate([sx * tongue_x - tongue[0] / 2, 0, 0]) rotate([90, 0, 90]) linear_extrude(tongue[0]) key_tongue2d(0);
  }
  key_face_cuts();
} }
