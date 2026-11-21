#!/usr/bin/env bash
# Install: curl -fsSL https://raw.githubusercontent.com/edouard-lopez/linux-auto-dark-light-desktop-theme/main/install.sh | bash
set -euo pipefail

VERSION="1.0.0"
RAW_BASE="${AUTO_THEME_RAW_BASE:-https://raw.githubusercontent.com/edouard-lopez/linux-auto-dark-light-desktop-theme/main}"
FILES=(auto-theme.py auto-theme.service auto-theme.timer auto-theme.conf)

for cmd in curl python3 systemctl; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "Error: $cmd is required." >&2; exit 1; }
done

echo "auto-theme installer v$VERSION"

src=""
if [[ -n "${BASH_SOURCE[0]:-}" && -f "${BASH_SOURCE[0]}" ]]; then
  dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  [[ -f "$dir/auto-theme.py" ]] && src="$dir"
fi

if [[ -z "$src" ]]; then
  src="$(mktemp -d)"
  trap 'rm -rf "$src"' EXIT
  echo "Downloading files from $RAW_BASE"
  for f in "${FILES[@]}"; do
    curl -fsSL "$RAW_BASE/$f" -o "$src/$f"
  done
fi

cd "$src"
install -Dm755 auto-theme.py ~/.local/bin/auto-theme.py
install -Dm644 auto-theme.service ~/.config/systemd/user/auto-theme.service
install -Dm644 auto-theme.timer ~/.config/systemd/user/auto-theme.timer
[[ -f ~/.config/auto-theme.conf ]] || install -Dm644 auto-theme.conf ~/.config/auto-theme.conf
systemctl --user daemon-reload
systemctl --user enable --now auto-theme.timer
systemctl --user enable auto-theme.service
systemctl --user start auto-theme.service
~/.local/bin/auto-theme.py status
echo "Installed auto-theme v$VERSION. Edit ~/.config/auto-theme.conf to set your location."
