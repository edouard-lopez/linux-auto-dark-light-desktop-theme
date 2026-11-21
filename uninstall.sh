#!/usr/bin/env bash
# Uninstall: curl -fsSL https://raw.githubusercontent.com/edouard-lopez/linux-auto-dark-light-desktop-theme/main/uninstall.sh | bash
set -euo pipefail
command -v systemctl >/dev/null 2>&1 || { echo "Error: systemctl is required." >&2; exit 1; }
systemctl --user disable --now auto-theme.timer auto-theme.service 2>/dev/null || true
rm -f ~/.local/bin/auto-theme.py ~/.config/systemd/user/auto-theme.service ~/.config/systemd/user/auto-theme.timer
systemctl --user daemon-reload
echo "Removed. Config kept at ~/.config/auto-theme.conf"
