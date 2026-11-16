// umote case v7: the FRONT SHELL. One piece: the whole face and all four walls, printed face down
// (the face comes off the smooth plate, with no panel seams). Everything that v6 split between two
// bodies, two face panels and the collar frame stands on the inside of the face here, so nothing
// overhangs in that orientation and every component drops in from the back:
//   IR LEDs -> caps and D-pad ring -> button board (4 clips) -> display board (onto 4 bosses)
//   -> encoder with nut, wheel and carrier (U-slot, open to the back) -> contact plate -> battery.
// Then the two back plates (backs.scad) close it.

batt_end = batt_y0 + batt[1];
bb_end = bb_y0 + bb_l;
end_block_y = bb_end + 0.6;         // solid end: the contact plate's slot, the key plate's screws, the eyelet
pad_x = 2.6;  pad_z = 8.25;         // plate A: brass-insert contact pads (5.2 apart)
dmag_x = 10.9;  dmag_z = 8.25;      // plate A: 10 x 2 magnets (dock magnets face them)
eye = [-21.5, L - 5.0, 5.3];        // strap eyelet: in through the side (along x), out through the end corner (along y)
clip_y = [bb_y0 + 20, bb_y0 + 100];  clip_w = 6;  clip_t = 1.3;   // board clips (1.0 thick in v6)
stop_y = bb_end + 0.1;
ps = [for (sx = [-1, 1]) [sx * 13, (end_block_y + L - pp_t - fit) / 2]];   // the key plate's 2 screws, mid-way through the end block
boss_d = 5.0;  boss_flat = 2.0;  boss_hole = 4.5;   // display bosses under the face, each tied to the side wall by a web; the two
                                    // at the antenna end are flat on the LCD side (the glass ends 2.3 from the hole)
tap_depth = 7.0;                    // self-tap holes in the cheeks and the end block (M2 x 8 through a 2.0 plate)
uz = db_z0 - usb_body_h / 2;

// the hollow: 2.4 walls all the way up (they follow the roll round the face), under a 2.0 face
module cavity(top = pz0) intersection() {
  union() { translate([0, 0, -30]) linear_extrude(30 + roll_z + 0.01) plan(wall); stack(roll_z, pz0 + 0.02, 6, wall); }
  translate([-60, -10, -40]) cube([120, L + 20, 40 + top]);
}

// ---------- head: display, USB-C, IR ----------
module disp_bosses() for (h = holes) {
  intersection() { translate([h[0], h[1], db_top + 0.05]) cylinder(d = boss_d, h = pz0 - db_top, $fn = 48);
    translate([-40, h[1] > 40 ? h[1] - boss_flat : -10, 0]) cube([80, 100, 40]); }
  translate([h[0] > 0 ? h[0] : -30, h[1] - 1.0, db_top + 0.05]) cube([30 - abs(h[0]), 2.0, pz0 - db_top]);
}
module rrc2d_up(w, h, r, c = -1) let(cc = c < 0 ? r : c) polygon(concat(
  [for (k = [0 : 8]) let(t = 180 + 90 * k / 8) [-w / 2 + r + r * cos(t), -h / 2 + r + r * sin(t)]],
  [for (k = [0 : 8]) let(t = 270 + 90 * k / 8) [w / 2 - r + r * cos(t), -h / 2 + r + r * sin(t)]],
  [[w / 2, h / 2 - cc], [w / 2 - cc, h / 2], [-w / 2 + cc, h / 2], [-w / 2, h / 2 - cc]]));
module rrc2d(w, h, r, flip = false, c = -1) { if (flip) mirror([0, 1]) rrc2d_up(w, h, r, c); else rrc2d_up(w, h, r, c); }
module usb_notch() { ux = usb_floor * tan(usb_flare);
  translate([usb_x, 0, uz]) rotate([-90, 0, 0]) hull() {
    translate([0, 0, -1]) linear_extrude(1) rrc2d(usb_w + 2 * ux, usb_h, usb_r, true, 1.2);
    linear_extrude(usb_floor) rrc2d(usb_w, usb_h, usb_r, true, 1.2);
  } }
module usb_cuts() {
  hull() { usb_notch(); translate([0, 0, -8]) usb_notch(); }     // open to the wall's edge: no roof to bridge, the head plate closes it
  translate([usb_x, usb_floor - 0.5, db_z0 - usb_hole[1] / 2]) rotate([-90, 0, 0]) linear_extrude(usb_skin + 2.4) rrc2d(usb_hole[0], usb_hole[1], usb_hole[2]);
}
module usb_skin_block() translate([usb_x, tip_wall - 0.01, uz]) rotate([-90, 0, 0])
  linear_extrude(max(0.01, usb_floor + usb_skin - tip_wall) + 0.01) rrc2d(usb_w + 2, usb_h + 2, usb_r + 1);
