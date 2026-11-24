// umote case v7 "Keel": part dispatcher. Print parts come out in print orientation; asm_* parts are
// in model (assembled) coordinates for the fit check and viewer.
// Render: openscad -D 'part="shell"' -o shell.stl case/v7/umote_v7.scad   (or case/v7/export.sh)
part = "params";
$fn = 64;
include <params.scad>
include <profile.scad>
include <wheel.scad>
include <keys.scad>
include <shell.scad>
include <backs.scad>
include <dock.scad>

// every value the checks need, as one JSON line
P = [["W", W], ["wall", wall], ["tip_wall", tip_wall], ["T", T], ["L", L], ["theta", theta], ["clr", clr],
  ["board_gap", board_gap], ["usb_x", usb_x], ["usb_in", usb_in], ["usb_body_h", usb_body_h], ["usb_floor", usb_floor],
  ["db_w", db_w], ["db_l", db_l], ["db_pcb", db_pcb], ["db_front", db_front], ["db_back", db_back], ["db_y0", db_y0],
  ["db_end", db_end], ["db_top", db_top], ["db_z0", db_z0], ["lcd_from_ant", lcd_from_ant], ["lcd_l", lcd_l],
  ["bb_w", bb_w], ["bb_l", bb_l], ["bb_pcb", bb_pcb], ["bb_y0", bb_y0], ["bb_z0", bb_z0], ["bb_top", bb_top],
  ["sw_body", sw_body], ["sw_total", sw_total], ["smd_h", smd_h], ["top_parts", top_parts],
  ["batt", batt], ["batt_y0", batt_y0], ["batt_z0", batt_z0], ["floor_t", floor_t], ["seat_z", seat_z],
  ["ir_x", ir_x], ["ir_z", ir_z], ["front_in", front_in], ["pan_t", pan_t], ["pz0", pz0],
  ["y_head_end", y_head_end], ["y_key_start", y_key_start], ["cy", cy], ["axle_z", axle_z],
  ["whl_d", whl_d], ["whl_w", whl_w], ["whl_x", whl_x], ["whl_proud", whl_proud], ["whl_gap", whl_gap], ["whl_well", whl_well],
  ["ec11_xf", ec11_xf], ["ec11_h", ec11_h], ["ec11_w", ec11_w], ["ec11_d", ec11_d], ["ec11_bush", ec11_bush], ["ec11_shaft", ec11_shaft],
  ["ec11_nut", ec11_nut], ["carrier", carrier], ["bulk_t", bulk_t], ["room_x", room_x], ["col_wall", col_wall],
  ["s2", s2], ["ps", ps], ["m2", m2], ["holes", holes], ["win", win], ["groove_x", groove_x], ["fit", fit],
  ["back_t", back_t], ["zb_tip", zb_tip], ["y_ap", y_ap], ["z_ap", z_ap], ["kh", kh], ["kk", kk], ["z_seat", z_seat],
  ["lip_clr", lip_clr], ["lip_w", lip_w], ["lip_h", lip_h], ["tap_depth", tap_depth], ["boss_hole", boss_hole],
  ["min_wall", min_wall], ["min_panel", min_panel], ["min_land", min_land], ["min_skin", min_skin],
  ["magnet", magnet], ["dmag_x", dmag_x], ["dmag_z", dmag_z], ["pad_insert", pad_insert], ["pad_x", pad_x], ["pad_z", pad_z],
  ["pogo_d", pogo_d], ["pogo_l", pogo_l], ["roll_z", roll_z], ["roll", roll], ["cap_proud", cap_proud],
  ["pp_w", pp_w], ["pp_z0", pp_z0], ["pp_t", pp_t], ["conn_b", conn_b], ["end_block_y", end_block_y],
  ["cap_hole", cap_hole], ["cap_d", cap_d], ["side_clr", side_clr], ["batt_end", batt_end], ["bb_end", bb_end], ["eye", eye],
  ["clip_y", clip_y], ["rib_x", rib_x], ["dock_g", dock_g],
  ["act_top", act_top], ["sock", sock], ["cap_h", cap_h], ["clip_t", clip_t], ["clip_w", clip_w], ["pocket_w", pocket_w]];
function jv(v) = is_list(v) ? str("[", jl(v, 0), "]") : str(v);
function jl(v, i) = i >= len(v) ? "" : str(jv(v[i]), i < len(v) - 1 ? "," : "", jl(v, i + 1));
function jo(p, i) = i >= len(p) ? "" : str("\"", p[i][0], "\":", jv(p[i][1]), i < len(p) - 1 ? "," : "", jo(p, i + 1));

// face down = turned over about y (a true flip: v6 used a mirror here, which made mirror-image panels)
module face_down() translate([0, 0, T]) rotate([0, 180, 0]) children();
// the 224 mm shell lies corner to corner on a 220 bed (it needs 196 x 196)
module shell_print() rotate([0, 0, 45]) translate([0, -L / 2, 0]) face_down() children();
module pp_print() translate([0, 0, -pp_z0]) children();                                    // contact plate: standing on its bottom
module dp_print() translate([0, 0, L + dock_g + dp_t]) rotate([-90, 0, 0]) children();   // dock plate: bottom face down

