// umote case v7: key geometry (caps, rockers, D-pad ring), unchanged from v6.
// plus the v5 rockers). Caps themselves come in Task 8.
module ring2d(grow = 0) {
  difference() {
    circle(r = ring_out + grow, $fn = 192);
    circle(r = ring_in - grow, $fn = 128);
    for (a = [45 : 90 : 315]) rotate(a) translate([0, -(ring_web / 2 - grow)]) square([ring_out + 5, ring_web - 2 * grow]);
  }
}
module sector2d(i, grow = 0) {       // i: 0 left(+x), 1 down(+y), 2 right(-x), 3 up(-y)
  intersection() {
    ring2d(grow);
    rotate(i * 90) polygon([[0, 0], [40, -40], [40, 40]]);
  }
}

module capsule2d(p, d) { hull() for (q = p) translate(q) circle(d = d, $fn = 48); }
round_keys = [0, 1, 2, 3, 6];       // POWER BACK HOME VOICE MUTE keep v4's round caps
// v6: POWER's rib turns to +x (towards the tip it came 0.85 from the panel's end), HOME's to +y (towards
// the tip it came 0.45 from the D-pad's hole)
function rib_a(k) = k == 0 ? 90 : k == 2 ? 180 : 0;
vol = [bpos(singles[4]), bpos(singles[5])];  ch = [bpos(singles[7]), bpos(singles[8])];
acc_in = ring_out;  acc_out = ring_out + 0.9;      // D-pad ring (accent part): the opening's rim (POWER's hole is 19.25 from the centre)
ring_tabs = [0, 180, -90];  ring_tab_arc = 26;          // retaining tabs: angles clear of POWER (-54) and HOME (90); arc in degrees

