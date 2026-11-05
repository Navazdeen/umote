// umote case v6: part dispatcher. Print parts come out in print orientation; asm_* parts are in
// model (assembled) coordinates for the fit check and viewer.
// Render: openscad -D 'part="key_body"' -o key_body.stl case/v6/umote_v6.scad   (or case/v6/export.sh)
part = "params";
$fn = 64;
include <params.scad>
include <profile.scad>
include <head_half.scad>
include <collar.scad>
include <keys.scad>
include <key_half.scad>
include <dock.scad>

// every value the checks need, as one JSON line
P = [["W", W], ["wall", wall], ["tip_wall", tip_wall], ["T", T], ["L", L], ["theta", theta], ["clr", clr],
  ["board_gap", board_gap], ["usb_x", usb_x], ["usb_in", usb_in], ["usb_body_h", usb_body_h], ["usb_floor", usb_floor],
  ["db_w", db_w], ["db_l", db_l], ["db_pcb", db_pcb], ["db_front", db_front], ["db_back", db_back], ["db_y0", db_y0],
  ["db_end", db_end], ["db_top", db_top], ["db_z0", db_z0], ["lcd_from_ant", lcd_from_ant], ["lcd_l", lcd_l],
  ["bb_w", bb_w], ["bb_l", bb_l], ["bb_pcb", bb_pcb], ["bb_y0", bb_y0], ["bb_z0", bb_z0], ["bb_top", bb_top],
  ["sw_body", sw_body], ["sw_total", sw_total], ["smd_h", smd_h], ["top_parts", top_parts],
  ["batt", batt], ["batt_y0", batt_y0], ["batt_z0", batt_z0], ["floor_t", floor_t],
  ["ir_x", ir_x], ["ir_z", ir_z], ["front_in", front_in], ["pan_t", pan_t], ["land", land], ["pcl", pcl],
  ["y_head_end", y_head_end], ["y_key_start", y_key_start], ["cy", cy], ["axle_z", axle_z],
  ["whl_d", whl_d], ["whl_w", whl_w], ["whl_x", whl_x], ["whl_proud", whl_proud], ["whl_gap", whl_gap],
  ["ec11_xf", ec11_xf], ["ec11_h", ec11_h], ["ec11_w", ec11_w], ["ec11_d", ec11_d], ["ec11_bush", ec11_bush], ["ec11_shaft", ec11_shaft],
  ["ec11_nut", ec11_nut], ["carrier", carrier], ["bulk_t", bulk_t],
  ["rail_x", rail_x], ["col_x", col_x], ["col_wall", col_wall], ["cap_z", cap_z], ["ridge_h", ridge_h], ["ridge_in", ridge_in],
  ["s1", s1], ["s2", s2], ["s3", s3], ["s3_d", s3_d], ["ps", ps], ["m2", m2], ["holes", holes],
  ["ten_x0", ten_x0], ["ten_x1", ten_x1], ["ten_top", ten_top], ["ten_len", ten_len], ["win", win], ["groove_x", groove_x],
  ["min_wall", min_wall], ["min_panel", min_panel], ["min_land", min_land], ["min_skin", min_skin],
  ["magnet", magnet], ["dmag_x", dmag_x], ["dmag_z", dmag_z], ["pad_insert", pad_insert], ["pad_x", pad_x], ["pad_z", pad_z],
  ["pogo_d", pogo_d], ["pogo_l", pogo_l], ["roll_z", roll_z], ["roll", roll], ["pz0", pz0], ["cap_proud", cap_proud],
  ["cap_hole", cap_hole], ["cap_d", cap_d], ["side_clr", side_clr], ["batt_end", batt_end], ["bb_end", bb_end], ["eye", eye]];
function jv(v) = is_list(v) ? str("[", jl(v, 0), "]") : str(v);
function jl(v, i) = i >= len(v) ? "" : str(jv(v[i]), i < len(v) - 1 ? "," : "", jl(v, i + 1));
function jo(p, i) = i >= len(p) ? "" : str("\"", p[i][0], "\":", jv(p[i][1]), i < len(p) - 1 ? "," : "", jo(p, i + 1));

module frame_print() translate([0, 0, T]) mirror([0, 0, 1]) children();      // cap down
module ridge_print() translate([0, 0, ridge_h]) children();                    // bottom down

