#!/usr/bin/env bash
# Copy the umote integration to Home Assistant over the SSH add-on, check the config, restart core.
set -euo pipefail
HOST=${HA_HOST:-192.168.31.91}
SSH=(ssh -p 2222 -i "$HOME/.ssh/home3d_ha_ed25519" -o ConnectTimeout=10 "root@$HOST")
cd "$(dirname "$0")/custom_components"
tar --exclude=__pycache__ -czf - umote | "${SSH[@]}" 'rm -rf /config/custom_components/umote && mkdir -p /config/custom_components && tar -xzf - -C /config/custom_components'
"${SSH[@]}" 'ha core check && ha core restart'
echo "deployed; HA core restarting"