// ---------- caps (v4's v2 caps, unchanged) ----------
cap_h = (T + cap_proud) - (front_in - cap_flange);
sock  = act_top - (front_in - cap_flange);
// a flange layer with its bed edge stepped in by ef (three 0.1 steps, ~45 deg) for elephant's foot
module ef_flange(h) {
  for (k = [0 : 2]) translate([0, 0, k * ef / 3]) linear_extrude(ef / 3 + 0.01) offset(delta = -ef * (3 - k) / 3) children();
  translate([0, 0, ef]) linear_extrude(h - ef) children();
}
// v7.2: pocket over the 6x6 switch body: vertical for h, then a 45 deg roof up to the hex bore, so
// nothing under a cap is bridged (the v7.1 rockers' flat 0.5 pockets sagged on the print)
module sw_pocket(h) {
  rb = grip_af / cos(30) / 2;            // the bore's corner radius: the roof ends there
  translate([0, 0, -1]) linear_extrude(1 + h) square(pocket_w, center = true);
  // v7.2.1: the roof starts from the square clipped to r 3.7. The full square's corners (r 4.67) broke
  // through the 8.6 caps' walls just above the flange; now >= 0.6 of wall stays. The square part (h) is
  // inside the flange (0.8), and the switch body's corners stay below h even pressed or tipped.
  translate([0, 0, h - 0.01]) hull() {
    linear_extrude(0.01) intersection() { square(pocket_w, center = true); circle(r = pocket_roof_r, $fn = 64); }
    translate([0, 0, pocket_roof_r - rb + 0.3]) linear_extrude(0.01) circle(r = rb, $fn = 32);   // +0.3: every roof face steeper than 45
  }
}
// blind hex bore for the plunger, with a 0.4 lead-in; its small flat ceiling is the only bridge
module bore() {
  translate([0, 0, -1]) rotate(30) cylinder(d = grip_af / cos(30), h = 1 + sock, $fn = 6);
  translate([0, 0, -0.01]) cylinder(d1 = grip_af / cos(30) + 0.8, d2 = grip_af / cos(30), h = 0.4, $fn = 6);
}
module ring_cap(i) {
  difference() {
    union() {
      // flange 0.4 past the opening (collar pocket is 0.95 past it), body side_clr inside it
      ef_flange(cap_flange) difference() { offset(r = 0.4) sector2d(i); circle(r = ring_in + side_clr, $fn = 128); }
      linear_extrude(cap_h - cap_top_cham) offset(r = -side_clr) sector2d(i);
      translate([0, 0, cap_h - cap_top_cham]) hull() {
        linear_extrude(0.01) offset(r = -side_clr) sector2d(i);
        translate([0, 0, cap_top_cham - 0.01]) linear_extrude(0.01) offset(r = -side_clr - cap_top_cham) sector2d(i);
      }
    }
    rotate(i * 90) translate([dpad_sw, 0, 0]) { bore(); sw_pocket(pocket_h); }
    rotate(i * 90) translate([dpad_sw - 0.5, 0, cap_h - 0.4]) linear_extrude(1) polygon([[-1.2, -2.0], [-1.2, 2.0], [1.4, 0]]);
  }
}
// d: the visible diameter; fd: flange diameter
// rib_a turns the key rib (default: towards the tip, -y); the icon stays upright
module round_cap(d, m, key = true, fd = flange_d - 2 * flange_shrink, rib_a = 0) {
  difference() {
    union() {
      ef_flange(cap_flange) circle(d = fd);
      if (key) rotate(rib_a) translate([0, -(d / 2 + rib_out), 0]) hull() {    // key rib, outer top edge chamfered
        translate([-cap_rib_w / 2, 0, 0]) cube([cap_rib_w, rib_out + 1, cap_rib_h - 0.3]);
        translate([-cap_rib_w / 2, 0.3, 0]) cube([cap_rib_w, rib_out + 0.7, cap_rib_h]);
      }
      cylinder(d = d, h = cap_h - cap_top_cham);
      translate([0, 0, cap_h - cap_top_cham]) cylinder(d1 = d, d2 = d - 2 * cap_top_cham, h = cap_top_cham);
    }
    bore();  sw_pocket(pocket_h);
    translate([0, 0, cap_h - 0.4]) linear_extrude(1) mark(m);
  }
}
// OK sits in a d = ok_d + 0.6 opening: body side_clr inside it, flange 0.55 past it (pocket r 6.45)
module ok_cap() { round_cap(ok_d + 0.6 - 2 * side_clr, 5, key = false, fd = ok_d + 0.6 + 1.1); }
module mark(m) {
  if (m == 5) difference() { circle(d = 5.4); circle(d = 4.0); }
  if (m == 6) { difference() { circle(d = 5); circle(d = 3.6); translate([-0.9, -3]) square([1.8, 3]); } translate([-0.45, -3]) square([0.9, 2.8]); }
  if (m == 7) { translate([0, -0.6]) offset(r = 0.9) square([0.01, 1.8], center = true); translate([-0.3, 1.0]) square([0.6, 1.2]); }
  if (m == 8) polygon([[-1.0, -2.0], [-1.0, 2.0], [1.6, 0]]);
  if (m == 9) polygon([[0, -2.2], [2.2, 0], [1.4, 0], [1.4, 1.9], [-1.4, 1.9], [-1.4, 0], [-2.2, 0]]);
  // -y is "up" (towards the tip) on every cap
  if (m == 10 || m == 11) square([3.6, 0.9], center = true);                       // VOL+ / VOL-
  if (m == 10) square([0.9, 3.6], center = true);
  if (m == 12) chevron();                                                         // CH+
  if (m == 13) mirror([0, 1]) chevron();                                          // CH-
  if (m == 14) {                                                                  // MUTE: speaker + x
    polygon([[-2.6, -0.8], [-1.6, -0.8], [-0.4, -2.0], [-0.4, 2.0], [-1.6, 0.8], [-2.6, 0.8]]);
    for (s = [-1, 1]) hull() { translate([0.7, -0.9 * s]) circle(d = 0.7, $fn = 16); translate([2.5, 0.9 * s]) circle(d = 0.7, $fn = 16); }
  }
}
module chevron() {
  for (s = [-1, 1]) hull() { translate([0, -0.9]) circle(d = 0.9, $fn = 16); translate([1.9 * s, 1.0]) circle(d = 0.9, $fn = 16); }
}


// ---------- v5: OK nub, rockers, D-pad ring ----------
module ok_cap_nub() { ok_cap(); translate([0, 0, cap_h - 0.05]) intersection() {   // sunk 0.05 so it joins the cap (it only touched it)
   sphere(d = 1.6, $fn = 24); translate([-1, -1, 0]) cube(2); } }
