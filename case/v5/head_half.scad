// umote case v5: head (screen half) body and face panel, modelled straight (head_xf() bends them).

// ---------- releasable snap: a beam hanging from the panel's underside ----------
// Local frame: x = 0 is the beam's outer face (towards the wall), the root is at z = 0 (the panel
// underside), the beam hangs down -z, w runs along y. The hook reaches across the free gap to the
// wall and into it by uc. Both hook faces are 45 deg: lifting the panel cams it out (pry release),
// and both print without support (beam up, panel face down).
snap_beam = 3.9;                    // z room above the display PCB at the tip end
module snap(uc = snap_uc, gap = 0.4, len = snap_beam, w = snap_w, t = [1.0, 0.8]) {
  p = gap + uc;                     // hook protrusion past the beam
  zt = -len + 2 * p + 0.2;          // top of the hook's retention face
  translate([0, -w / 2, 0]) rotate([90, 0, 0]) mirror([0, 0, 1]) linear_extrude(w)
    polygon([[-t[0], 0], [0, 0], [0, zt], [p, zt - p], [p, zt - p - 0.2], [0, -len], [-t[1], -len]]);
}
// the matching pocket, same frame. It is cut from the beam's face (x = 0): above roll_z the wall
// rolls in, so its inner face is nearer than gap at the hook's height.
module catch(uc = snap_uc, gap = 0.4, len = snap_beam, w = snap_w) {
  p = gap + uc;  zt = -len + 2 * p + 0.2;
  translate([0, -(w + 0.6) / 2, 0]) rotate([90, 0, 0]) mirror([0, 0, 1]) linear_extrude(w + 0.6)
    polygon([[-0.01, zt + 0.1 + gap], [p + 0.15, zt - p - 0.05], [p + 0.15, zt - p - 0.35], [-0.01, -len - 0.35 - gap]]);
}
// where the 4 snaps sit (straight head coordinates): [x, y, rotation about z]; the beam's outer
// face points along the rotated +x. Two on the tip wall (beside the IR clips, outside the USB-end
// screw heads), one on each side wall near the tip.
snap_root_z = pz0;
tip_snap_y = 2.9;                    // beam outer face: clear of the rolled tip wall at the root (2.82 at z 14.2)
side_snap_x = 22.3;                  // beam outer face; inner face 21.3 (the LCD starts at y 10.5, the snaps sit at y 6)
snaps = [[ 17.5, tip_snap_y, -90], [-17.5, tip_snap_y, -90],
         [ side_snap_x, 6.0, 0], [-side_snap_x, 6.0, 180]];

// the hollow inside the head body: straight walls up to roll_z, then following the upper roll
module head_cavity() { intersection() {
  union() {
    translate([0, 0, floor_t]) linear_extrude(roll_z - floor_t + 0.01) plan(wall);
    stack(roll_z, T + 0.01, 8, 1.8);
  }
  translate([-50, tip_wall, -1]) cube([100, L, 30]);
} }

// ---------- head body ----------
// prongs: blocks merged into the side walls that reach prong[1] into the collar and sit on its
// thickened floor; an M2 from the back (under the magnet plate) threads up into each
prong_x = 19.5;  prong = [5.7, 4.0, 4.3];    // [x width from 17.8 to the wall, y reach, z height]
module prongs(y0, dir) {                     // dir +1: reach +y from y0 (head), -1: reach -y (key)
  zb = floor_t + 1.8;
  for (sx = [-1, 1]) mirror([sx > 0 ? 0 : 1, 0, 0]) translate([17.8, dir > 0 ? y0 - 1 : y0 - prong[1], zb]) difference() {
    union() {
      translate([0, dir > 0 ? 0 : prong[1], 0]) cube([in_w / 2 - 17.8 + 0.5, 1, prong[2]]);      // root, into the own wall
      translate([0, dir > 0 ? 1 : 0, 0]) cube([in_w / 2 - 17.8 - 0.1, prong[1], prong[2]]);       // reach, inside the collar
    }
    translate([prong_x - 17.8, dir > 0 ? prong[1] / 2 + 1 : prong[1] / 2, -1]) cylinder(d = 1.7, h = prong[2] - 0.6, $fn = 24);
  }
}
uz = db_z0 - usb_body_h / 2;
// rounded rectangle whose top (+y) corners are 45 deg chamfers instead: the top edge of an opening
// faces down when the body prints back down. flip = true chamfers the bottom instead (a boss's underside).
module rrc2d_up(w, h, r) polygon(concat(
  [for (k = [0 : 8]) let(t = 180 + 90 * k / 8) [-w / 2 + r + r * cos(t), -h / 2 + r + r * sin(t)]],
  [for (k = [0 : 8]) let(t = 270 + 90 * k / 8) [w / 2 - r + r * cos(t), -h / 2 + r + r * sin(t)]],
  [[w / 2, h / 2 - r], [w / 2 - r, h / 2], [-w / 2 + r, h / 2], [-w / 2, h / 2 - r]]));