if (part == "params") { echo(str("PARAMS {", jo(P, 0), "}")); cube(0.01); }
else if (part == "envelope") envelope();
else if (part == "shell") shell_print() shell();
else if (part == "asm_shell") shell();
else if (part == "head_back") head_back_print() head_back();
else if (part == "asm_head_back") head_back();
else if (part == "key_back") key_back_print() key_back();
else if (part == "asm_key_back") key_back();
else if (part == "pogo_plate_a") pp_print() pogo_plate_a();
else if (part == "pogo_plate_b") pp_print() pogo_plate_b();
else if (part == "asm_pogo_plate_a") pogo_plate_a();
else if (part == "asm_pogo_plate_b") pogo_plate_b();
else if (part == "dock_plate_a") dp_print() dock_plate_a();
else if (part == "dock_plate_b") dp_print() dock_plate_b();
else if (part == "asm_dock_plate_a") dock_plate_a();
else if (part == "asm_dock_plate_b") dock_plate_b();
else if (part == "wheel") translate([0, 0, whl_w / 2]) rotate([0, 90, 0]) wheel();
else if (part == "asm_wheel") wheel_at();
else if (part == "asm_ec11") ec11_model();
else if (part == "asm_nut") ec11_nut_model();
else if (part == "asm_carrier") carrier_model();
else if (part == "caps") caps_plate();
else if (part == "caps_asm") caps_asm();
else if (part == "caps_asm_pressed") caps_asm(press = 0.3);
else if (part == "caps_asm_rocker_tilt") caps_asm(tip = 0.3);
else if (part == "dpad_ring") translate([0, 0, T + 0.5]) rotate([0, 180, 0]) dpad_ring_at();
else if (part == "asm_dpad_ring") dpad_ring_at();
else if (part == "dock") translate([0, 0, 20]) remote_to_world() dock();
else if (part == "asm_dock") dock();
else if (part == "asm_pogo") pogo_tips();
else if (part == "asm_all") asm_all();
else if (part == "asm_section") difference() { asm_all(); translate([-60, -10, -10]) cube([60 + sec_x, L + 20, 40]); }
else if (part == "t0_screw_gauge") t0();
else if (part == "t1_wheel_zone") t1();
else if (part == "t2_bottom_end") t2();
else assert(false, str("unknown part ", part));

sec_x = -4;  // asm_section: cut away x < sec_x
module asm_all() {
  color("dimgray") shell();
  color("white") head_back();
  color("white") key_back();
  color("gold") pogo_plate_a();
  color("orange") wheel_at();
  color("silver") { ec11_model(); ec11_nut_model(); }
  color("green") carrier_model();
}
module dpad_ring_at() translate(concat(dc, [0])) dpad_ring();

// ---------- test pieces: print these before the full set ----------
// T0 screw gauge: a bar with five self-tap holes (1.7 .. 2.1 as drawn), a clearance hole and a
// countersink, each marked by notches on the edge (1 notch = 1.7). Drive an M2 into each: the right
// one bites firmly without splitting the bar. Tell me which and m2[0] in params.scad is set to it.
gauge = [1.7, 1.8, 1.9, 2.0, 2.1];
module t0() difference() {
  hull() { cube([44, 8, 7.7]); translate([0.3, 0.3, 7.7]) cube([43.4, 7.4, 0.3]); }
  for (i = [0 : 4]) translate([4 + i * 6.5, 4, 1]) { cylinder(d = gauge[i], h = 10, $fn = 48); translate([0, 0, 6.6]) cylinder(d1 = gauge[i], d2 = gauge[i] + 0.9, h = 0.5, $fn = 48); }
  for (i = [0 : 4], n = [0 : i]) translate([4 + i * 6.5 - i * 0.6 + n * 1.2 - 0.3, -0.01, 5]) cube([0.6, 0.6, 4]);
  translate([38.5, 4, -1]) cylinder(d = m2[1], h = 10, $fn = 48);
  translate([38.5, 4, 8.01]) mirror([0, 0, 1]) m2_csk(3);
}
// T1 wheel zone: the shell from the display's last screws to the first key (bosses, cheeks,
// bulkhead, wheel window, tongue grooves), the head plate's end, the key plate's start and the wheel
module t1() {
  rotate([0, 0, 90]) translate([0, -cy, 0]) face_down() ycut(y_head_end - 10, y_key_start + 12) shell();
  translate([0, 45 - (y_head_end - 10), 0]) head_back_print() ycut(y_head_end - 10, 400) head_back();
  translate([0, 85 - y_ap, 0]) key_back_print() ycut(-100, y_key_start + 12) key_back();
  translate([40, 20, whl_w / 2]) rotate([0, 90, 0]) wheel();
}
// T2 bottom end: the shell's last 24 mm (end block, plate slot, eyelet, screw pilots), the key
// plate's end and plate A
module t2() {
  translate([0, -L, 0]) face_down() ycut(L - 24, L + 5) shell();
  translate([0, 40 - L, 0]) key_back_print() ycut(L - 24, L + 5) key_back();
  translate([0, 20 - L, 0]) pp_print() pogo_plate_a();
}
