// umote case v5: part dispatcher. Print parts come out in print orientation; asm_* parts are in
// model (assembled) coordinates for the fit check and viewer.
// Render: openscad -D 'part="key_body"' -o key_body.stl case/v5/umote_v5.scad   (or case/v5/export.sh)
part = "params";
$fn = 64;
include <params.scad>
include <profile.scad>
include <head_half.scad>
include <collar.scad>

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
  ["whl_d", whl_d], ["whl_w", whl_w], ["whl_proud", whl_proud], ["ec11", ec11], ["tact", tact],
  ["cradle_travel", cradle_travel], ["fork_x", fork_x], ["fork_y", fork_y], ["key_tongue", key_tongue],
  ["magnet", magnet], ["pad_insert", pad_insert], ["pogo_d", pogo_d], ["pogo_l", pogo_l], ["snap_uc", snap_uc]];
function jv(v) = is_list(v) ? str("[", jl(v, 0), "]") : str(v);
function jl(v, i) = i >= len(v) ? "" : str(jv(v[i]), i < len(v) - 1 ? "," : "", jl(v, i + 1));
function jo(p, i) = i >= len(p) ? "" : str("\"", p[i][0], "\":", jv(p[i][1]), i < len(p) - 1 ? "," : "", jo(p, i + 1));

if (part == "params") { echo(str("PARAMS {", jo(P, 0), "}")); cube(0.01); }
else if (part == "envelope") envelope();
else if (part == "envelope_bent") union() { ycut(y_key_start, L + 1) envelope(); head_xf() ycut(-1, y_head_end) envelope(); }
else if (part == "snap_test") snap_test();
else if (part == "roller_test") roller_test();
else if (part == "head_body") head_body();
else if (part == "head_panel") translate([0, 0, T]) mirror([0, 0, 1]) head_panel();
else if (part == "asm_head_body") head_xf() head_body();
else if (part == "asm_head_panel") head_xf() head_panel();
else if (part == "asm_collar_core") collar_core();
else if (part == "asm_wheel") translate([whl_x, cy, axle_z]) wheel();
else if (part == "asm_cradle") cradle();
else if (part == "asm_ec11") ec11_envelope();
else assert(false, str("unknown part ", part));

// ---------- test prints ----------
// snap_test: the head's tip corner (back down) and the panel's tip corner (face down), side by side.
// Tip-wall snaps with undercuts 0.3 / 0.4 / 0.5 (1 / 2 / 3 dots inside the panel) and one side-wall snap (0.4).
st_uc = [0.3, 0.4, 0.5];  st_x = [4, 10.5, 17];
module st_box() { translate([-3, -1, -1]) cube([29.5, 15, 30]); }
module snap_test() {
  intersection() { st_box(); difference() {
    envelope(); head_cavity(); panel_zone(0);
    for (i = [0 : 2]) translate([st_x[i], tip_snap_y, snap_root_z]) rotate(-90) catch(st_uc[i]);
    translate([side_snap_x, 6.0, snap_root_z]) catch(0.4, gap = 1.0);
  } }
  translate([0, 40, T]) mirror([0, 0, 1]) difference() {
    union() {
      intersection() { st_box(); panel_zone(pcl); }
      for (i = [0 : 2]) translate([st_x[i], tip_snap_y, snap_root_z]) rotate(-90) snap(st_uc[i]);
      translate([side_snap_x, 6.0, snap_root_z]) snap(0.4, gap = 1.0);
    }
    for (i = [0 : 2]) for (k = [0 : i]) translate([st_x[i] - 2 + k * 1.6, 9, pz0 - 0.1]) cylinder(d = 0.9, h = 0.5, $fn = 16);
  }
}
// roller_test: the collar without its fork and slots (standing on its key face), the wheel and the cradle.
// the collar prints standing on its key-side face (assembled +y points down)
module collar_print() translate([0, 0, y_key_start]) rotate([-90, 0, 0]) children();
module roller_test() {
  collar_print() collar_core();
  translate([0, 45, whl_w / 2]) rotate([0, 90, 0]) wheel();
  translate([0, 30 - 85, -cr_z0]) cradle();
}
