#!/usr/bin/env bash
# Dump + validate (and optionally screenshot) simulator fixtures.
#   tools/run_sim.sh [--shots] FIXTURE[:STATE[:PAGE]] ...
# Needs the sim built (esphome compile sim.yaml) and SDL from ../.sdl.
set -uo pipefail
cd "$(dirname "$0")/.."
export LD_LIBRARY_PATH="$PWD/../.sdl/lib"
BIN=.esphome/build/remote-sim/.pioenvs/remote-sim/program
OUT=${SIM_OUT:-/tmp/umote-sim}; mkdir -p "$OUT" screens
SHOTS=0; [ "${1:-}" = "--shots" ] && { SHOTS=1; shift; }
rc=0
for spec in "$@"; do
  IFS=: read -r fx st page <<<"$spec"; st=${st:-normal}
  penv=(); [ -n "$page" ] && penv=(SIM_PAGE="$page"); page=${page:-f}
  dump="$OUT/$fx-$st-$page.jsonl"; rm -f "$dump"
  env "${penv[@]}" SDL_VIDEODRIVER=dummy SIM_DUMP="$dump" SIM_FIXTURE="$fx" SIM_STATE="$st" timeout 20 "$BIN" >/dev/null 2>&1
  if ! ../.venv/bin/python tools/check_ui.py "$dump"; then rc=1; fi
  if [ $SHOTS = 1 ]; then
    xvfb-run -a -s "-screen 0 240x320x24" bash -c "${penv[*]} SIM_FIXTURE=$fx SIM_STATE=$st timeout 6 $BIN >/dev/null 2>&1 & sleep 3; import -window root screens/${fx}_${st}_p${page}.png; wait" 2>/dev/null
  fi
done
exit $rc
