#!/usr/bin/env bash
# Replace the firmware files in copyparty's /firmware/ folder with the ones in this folder.
# Usage: ./upload_to_copyparty.sh            (password from ../.secret, or CPP_PW)
# secrets.yaml (your real WiFi password) is never uploaded; secrets.example.yaml is.
set -euo pipefail
URL="${URL:-http://192.168.31.9:3923/firmware/}"
cd "$(dirname "$0")"
[ -n "${CPP_PW:-}" ] || CPP_PW="$(head -n1 ../.secret | tr -d '\r\n')"
# copyparty creates /firmware/ (and screens/) on the first PUT.
# copyparty keeps the old file and saves a renamed copy on PUT, so delete first, then upload
for f in remote.yaml ui.yaml sim.yaml voice_relay.py secrets.example.yaml upload_to_copyparty.sh; do
  curl -sk -o /dev/null -X POST -H "PW: $CPP_PW" "${URL}${f}?delete"
  code=$(curl -sk -o /dev/null -w '%{http_code}' -H "PW: $CPP_PW" -T "$f" "${URL}${f}")
  echo "$code  $f"
done
for f in screens/*.png; do
  [ -e "$f" ] || continue
  curl -sk -o /dev/null -X POST -H "PW: $CPP_PW" "${URL}${f}?delete"
  code=$(curl -sk -o /dev/null -w '%{http_code}' -H "PW: $CPP_PW" -T "$f" "${URL}${f}")
  echo "$code  $f"
done
curl -sk -H "PW: $CPP_PW" "${URL}?ls" | python3 -c "import sys,json; [print(f\"{x['sz']:>9}  {x['href']}\") for x in json.load(sys.stdin)['files']]"
