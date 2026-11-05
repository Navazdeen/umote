#!/usr/bin/env bash
# Replace the STLs in copyparty's /stl/ folder with the ones in this folder.
# Usage: ./upload_to_copyparty.sh                      (this folder -> /stl/)
#        URL=http://192.168.31.9:3923/stl/v5.0/ ./upload_to_copyparty.sh release/v5.0
# One folder per version (/stl/v5.0/, v5.1, ...): every file of that version goes up together.
set -euo pipefail
URL="${URL:-http://192.168.31.9:3923/stl/}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${1:-$(dirname "$0")}"
shopt -s nullglob
[ -n "${CPP_PW:-}" ] || CPP_PW="$(head -n1 "$ROOT/.secret" | tr -d '\r\n')"   # same login as SSH (user said so)
# copyparty keeps the old file and saves a renamed copy on PUT, so delete first, then upload
for f in *.stl *.zip *.png *.html; do
  curl -sk -o /dev/null -X POST -H "PW: $CPP_PW" "${URL}${f}?delete"
  code=$(curl -skf -o /dev/null -w '%{http_code}' -H "PW: $CPP_PW" -T "$f" "${URL}${f}") || { echo "upload failed: $f"; exit 1; }
  echo "$code  $f"
done
curl -sk -H "PW: $CPP_PW" "${URL}?ls" | python3 -c "import sys,json; [print(f\"{x['sz']:>9}  {x['href']}\") for x in json.load(sys.stdin)['files']]"