rk_drop = 0.3;                      // rockers sit rk_drop lower: their ends can rise that far as they tip
rk_h = cap_h + rk_drop;  rk_sock = sock + rk_drop;
rk_flange_half = rk_drop * 6.5 / 0.3 - 0.5;   // tipping 0.3 at a switch (6.5 out) lifts the flange end less than rk_drop
module rk_bore() {
  translate([0, 0, -1]) rotate(30) cylinder(d = grip_af / cos(30), h = 1 + rk_sock, $fn = 6);
  translate([0, 0, -0.01]) cylinder(d1 = grip_af / cos(30) + 0.8, d2 = grip_af / cos(30), h = 0.4, $fn = 6);
}
// a rocker over two switches (p = their two centres, along y), in local coordinates centred between
// them, flange bottom at z 0. Saddle top, a + / - or chevron mark at each end.
module rocker(p, marks) {
  c = (p[0] + p[1]) / 2;  q = [p[0] - c, p[1] - c];
  difference() {
    union() {
      // flange only along the middle: tipped, a flange at the ends would rise past the panel underside
      ef_flange(cap_flange) intersection() { capsule2d(q, flange_d - 2 * flange_shrink); square([30, 2 * rk_flange_half], center = true); }
      linear_extrude(rk_h - cap_top_cham) capsule2d(q, cap_d);
      translate([0, 0, rk_h - cap_top_cham]) hull() { linear_extrude(0.01) capsule2d(q, cap_d);
        translate([0, 0, cap_top_cham - 0.01]) linear_extrude(0.01) capsule2d(q, cap_d - 2 * cap_top_cham); }
    }
    for (e = q) translate(e) rk_bore();
    for (e = q) translate(e) sw_pocket(rk_pocket_h);   // clear of the switch body when tipped and pressed
    translate([0, 0, rk_h + 40 - 0.5]) rotate([0, 90, 0]) cylinder(r = 40, h = 20, center = true, $fn = 360);   // saddle, 0.5 deep
    for (i = [0, 1]) translate(concat(q[i], [rk_h - 0.5])) linear_extrude(2) mark(marks[i]);   // 0.5 deep (0.9 in v7.1): 0.7 left over the plunger
  }
}
rockers = [[vol, [10, 11]], [ch, [12, 13]]];
// the fulcrum each rocker tips on: two pads under the panel, either side of the rocker's body, on
// its flange's middle
rk_pad = [0.7, 1.2];                // across (the flange's margin past the body), along the rocker
module rk_fulcrums() for (r = rockers) let(c = (r[0][0] + r[0][1]) / 2) for (sx = [-1, 1])
  translate([c[0] + sx * (cap_d / 2 + 0.05 + rk_pad[0] / 2) - rk_pad[0] / 2, c[1] - rk_pad[1] / 2, pz0 - rk_drop]) cube([rk_pad[0], rk_pad[1], rk_drop + 0.01]);
// at rest a rocker's flange top touches its fulcrum; tipped, it turns about that line
module rocker_at(r, tip = 0) let(c = (r[0][0] + r[0][1]) / 2, a = -sign(r[0][0][1] - c[1]) * asin(tip / norm(r[0][0] - c)))   // tip: the first switch's end goes down
  translate([c[0], c[1], pz0 - rk_drop - cap_flange]) translate([0, 0, cap_flange]) rotate([a, 0, 0]) translate([0, 0, -cap_flange]) rocker(r[0], r[1]);

// D-pad ring (accent): the visible frame round the D-pad sectors (rim r ring_out .. acc_out, the
// webs, the hub round OK), all 0.5 proud, held under the panel by three 45 deg tabs. The sector and
// OK flanges sit in v4's collar pockets in the panel and bear on this frame's underside.
module ring_tab_arcs(r) for (a = ring_tabs) rotate(a - ring_tab_arc / 2) intersection() {
  circle(r = r, $fn = 192); polygon([[0, 0], [r * 2, 0], [r * 2 * cos(ring_tab_arc), r * 2 * sin(ring_tab_arc)]]); }
// one retaining tab: a 45 deg wedge swept over ring_tab_arc (grow for the panel's pocket)
module ring_tab(grow) rotate_extrude(angle = ring_tab_arc + 2 * grow * 10, $fn = 192)
  polygon([[acc_out - 0.05, -grow], [acc_out + 0.9 + grow * 1.414, -grow], [acc_out - 0.05, 1.1 + grow * 1.414]]);   // 41 deg
module dpad_ring() difference() {
  union() {
    translate([0, 0, pz0]) linear_extrude(T + 0.5 - pz0) circle(r = acc_out, $fn = 192);
    for (a = ring_tabs) rotate(a - ring_tab_arc / 2) translate([0, 0, pz0 - 0.01]) ring_tab(0);
  }
  translate([0, 0, pz0 - 5]) linear_extrude(10) { ring2d(0); circle(d = ok_d + 0.6, $fn = 96); }
}
// every cap where it sits (for the fit check); press moves them all down, tip tips the VOL rocker
module caps_asm(press = 0, tip = 0) {
  for (i = [0 : 3]) translate(concat(dc, [front_in - cap_flange - press])) ring_cap(i);
  translate(concat(dc, [front_in - cap_flange - press])) ok_cap_nub();
  for (k = round_keys) translate(concat(bpos(singles[k]), [front_in - cap_flange - press])) round_cap(cap_d, singles[k][3], rib_a = rib_a(k));
  translate([0, 0, -press]) rocker_at(rockers[0], tip);
  translate([0, 0, -press]) rocker_at(rockers[1]);
}
module caps_plate() {
  for (i = [0 : 3]) translate([i * 22 - 33, 0, 0]) translate([-dpad_sw * cos(i * 90), -dpad_sw * sin(i * 90), 0]) ring_cap(i);
  translate([-33, 24, 0]) ok_cap_nub();
  for (j = [0 : len(round_keys) - 1]) translate([-18 + j * 13, 24, 0]) round_cap(cap_d, singles[round_keys[j]][3], rib_a = rib_a(round_keys[j]));
  for (j = [0, 1]) translate([-24 + j * 16, 46, 0]) rocker(rockers[j][0], rockers[j][1]);
}
