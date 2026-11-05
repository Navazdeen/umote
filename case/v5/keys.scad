// umote case v5: key geometry shared by the key panel and the caps (v4's D-pad ring and sectors,
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
vol = [bpos(singles[4]), bpos(singles[5])];  ch = [bpos(singles[7]), bpos(singles[8])];
acc_in = ring_out;  acc_out = ring_out + 1.5;      // D-pad ring (accent part): the opening's rim