if (part == "params") { echo(str("PARAMS {", jo(P, 0), "}")); cube(0.01); }
else if (part == "envelope") envelope();
else if (part == "head_body") head_body();
else if (part == "head_panel") translate([0, 0, T]) mirror([0, 0, 1]) head_panel();
else if (part == "asm_head_body") head_xf() head_body();
else if (part == "asm_head_panel") head_xf() head_panel();
else if (part == "frame") frame_print() frame();
else if (part == "asm_frame") frame();
else if (part == "ridge") ridge_print() ridge();
else if (part == "asm_ridge") ridge();
else if (part == "wheel") translate([0, 0, whl_w / 2]) rotate([0, 90, 0]) wheel();
else if (part == "asm_wheel") wheel_at();
else if (part == "asm_ec11") ec11_model();
else if (part == "asm_nut") ec11_nut_model();
else if (part == "asm_carrier") carrier_model();
else if (part == "key_body") key_body();
else if (part == "asm_key_body") key_body();
else if (part == "key_panel") translate([0, 0, T]) mirror([0, 0, 1]) key_panel();
else if (part == "asm_key_panel") key_panel();
else if (part == "caps") caps_plate();
else if (part == "caps_asm") caps_asm();
else if (part == "caps_asm_pressed") caps_asm(press = 0.3);
else if (part == "caps_asm_rocker_tilt") caps_asm(tip = 0.3);
else if (part == "dpad_ring") translate([0, 0, T + 0.5]) mirror([0, 0, 1]) dpad_ring_at();
else if (part == "asm_dpad_ring") dpad_ring_at();
else if (part == "dock") translate([0, 0, 20]) remote_to_world() dock();
else if (part == "asm_dock") dock();
else if (part == "asm_pogo") pogo_tips();
else if (part == "asm_all") asm_all();
else if (part == "asm_section") difference() { asm_all(); translate([-60, -10, -10]) cube([60 + sec_x, L + 20, 40]); }
else if (part == "t1_wheel_zone") t1();
else if (part == "t2_key_corner") t2();
else if (part == "t3_bottom_end") t3();
else assert(false, str("unknown part ", part));

sec_x = -4;  // asm_section: cut away x < sec_x
module asm_all() {
  color("white") head_xf() head_body();
  color("gray") head_xf() head_panel();
  color("white") key_body();
  color("dimgray") key_panel();
  color("black") frame();
  color("darkslategray") ridge();
  color("orange") wheel_at();
  color("silver") { ec11_model(); ec11_nut_model(); }
  color("green") carrier_model();
}
module dpad_ring_at() translate(concat(dc, [0])) dpad_ring();

// ---------- test pieces (spec v6 section 7), each in print orientation, side by side ----------
// T1 wheel zone: the head's last 14 mm (with tenons), the key body's wheel zone + 10 mm, the frame,
// the ridge and the wheel. Confirms the EC11 fit, the nut, the wheel's press fit and the joint.
module t1() {
  intersection() { head_body(); translate([-60, y_head_end - 14, -10]) cube([120, 30, 40]); }
  translate([0, -70, 0]) intersection() { key_body(); translate([-60, -10, -10]) cube([120, y_key_start + 10 + 10, 40]); }
  translate([60, -40, 0]) frame_print() frame();
  translate([60, -10, 0]) ridge_print() ridge();
  translate([60, 30, whl_w / 2]) rotate([0, 90, 0]) wheel();
}
// T2 key corner: a 40 mm slice of the key body from the wheel zone, and the same slice of the panel
// (tongues, ledge, VOL rocker hole, a round key hole).
module t2() {
  intersection() { key_body(); translate([-60, y_key_start - 2, -10]) cube([120, 42, 40]); }
  translate([60, 0, 0]) intersection() { translate([0, 0, T]) mirror([0, 0, 1]) key_panel(); translate([-60, y_key_start - 3, -10]) cube([120, 43, 40]); }
}
// T3 bottom end: the last 20 mm of the key body (pads, magnets, eyelet, panel screws) and of the panel
module t3() {
  intersection() { key_body(); translate([-60, L - 20, -10]) cube([120, 30, 40]); }
  translate([60, 0, 0]) intersection() { translate([0, 0, T]) mirror([0, 0, 1]) key_panel(); translate([-60, L - 20, -10]) cube([120, 30, 40]); }
}
