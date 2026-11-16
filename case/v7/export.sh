#!/usr/bin/env bash
# Render v7 parts into case/stl_v7/ and dump the parameters to case/stl_v7/params.json.
# Usage: case/v7/export.sh part [part ...]      or      case/v7/export.sh all
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=stl_v7; mkdir -p "$OUT"
ALL="params shell head_back key_back wheel caps dpad_ring pogo_plate_a pogo_plate_b dock dock_plate_a dock_plate_b t0_screw_gauge t1_wheel_zone t2_bottom_end asm_shell asm_head_back asm_key_back asm_pogo_plate_a asm_pogo_plate_b asm_dock_plate_a asm_dock_plate_b asm_wheel asm_ec11 asm_nut asm_carrier caps_asm caps_asm_pressed caps_asm_rocker_tilt asm_dpad_ring asm_dock asm_pogo"
parts=("$@"); [ "${parts[0]:-all}" = all ] && read -r -a parts <<< "$ALL"
for p in "${parts[@]}"; do
  log="$OUT/$p.log"
  openscad -o "$OUT/$p.stl" -D "part=\"$p\"" v7/umote_v7.scad > "$log" 2>&1 || { cat "$log"; echo "FAILED $p"; exit 1; }
  if grep -q "WARNING:\|ERROR" "$log"; then cat "$log"; echo "FAILED $p (warnings)"; exit 1; fi
  if [ "$p" = params ]; then sed -n 's/^ECHO: "PARAMS \(.*\)"$/\1/p' "$log" | sed 's/\\"/"/g' > "$OUT/params.json"; rm -f "$OUT/params.stl"; fi
  echo "ok $p"
done
