#!/usr/bin/env bash
# Install: curl -fsSL https://raw.githubusercontent.com/edouard-lopez/linux-auto-dark-light-desktop-theme/main/install.sh | bash
set -euo pipefail

VERSION="1.0.0"
RAW_BASE="${AUTO_THEME_RAW_BASE:-https://raw.githubusercontent.com/edouard-lopez/linux-auto-dark-light-desktop-theme/main}"
FILES=(auto-theme.py auto-theme.service auto-theme.timer auto-theme.example.conf)

for cmd in curl python3 systemctl; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "Error: $cmd is required." >&2; exit 1; }
done

echo "auto-theme installer v$VERSION"

source_dir=""
if [[ -n "${BASH_SOURCE[0]:-}" && -f "${BASH_SOURCE[0]}" ]]; then
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  [[ -f "$script_dir/auto-theme.py" ]] && source_dir="$script_dir"
fi

if [[ -z "$source_dir" ]]; then
  source_dir="$(mktemp -d)"
  trap 'rm -rf "$source_dir"' EXIT
  echo "Downloading files from $RAW_BASE"
  for file in "${FILES[@]}"; do
    curl -fsSL "$RAW_BASE/$file" -o "$source_dir/$file"
  done
fi

install -Dm755 "$source_dir/auto-theme.py" ~/.local/bin/auto-theme.py
install -Dm644 "$source_dir/auto-theme.service" ~/.config/systemd/user/auto-theme.service
install -Dm644 "$source_dir/auto-theme.timer" ~/.config/systemd/user/auto-theme.timer
if [[ ! -f ~/.config/auto-theme.conf ]]; then
  install -Dm644 "$source_dir/auto-theme.example.conf" ~/.config/auto-theme.conf
fi
systemctl --user daemon-reload
systemctl --user enable --now auto-theme.timer
systemctl --user enable auto-theme.service
systemctl --user start auto-theme.service
~/.local/bin/auto-theme.py status
echo "Installed auto-theme v$VERSION. Edit ~/.config/auto-theme.conf to set your location."
