// umote case v5: part dispatcher. Print parts come out in print orientation; asm_* parts are in
// model (assembled) coordinates for the fit check and viewer.
// Render: openscad -D 'part="key_body"' -o key_body.stl case/v5/umote_v5.scad   (or case/v5/export.sh)
part = "params";
$fn = 64;
include <params.scad>
include <profile.scad>

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
else assert(false, str("unknown part ", part));
