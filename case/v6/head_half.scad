// umote case v6: head (screen half) body and face panel, modelled straight (head_xf() bends them).
// No snaps (v5's tip catches broke through the rolled tip wall). The panel is held by 4 M2 from the
// back: through the head floor, the display posts and the display's own corner holes, into bosses
// under the panel; that clamps the display too. Two tenons run from the head's end into the key
// body's rails.

// the hollow inside the head body: straight walls up to roll_z, then following the upper roll
module head_cavity() { intersection() {
  union() {
    translate([0, 0, floor_t]) linear_extrude(roll_z - floor_t + 0.01) plan(wall);
    stack(roll_z, T + 0.01, 8, wall);
  }
  translate([-50, tip_wall, -1]) cube([100, L, 30]);
} }

// ---------- tenons ----------
// In head coordinates. Cross-section (x, z): from the back (z 0, on the bed) up to a 45 deg roof that
// falls from z ten_top at the outer edge to ten_top - (ten_x1 - ten_x0) at the inner one, so the slots
// in the rails print without a flat roof. They run ten_len past the head's end; their roots fill
// the corner inside the head beside and under the display board.
ten_x0 = rail_x;  ten_x1 = 23.4;  ten_top = 8.6;  ten_len = 8.0;
module tenon2d(g = 0) offset(delta = g) polygon([[ten_x0, 0], [ten_x1, 0], [ten_x1, ten_top], [ten_x0, ten_top - (ten_x1 - ten_x0)]]);
// clipped 2.55 inside the outer surface (2.4 of rail outside its slot, which is 0.15 bigger)
module tenon(g = 0, y0 = y_head_end, y1 = y_head_end + ten_len) for (sx = [-1, 1]) tenon_one(sx, g, y0, y1);
module tenon_one(sx, g = 0, y0 = y_head_end, y1 = y_head_end + ten_len) intersection() {
  mirror([sx > 0 ? 0 : 1, 0, 0])
    translate([0, y0 - g, 0]) rotate([-90, 0, 0]) mirror([0, 1, 0]) linear_extrude(y1 - y0 + 2 * g) tenon2d(g);
  union() {
    env_inset(2.55 - g);
    translate([0, 0, -5]) linear_extrude(5.01) plan(e_in(0) + 2.55 - g);   // below the back: it dips into the ridge in key coordinates
  }
}
module tenons_xf(g = 0) head_xf() tenon(g);
// the root inside the head: up to the display PCB's underside beside it, under its back parts inboard
module tenon_root() intersection() {
  for (sx = [-1, 1]) mirror([sx > 0 ? 0 : 1, 0, 0]) translate([0, y_head_end - 8, 0]) rotate([-90, 0, 0]) mirror([0, 1, 0]) linear_extrude(8.01)
    polygon([[ten_x0, 0], [ten_x1 + 1.5, 0], [ten_x1 + 1.5, ten_top], [ten_x0, ten_top - (ten_x1 - ten_x0)]]);   // runs into the side wall
  union() {
    for (sx = [-1, 1]) translate([sx > 0 ? db_w / 2 - 0.5 + 0.3 : -60, -50, 0]) cube([60 - (db_w / 2 - 0.5 + 0.3), 400, db_z0 - 0.3]);   // beside the back parts (|x| > 20.9 + 0.3)
    translate([-50, -50, 0]) cube([100, 400, db_z0 - db_back - 0.3]);              // under them
  }
  translate([-50, -50, 0]) cube([100, 400, db_z0 - 0.3]);
}

// ---------- head body ----------
uz = db_z0 - usb_body_h / 2;
module rrc2d_up(w, h, r, c = -1) let(cc = c < 0 ? r : c) polygon(concat(
  [for (k = [0 : 8]) let(t = 180 + 90 * k / 8) [-w / 2 + r + r * cos(t), -h / 2 + r + r * sin(t)]],
  [for (k = [0 : 8]) let(t = 270 + 90 * k / 8) [w / 2 - r + r * cos(t), -h / 2 + r + r * sin(t)]],
  [[w / 2, h / 2 - cc], [w / 2 - cc, h / 2], [-w / 2 + cc, h / 2], [-w / 2, h / 2 - cc]]));
module rrc2d(w, h, r, flip = false, c = -1) { if (flip) mirror([0, 1]) rrc2d_up(w, h, r, c); else rrc2d_up(w, h, r, c); }
module usb_cuts() {
  ux = usb_floor * tan(usb_flare);
  translate([usb_x, 0, uz]) rotate([-90, 0, 0]) hull() {
    translate([0, 0, -1]) linear_extrude(1) rrc2d(usb_w + 2 * ux, usb_h, usb_r, true, 1.2);
    linear_extrude(usb_floor) rrc2d(usb_w, usb_h, usb_r, true, 1.2);
  }
  translate([usb_x, usb_floor - 0.5, db_z0 - usb_hole[1] / 2]) rotate([-90, 0, 0]) linear_extrude(usb_skin + 2.4) rrc2d(usb_hole[0], usb_hole[1], usb_hole[2], true);
}
module usb_skin_block() translate([usb_x, tip_wall - 0.01, uz]) rotate([-90, 0, 0])
  linear_extrude(max(0.01, usb_floor + usb_skin - tip_wall) + 0.01) rrc2d(usb_w + 2, usb_h + 2, usb_r + 1);
