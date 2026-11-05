#!/usr/bin/env bash
# Render v5 parts into case/stl_v5/ and dump the parameters to case/stl_v5/params.json.
# Usage: case/v5/export.sh part [part ...]      or      case/v5/export.sh all
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=stl_v5; mkdir -p "$OUT"
ALL="params envelope envelope_bent"
parts=("$@"); [ "${parts[0]:-all}" = all ] && read -r -a parts <<< "$ALL"
for p in "${parts[@]}"; do
  log="$OUT/$p.log"
  openscad -o "$OUT/$p.stl" -D "part=\"$p\"" v5/umote_v5.scad > "$log" 2>&1 || { cat "$log"; echo "FAILED $p"; exit 1; }
  if grep -q "WARNING:\|ERROR" "$log"; then cat "$log"; echo "FAILED $p (warnings)"; exit 1; fi
  if [ "$p" = params ]; then sed -n 's/^ECHO: "PARAMS \(.*\)"$/\1/p' "$log" | sed 's/\\"/"/g' > "$OUT/params.json"; rm -f "$OUT/params.stl"; fi
  echo "ok $p"
done
