#!/usr/bin/env bash
# Add the remote to Home Assistant's ESPHome Device Builder (/config/esphome) over the SSH add-on,
# the same way home3d/tools/deploy.sh reaches HA.
#   /config/esphome/tv-remote.yaml      <- remote.yaml (include path rewritten)
#   /config/esphome/tv-remote/          <- ui.yaml, ui_res.yaml, assets.yaml, logic.h, ui_lv.h, assets/
#                                          (a subfolder so the dashboard doesn't list them as devices;
#                                          paths that ESPHome resolves from the config dir are rewritten)
# Refuses to overwrite an existing tv-remote.yaml unless FORCE=1.
# Checks that secrets.yaml defines wifi_ssid, wifi_password, tv_mac, api_key and ota_password (prints only yes/no, never values).
set -euo pipefail
cd "$(dirname "$0")"
HOST="${HA_SSH:-root@192.168.31.91}"
KEY="${HA_SSH_KEY:-$HOME/.ssh/home3d_ha_ed25519}"
SSH=(ssh -p "${HA_SSH_PORT:-2222}" -i "$KEY" -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new "$HOST")
D=/config/esphome

if [ "${FORCE:-0}" != 1 ] && "${SSH[@]}" "test -e $D/tv-remote.yaml"; then
  echo "$D/tv-remote.yaml already exists; re-run with FORCE=1 to replace it" >&2
  exit 1
fi
"${SSH[@]}" "mkdir -p $D/tv-remote"
sed -e 's#ui: !include ui.yaml#ui: !include tv-remote/ui.yaml#' \
    -e 's#assets: !include assets.yaml#assets: !include tv-remote/assets.yaml#' remote.yaml | "${SSH[@]}" "cat > $D/tv-remote.yaml"
REV=$(cat logic.h ui_lv.h | md5sum | cut -c1-8)
sed -e 's#^    - logic.h#    - tv-remote/logic.h#' -e 's#^    - ui_lv.h#    - tv-remote/ui_lv.h#' \
    -e "s#^  ui_rev: \"dev\"#  ui_rev: \"$REV\"#" ui.yaml | "${SSH[@]}" "cat > $D/tv-remote/ui.yaml"
sed 's#file: assets/#file: tv-remote/assets/#' assets.yaml | "${SSH[@]}" "cat > $D/tv-remote/assets.yaml"
tar -czf - ui_res.yaml logic.h ui_lv.h assets | "${SSH[@]}" "rm -rf $D/tv-remote/assets && tar -xzf - -C $D/tv-remote"
"${SSH[@]}" "ls -la $D/tv-remote.yaml $D/tv-remote
  for k in wifi_ssid wifi_password tv_mac api_key ota_password; do
    if grep -q \"^\$k:\" $D/secrets.yaml 2>/dev/null; then echo \"secrets.yaml has \$k: yes\"; else echo \"secrets.yaml has \$k: NO - add it\"; fi
  done"
echo "Done. Open http://192.168.31.91:8123 -> ESPHome Device Builder -> tv-remote"
