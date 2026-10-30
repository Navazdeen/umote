#!/usr/bin/env bash
# Replace the STLs in copyparty's /stl/ folder with the ones in this folder.
# Usage: ./upload_to_copyparty.sh            (asks for the copyparty password)
set -euo pipefail
URL="${URL:-http://192.168.31.9:3923/stl/}"
cd "$(dirname "$0")"
[ -n "${CPP_PW:-}" ] || CPP_PW="$(head -n1 ../.secret | tr -d '\r\n')"   # same login as SSH (user said so)
# copyparty keeps the old file and saves a renamed copy on PUT, so delete first, then upload
for f in *.stl *.zip button_board_copper_guide.png; do
  curl -sk -o /dev/null -X POST -H "PW: $CPP_PW" "${URL}${f}?delete"
  code=$(curl -sk -o /dev/null -w '%{http_code}' -H "PW: $CPP_PW" -T "$f" "${URL}${f}")
  echo "$code  $f"
done
curl -sk -H "PW: $CPP_PW" "${URL}?ls" | python3 -c "import sys,json; [print(f\"{x['sz']:>9}  {x['href']}\") for x in json.load(sys.stdin)['files']]"
