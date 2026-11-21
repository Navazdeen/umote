#!/usr/bin/env bash
# Upload one release folder to the matching copyparty folder, /stl/<version>/.
# Usage: release/upload_to_copyparty.sh v7.1              (every file in release/v7.1/)
#        release/upload_to_copyparty.sh v7.1 a.stl b.stl  (only those files)
# Password: first line of ../.secret, or CPP_PW. Never uploads to the /stl/ root.
set -euo pipefail
VER="${1:?usage: $0 <version folder, e.g. v7.1> [file ...]}"; shift
BASE="${URL:-http://192.168.31.9:3923/stl/}"
cd "$(dirname "$0")/$VER"
URL="${BASE}${VER}/"
[ -n "${CPP_PW:-}" ] || CPP_PW="$(head -n1 ../../.secret | tr -d '\r\n')"
files=("$@"); [ ${#files[@]} -gt 0 ] || files=(*)
# copyparty keeps the old file and saves a renamed copy on PUT, so delete first, then upload
for f in "${files[@]}"; do
  [ -f "$f" ] || { echo "skip $f (not a file)"; continue; }
  curl -sk -o /dev/null -X POST -H "PW: $CPP_PW" "${URL}${f}?delete"
  echo "$(curl -sk -o /dev/null -w '%{http_code}' -H "PW: $CPP_PW" -T "$f" "${URL}${f}")  $f"
done
# check what's on the server against SHA256SUMS.txt
if [ -f SHA256SUMS.txt ]; then
  while read -r sum f; do
    got=$(curl -sk -H "PW: $CPP_PW" "${URL}${f}" | sha256sum | cut -d' ' -f1)
    [ "$got" = "$sum" ] && echo "ok        $f" || echo "MISMATCH  $f"
  done < SHA256SUMS.txt
fi
