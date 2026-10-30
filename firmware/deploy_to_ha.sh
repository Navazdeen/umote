#!/usr/bin/env bash
# Add the remote to Home Assistant's ESPHome Device Builder (/config/esphome) over the SSH add-on,
# the same way home3d/tools/deploy.sh reaches HA.
#   /config/esphome/tv-remote.yaml      <- remote.yaml (include path rewritten)
#   /config/esphome/tv-remote/ui.yaml   <- ui.yaml (in a subfolder so the dashboard doesn't list it as a device)
#   /config/esphome/tv-remote-diag.yaml <- diag.yaml (USB-serial-log build for bring-up, same device)
# Refuses to overwrite an existing tv-remote.yaml unless FORCE=1.
# Checks that secrets.yaml defines wifi_ssid and wifi_password (prints only yes/no, never values).
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
sed 's#ui: !include ui.yaml#ui: !include tv-remote/ui.yaml#' remote.yaml | "${SSH[@]}" "cat > $D/tv-remote.yaml"
"${SSH[@]}" "cat > $D/tv-remote/ui.yaml" < ui.yaml
sed 's#base: !include remote.yaml#base: !include tv-remote.yaml#' diag.yaml | "${SSH[@]}" "cat > $D/tv-remote-diag.yaml"
"${SSH[@]}" "ls -la $D/tv-remote.yaml $D/tv-remote/ui.yaml $D/tv-remote-diag.yaml
  for k in wifi_ssid wifi_password; do
    if grep -q \"^\$k:\" $D/secrets.yaml 2>/dev/null; then echo \"secrets.yaml has \$k: yes\"; else echo \"secrets.yaml has \$k: NO - add it\"; fi
  done"
echo "Done. Open http://192.168.31.91:8123 -> ESPHome Device Builder -> tv-remote"