module ir_xf(sx) translate([sx * ir_x, tip_wall, ir_z]) rotate([theta, 0, 0]) translate([0, -tip_wall, 0]) children();
// dome pocket behind a skin, open to the top for the panel's clip; above the LED its front steps back
// with the top roll, so the skin doesn't thin under it
module ir_slot() for (sx = [-1, 1]) ir_xf(sx) hull() {
  translate([0, ir_skin, 0]) rotate([-90, 0, 0]) cylinder(d = 3.15, h = tip_wall + 6, $fn = 32);
  translate([-1.575, ir_skin + e_in(pz0) - e_in(ir_z) + 0.2, 1.575 + 2.5]) cube([3.15, tip_wall + 6, 5]);
}
post_d = 5.2;
module head_posts() for (h = holes) translate([h[0], h[1], floor_t - 0.01]) cylinder(d = post_d, h = db_z0 - floor_t + 0.01, $fn = 40);
// the 4 panel screws: counterbore in the back, clearance up through the post and the PCB
module panel_screw_holes() for (h = holes) translate([h[0], h[1], 0]) m2_csk(db_z0 + 2);
module head_body() { difference() {
  union() {
    difference() { ycut(-1, y_head_end) envelope(); head_cavity(); translate([-60, -10, pz0]) cube([120, L + 20, 20]); }
    intersection() { ycut(-1, y_head_end) translate([0, 0, floor_t]) linear_extrude(T) plan(wall - 0.01);
      union() { usb_skin_block(); head_posts(); } }
    intersection() { ycut(-1, y_head_end + 0.01) translate([0, 0, -1]) linear_extrude(T) plan(wall - 0.01); tenon_root(); }
    tenon();
  }
  usb_cuts(); ir_slot(); panel_screw_holes();
  // pilot holes for the ridge's joint screws: vertical in key coordinates
  head_xf_inv() for (p = s1) translate([p[0], p[1], -6]) { cylinder(d = m2[0], h = 6 + 1.4, $fn = 24);   // 1.2 under the 45 deg roof; drill-point top
    translate([0, 0, 6 + 1.4 - 0.01]) cylinder(d1 = m2[0], d2 = 0, h = m2[0], $fn = 24); }   // 63 deg point: still steeper than 45 after the 8 deg bend
  translate([-in_w / 2 - ir_wire[2], ir_wire[0], eb]) cube([ir_wire[2] + 0.01, ir_wire[1], roll_z - eb]);   // stops at the top roll
} }

// ---------- head face panel ----------
boss_d = 4.0;  boss_hole = 4.5;      // panel bosses down to the display PCB (4.0 clears the LCD); self-tap depth
module ir_clips() for (sx = [-1, 1]) intersection() {
  ir_xf(sx) difference() {
    translate([-2.4, tip_wall - 0.05, -0.6]) cube([4.8, 5.0, 6]);
    translate([0, tip_wall - 1, 0]) rotate([-90, 0, 0]) cylinder(d = 3.1, h = 7, $fn = 32);
    translate([-1.3, tip_wall - 1, -3]) cube([2.6, 7, 3]);
  }
  translate([-50, 0, 0]) cube([100, 50, pz0 + 0.05]);
  union() { translate([0, 0.15, -0.01]) head_cavity(); panel_zone(pcl); }
}
module head_panel() { difference() {
  union() {
    panel_cap(-1, y_head_end - 0.1);
    for (h = holes) translate([h[0], h[1], db_top + 0.05]) cylinder(d = boss_d, h = pz0 - db_top - 0.05 + 0.01, $fn = 40);
    ir_clips();
  }
  for (h = holes) translate([h[0], h[1], db_top]) cylinder(d = m2[0], h = boss_hole, $fn = 24);
  // screen window + 45 deg bezel
  translate([0, win_y0 + win_l / 2, pz0 - 0.5]) linear_extrude(pan_t + 1) rr2d(win_w, win_l, win_r);
  translate([0, win_y0 + win_l / 2, T - win_cham]) hull() {
    linear_extrude(0.01) rr2d(win_w, win_l, win_r);
    translate([0, 0, win_cham + 0.01]) linear_extrude(0.01) rr2d(win_w + 2 * win_cham, win_l + 2 * win_cham, win_r + win_cham);
  }
} }
