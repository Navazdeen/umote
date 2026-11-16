// umote case v7: the two BACK PLATES. Each is flat on its outside, so it prints outside down with
// nothing but the foot chamfer touching the bed; they meet at the keel line (y_ap) on a 45 deg
// bevel. The head plate carries the display posts and the wheel's well and is held by 6 screws
// (4 through the display's corner holes into the face bosses, 2 into the cheeks). The key plate is
// the battery door: two tongues under the cheeks, the bevel, and 2 screws at the bottom end.
scarf_x = 18.5;  sc_step = 0.8;     // bevel across the middle (|x| < scarf_x), after a 0.8 square edge
post_d = 5.2;  post_base = [7.5, 3.4];   // display posts: d under the board; d and top z of the wider foot (takes the sunk screw head)
rib_x = [-15, 0, 15];                    // v7.0: three battery seat ribs here. v7.1: one flat deck (the tests still probe these x)
deck_x = in_w / 2 - lip_clr;             // the deck runs from lip to lip: a full flat face to tape the battery to

// the head plate's side of the split; g moves the cut (negative: towards the key side)
module head_side(g = 0) union() {
  translate([-100, -200, -50]) cube([200, 200 + y_ap - g, 100]);
  translate([-scarf_x, 0, 0]) rotate([90, 0, 90]) linear_extrude(2 * scarf_x)
    polygon([[y_ap - 1, z_ap + sc_step], [y_ap - g, z_ap + sc_step], [y_ap - g + 4, z_ap + sc_step + 4], [y_ap - 1, z_ap + sc_step + 4]]);
}
module plate_layer() difference() { envelope(); above_seam(); }
seam_v = 0.3;      // v7.1: the edge break at the keel seam. 0.75 in v7.0 read as a 1 mm groove in the print; 0.3 is one layer
                   // deep (0.2 a side), just enough that the two squashed first layers don't hold the plates apart
module vgroove() translate([0, y_ap + 0.075, z_ap]) rotate([45, 0, 0]) cube([80, seam_v, seam_v], center = true);
// locating lip inside the shell's side walls, with a stepped lead-in
module lip(y0, y1) intersection() {
  translate([-50, y0, -50]) cube([100, y1 - y0, 100]);
  union() {
    intersection() { band(back_t - 0.01, back_t + lip_h - 0.6); translate([0, 0, -40]) linear_extrude(80) difference() { plan(wall + lip_clr); plan(wall + lip_clr + lip_w); } }
    intersection() { band(back_t + lip_h - 0.61, back_t + lip_h); translate([0, 0, -40]) linear_extrude(80) difference() { plan(wall + lip_clr + 0.5); plan(wall + lip_clr + lip_w); } }
  }
}
// M2 countersunk from the back at p, the head's top at z
module csk_at(p, z) translate([p[0], p[1], 0]) {
  translate([0, 0, z - m2[3]]) m2_csk(30);
  translate([0, 0, -30]) cylinder(d = m2[2], h = 30 + z - m2[3] + 0.01, $fn = 32);
}

module head_back() difference() {
  union() {
    intersection() { plate_layer(); head_side(); }
    intersection() { above_back(back_t - 0.01); union() {
      lip(12, y_head_end - 0.6);
      for (h = holes) translate([h[0], h[1], -30]) { cylinder(d = post_d, h = 30 + db_z0, $fn = 48); cylinder(d = post_base[0], h = 30 + post_base[1], $fn = 48); }
    } }
  }
  wheel_room();
  for (h = holes) csk_at(h, max(z_seat, zb(h[1]) + m2[3]));
  for (p = s2) csk_at(p, zb(p[1]) + m2[3]);
  vgroove();
}
batt_stop = [[-8, 4], [8, 4]];      // x, width: two low wedges at the battery's top end
module key_back() difference() {
  union() {
    difference() { plate_layer(); head_side(-0.15); }
    intersection() { above_back(back_t - 0.01); union() {
      lip(y_ap + 4.5, 170);
      translate([-deck_x, batt_y0 + 2, -30]) cube([2 * deck_x, batt[1] - 4, 30 + seat_z]);
      // 45 deg face towards the battery: the plate comes off along that line
      for (s = batt_stop) let(b = batt_y0 - 0.4) translate([s[0] - s[1] / 2, 0, 0]) rotate([90, 0, 90]) linear_extrude(s[1])
        polygon([[b, -30], [b, seat_z], [b - 1.2, seat_z + 1.2], [b - 3.0, seat_z + 1.2], [b - 3.0, -30]]);
      for (g = groove_x) translate([g[0] + fit, 0, 0]) rotate([90, 0, 90]) linear_extrude(g[1] - g[0] - 2 * fit) tongue2d(0);
    } }
  }
  for (p = ps) csk_at(p, zb(p[1]) + m2[3]);
  vgroove();
}
// print orientation: outside down. Turning about x by atan(-slope) lays the plate's plane flat.
module head_back_print() translate([0, 0, -zb_tip * cos(atan(-kh))]) rotate([atan(-kh), 0, 0]) children();
module key_back_print() translate([0, 0, -(z_ap - kk * y_ap) * cos(atan(-kk))]) rotate([atan(-kk), 0, 0]) children();