// IR LEDs: the dome sits in a blind hole in the tip wall, behind a skin; the body snaps into a saddle
// under the face from the back, and the display board then closes under it
module ir_pockets() for (sx = [-1, 1]) translate([sx * ir_x, 0, ir_z]) td_y(3.15, ir_skin, tip_wall + 0.5, down = true);
module ir_clips() for (sx = [-1, 1]) translate([sx * ir_x, 0, ir_z]) difference() {
  translate([-2.4, tip_wall - 0.05, -0.6]) cube([4.8, 5.0, 6]);
  translate([0, tip_wall - 1, 0]) rotate([-90, 0, 0]) cylinder(d = 3.1, h = 7, $fn = 32);
  translate([-1.3, tip_wall - 1, -3]) cube([2.6, 7, 3]);
}

// ---------- wheel zone: cheeks, cross walls, bulkhead ----------
module wz_solids() {
  h = 30 + pz0 + 0.01;
  for (sx = [-1, 1]) translate([sx > 0 ? room_x : -40, y_head_end, -30]) cube([40 - room_x, y_key_start - y_head_end, h]);
  for (y = [y_head_end, room_y1]) translate([-room_x - 0.01, y, -30]) cube([2 * room_x + 0.02, col_wall, h]);
  difference() {      // the bushing drops into a U-slot open to the back, with nut, wheel and carrier already on
    translate([ec11_xf - bulk_t, y_head_end, -30]) cube([bulk_t, y_key_start - y_head_end, h]);
    translate([ec11_xf - bulk_t - 1, cy, axle_z]) rotate([0, 90, 0]) linear_extrude(bulk_t + 2) {
      circle(d = ec11_bush[0] + 0.3, $fn = 48);
      translate([0, -(ec11_bush[0] + 0.3) / 2]) square([40, ec11_bush[0] + 0.3]);   // rotated: +local x = -z
    }
  }
}
// the key plate's two tongues hook under the cheeks' key ends: leaning 45 deg, so the plate goes on
// along that line and its edge closes onto the head plate's bevel at the same time
groove_x = [[-22.4, -19.6], [19.6, 22.4]];  tongue_h = 2.6;
module tongue2d(grow = 0) let(z0 = zs(y_ap)) offset(delta = grow)
  polygon([[y_ap + 1.4, z0 - 0.5], [y_ap + 3.9, z0 - 0.5], [y_ap + 3.4 - tongue_h, z0 + tongue_h], [y_ap + 0.9 - tongue_h, z0 + tongue_h]]);

// ---------- key half: collars, clips, end block ----------
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
module key_collars() translate([0, 0, pz0 - cap_flange - 0.4]) linear_extrude(cap_flange + 0.45)
  offset(r = 0.6) offset(delta = -0.6) intersection() {
    difference() {
      union() { key_collars2d(); translate(dc) circle(r = acc_out + 0.1 + 1.2, $fn = 192); }
      translate(dc) circle(r = acc_out + 0.1, $fn = 192);
      for (k = round_keys) translate(bpos(singles[k])) circle(d = flange_d + 2 * flange_clr);
      for (p = [vol, ch]) capsule2d(p, flange_d + 2 * flange_clr);
    }
    translate([-50, y_key_start + 0.2]) square([100, L]);
  }
module board_clip() {
  len = pz0 - bb_z0 + 0.5;
  translate([0, -clip_w / 2, 0]) rotate([90, 0, 0]) mirror([0, 0, 1]) linear_extrude(clip_w)
    polygon([[0, 0], [clip_t, 0], [clip_t, -len], [-0.6, -len + 0.0], [-0.6, -len + 0.5], [0, -len + 1.1]]);
}
module end_block() {
  translate([-40, end_block_y, -30]) cube([80, 30, 30 + pz0 + 0.01]);
  for (sx = [-1, 1]) translate([sx * 6 - 3, stop_y, bb_z0 + 0.5]) cube([6, 1.5, pz0 - bb_z0 - 0.45]);   // the board's end stops
}

