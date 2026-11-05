#!/usr/bin/env bash
# Render v6 parts into case/stl_v6/ and dump the parameters to case/stl_v6/params.json.
# Usage: case/v6/export.sh part [part ...]      or      case/v5/export.sh all
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=stl_v6; mkdir -p "$OUT"
ALL="params head_body head_panel frame ridge wheel key_body key_panel caps dpad_ring dock asm_head_body asm_head_panel asm_frame asm_ridge asm_wheel asm_ec11 asm_nut asm_carrier asm_key_body asm_key_panel caps_asm caps_asm_pressed caps_asm_rocker_tilt asm_dpad_ring asm_dock asm_pogo t1_wheel_zone t2_key_corner t3_bottom_end"
parts=("$@"); [ "${parts[0]:-all}" = all ] && read -r -a parts <<< "$ALL"
for p in "${parts[@]}"; do
  log="$OUT/$p.log"
  openscad -o "$OUT/$p.stl" -D "part=\"$p\"" v6/umote_v6.scad > "$log" 2>&1 || { cat "$log"; echo "FAILED $p"; exit 1; }
  if grep -q "WARNING:\|ERROR" "$log"; then cat "$log"; echo "FAILED $p (warnings)"; exit 1; fi
  if [ "$p" = params ]; then sed -n 's/^ECHO: "PARAMS \(.*\)"$/\1/p' "$log" | sed 's/\\"/"/g' > "$OUT/params.json"; rm -f "$OUT/params.stl"; fi
  echo "ok $p"
done
