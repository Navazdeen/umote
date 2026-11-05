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
// the matching pocket in the wall, same frame (the wall's inner face is at x = gap)
module catch(uc = snap_uc, gap = 0.4, len = snap_beam, w = snap_w) {
  p = gap + uc;  zt = -len + 2 * p + 0.2;
  translate([0, -(w + 0.6) / 2, 0]) rotate([90, 0, 0]) mirror([0, 0, 1]) linear_extrude(w + 0.6)
    polygon([[gap - 0.01, zt + 0.1], [p + 0.15, zt - p - 0.05], [p + 0.15, zt - p - 0.35], [gap - 0.01, -len - 0.35]]);
}
// where the 4 snaps sit (straight head coordinates): [x, y, rotation about z]; the beam's outer
// face points along the rotated +x. Two on the tip wall (beside the IR clips, outside the USB-end
// screw heads), one on each side wall near the tip.
snap_root_z = pz0;
tip_snap_y = tip_wall + 0.4;         // beam outer face 0.4 in from the tip wall
side_snap_x = in_w / 2 - 0.9;        // under the panel edge, clear of the rolled wall
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