module rrc2d(w, h, r, flip = false) { if (flip) mirror([0, 1]) rrc2d_up(w, h, r); else rrc2d_up(w, h, r); }
module usb_cuts() {                           // v4's notch: trapezoid round the plug, skin floor, receptacle hole
  ux = usb_floor * tan(usb_flare);
  translate([usb_x, 0, uz]) rotate([-90, 0, 0]) hull() {
    translate([0, 0, -1]) linear_extrude(1) rrc2d(usb_w + 2 * ux, usb_h, usb_r, true);
    linear_extrude(usb_floor) rrc2d(usb_w, usb_h, usb_r, true);
  }
  translate([usb_x, usb_floor - 0.5, db_z0 - usb_hole[1] / 2]) rotate([-90, 0, 0]) linear_extrude(usb_skin + 2) rrc2d(usb_hole[0], usb_hole[1], usb_hole[2], true);
}
module usb_skin_block() translate([usb_x, tip_wall - 0.01, uz]) rotate([-90, 0, 0])
  linear_extrude(usb_floor + usb_skin - tip_wall + 0.01) rrc2d(usb_w + 2, usb_h + 2, usb_r + 1);
// IR LED: tilted theta down at the tip, so the beam is level when the key half is (the head is bent up)
module ir_xf(sx) translate([sx * ir_x, tip_wall, ir_z]) rotate([theta, 0, 0]) translate([0, -tip_wall, 0]) children();
module ir_slot() for (sx = [-1, 1]) ir_xf(sx)            // dome pocket behind a skin, open to the top for the panel's clip
  translate([0, ir_skin, 0]) rotate([-90, 0, 0]) linear_extrude(tip_wall + 6) hull() { circle(d = 3.15, $fn = 32); translate([-1.575, -8]) square([3.15, 0.01]); }
module head_posts() for (h = holes) translate([h[0], h[1], floor_t - 0.01]) difference() {
  cylinder(d = h[1] < db_y0 + db_l / 2 ? 4.6 : 5.2, h = db_z0 - floor_t + 0.01, $fn = 40);
  translate([0, 0, 1]) cylinder(d = 2.1, h = 20, $fn = 24);
}
module head_body() { difference() {
  union() {
    difference() { ycut(-1, y_head_end) envelope(); head_cavity(); panel_zone(0); }
    intersection() { ycut(-1, y_head_end) translate([0, 0, floor_t]) linear_extrude(T) plan(wall - 0.01);
      union() { usb_skin_block(); head_posts(); } }
    prongs(y_head_end, 1);
  }
  usb_cuts(); ir_slot();
  for (s = snaps) translate([s[0], s[1], snap_root_z]) rotate(s[2]) catch(gap = abs(s[2]) == 90 ? tip_snap_y - tip_wall : 0.6);
  // IR LED wire groove down the -x side wall, from the LED's level to below the display PCB
  translate([-in_w / 2 - ir_wire[2], ir_wire[0], eb]) cube([ir_wire[2] + 0.01, ir_wire[1], roll_z - eb + 1]);
} }

// ---------- head face panel ----------
lip = 1.2;                                   // collar lip over the panel's collar edge (45 deg)
module ir_clips() for (sx = [-1, 1]) intersection() {   // v4's C saddles, tilted with the LEDs
  ir_xf(sx) difference() {
    translate([-2.4, tip_wall - 0.05, -0.6]) cube([4.8, 5.0, 6]);
    translate([0, tip_wall - 1, 0]) rotate([-90, 0, 0]) cylinder(d = 3.1, h = 7, $fn = 32);
    translate([-1.3, tip_wall - 1, -3]) cube([2.6, 7, 3]);
  }
  translate([-50, 0, 0]) cube([100, 50, pz0 + 0.05]);
  translate([0, 0.15, -0.01]) union() { head_cavity(); translate([0, 0, pz0]) linear_extrude(1) plan(wall); }   // stays inside, 0.15 off the tip wall
}
module head_panel() { difference() {
  union() {
    intersection() { panel_zone(pcl); translate([-50, -1, 0]) cube([100, y_head_end + 1, 30]); }
    for (s = snaps) translate([s[0], s[1], snap_root_z + 0.01]) rotate(s[2]) snap(gap = abs(s[2]) == 90 ? tip_snap_y - tip_wall : 0.6);
    ir_clips();
  }
  // screen window + 45 deg bezel (v4)
  translate([0, win_y0 + win_l / 2, pz0 - 0.5]) linear_extrude(pan_t + 1) rr2d(win_w, win_l, win_r);
  translate([0, win_y0 + win_l / 2, T - win_cham]) hull() {
    linear_extrude(0.01) rr2d(win_w, win_l, win_r);
    translate([0, 0, win_cham + 0.01]) linear_extrude(0.01) rr2d(win_w + 2 * win_cham, win_l + 2 * win_cham, win_r + win_cham);
  }
  // the collar edge: 45 deg chamfer from the face under the collar's lip
  translate([-50, 0, 0]) rotate([90, 0, 90]) linear_extrude(100)
    polygon([[y_head_end - lip, T + 0.01], [y_head_end + 1, T + 0.01], [y_head_end + 1, T - lip - 1], [y_head_end + 0.01, T - lip - 1], [y_head_end + 0.01, T - lip]]);
} }