// ---------- contact plate: slot in the end, plates A (pads + magnets) and B (magnetic connector) ----------
// footprint (x, y): the plate, open through the end face, with a T-rib on its back that runs in a
// T-slot in the end block; g grows it (the slot). It drops in from the back; the key plate holds it.
module pp_foot(g = 0) {
  translate([-pp_w / 2 - g, L - pp_t - g]) square([pp_w + 2 * g, pp_t + 10]);
  translate([-pp_tee[0] / 2 - g, L - pp_t - pp_tee[1] - g]) square([pp_tee[0] + 2 * g, pp_tee[1] + 0.02]);
  translate([-pp_tee[2] / 2 - g, L - pp_t - pp_tee[1] - pp_tee[3] - g]) square([pp_tee[2] + 2 * g, pp_tee[3] + 2 * g]);
}
module pp_slot() translate([0, 0, -30]) linear_extrude(30 + pz0) pp_foot(fit);
mag_y1 = L - min_skin - max(e_in(dmag_z + magnet[0] / 2 + 0.1), e_in(dmag_z - magnet[0] / 2 - 0.1)) - 0.1;
module pp_blank() intersection() { envelope(); translate([0, 0, pp_z0]) linear_extrude(pz0 - 0.15 - pp_z0) pp_foot(0); }
module pogo_plate_a() difference() {   // assembled position
  pp_blank();
  for (sx = [-1, 1]) {
    translate([sx * pad_x, 0, pad_z]) { td_y(pad_insert[0], L - pad_insert[1], L + 1); td_y(2.0, L - pp_t - 1, L - pad_insert[1] + 0.1); }
    translate([sx * dmag_x, 0, dmag_z]) td_y(magnet[0] + 0.2, L - pp_t - 1, mag_y1);   // teardrop: the plate prints standing
  }
}
module pogo_plate_b() difference() {   // a ready-made magnetic connector: housing through the plate, ears screwed on its back
  pp_blank();
  translate([-conn_b[0] / 2 - 0.15, L - pp_t - 1, pad_z - conn_b[1] / 2 - 0.15]) cube([conn_b[0] + 0.3, pp_t + 5, conn_b[1] + 0.3]);
  for (sx = [-1, 1]) translate([sx * conn_b[3] / 2, 0, pad_z]) td_y(conn_b[4], L - pp_t - 0.01, L - pp_t + 4.0);
}

// ---------- the shell ----------
module tap(p, z) translate([p[0], p[1], z]) {      // self-tap pilot going up from z, with a lead-in
  translate([0, 0, -1]) cylinder(d = m2[0], h = 1 + tap_depth, $fn = 48);
  translate([0, 0, -1]) cylinder(d1 = m2[0] + 2.8, d2 = m2[0], h = 1.4, $fn = 48);
}
module shell_cuts() {
  // screen window + 45 deg bezel
  translate([0, win_y0 + win_l / 2, pz0 - 0.5]) linear_extrude(pan_t + 1) rr2d(win_w, win_l, win_r);
  translate([0, win_y0 + win_l / 2, T - win_cham]) hull() {
    linear_extrude(0.01) rr2d(win_w, win_l, win_r);
    translate([0, 0, win_cham + 0.01]) linear_extrude(0.01) rr2d(win_w + 2 * win_cham, win_l + 2 * win_cham, win_r + win_cham);
  }
  key_face_cuts();
  // wheel: window in the face, its room, and the wire notches through the cross walls (open to the back)
  translate([whl_x - win[0] / 2, cy - win[1] / 2, pz0 - 1]) cube([win[0], win[1], 10]);
  wheel_room();
  translate([-15.3, y_head_end - 1, -30]) cube([5.3, y_key_start - y_head_end + 2, 30 + 11.2]);    // battery + inter-board wires
  translate([13.2, room_y1 - 1, -30]) cube([2.3, col_wall + 2, 30 + 12.0]);                        // the roller's three
  translate(concat(bpos(mic_b), [-30])) cylinder(d = mic_mod[0] + 1.0, h = 30 + bb_top - 0.5 + mic_mod[1] + 1.2, $fn = 64);   // the mic module overhangs the board's top edge
  usb_cuts(); ir_pockets();
  translate([-in_w / 2 - ir_wire[2], ir_wire[0], zb(ir_wire[0]) + eb]) cube([ir_wire[2] + 0.01, ir_wire[1], roll_z - zb(ir_wire[0]) - eb]);
  for (h = holes) translate([h[0], h[1], db_top]) { cylinder(d = m2[0], h = boss_hole, $fn = 48); cylinder(d1 = m2[0] + 0.9, d2 = m2[0], h = 0.5, $fn = 48); }
  for (p = concat(s2, ps)) tap(p, zs(p[1]));
  for (g = groove_x) translate([g[0], 0, 0]) rotate([90, 0, 90]) linear_extrude(g[1] - g[0]) tongue2d(fit);
  pp_slot();
  translate([-4, end_block_y - 1, -30]) cube([8, L - pp_t - end_block_y + 1.1, 30 + pad_z + 1.25]);   // the plate's wires into the bottom zone (open to the back)
  translate([0, eye[1], eye[2]]) td_x(2.2, -W, eye[0] + 1.1, down = true);
  translate([eye[0], 0, eye[2]]) td_y(2.2, eye[1] - 1.1, L + 2, down = true);
}
module shell() difference() {
  intersection() {
    envelope(); above_seam();
    union() {
      difference() { envelope(); cavity(); }
      intersection() { cavity(pz0 + 0.02); union() {
        disp_bosses(); ir_clips(); usb_skin_block(); wz_solids(); key_collars(); end_block(); rk_fulcrums();
        for (y = clip_y) for (sx = [-1, 1]) mirror([sx > 0 ? 0 : 1, 0, 0]) translate([bb_w / 2 + 0.1, y, pz0 + 0.01]) board_clip();
      } }
    }
  }
  shell_cuts();
}
