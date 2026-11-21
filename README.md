# Auto dark mode (Cinnamon, Fedora 44 / Ubuntu 26.10)

1. Install (or update) with:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/edouard-lopez/linux-auto-dark-light-desktop-theme/main/install.sh | bash
   ```
   Or from a clone: `./install.sh`.
3. Edit `~/.config/auto-theme.conf`: set latitude/longitude and theme names.
   List themes: `ls /usr/share/themes ~/.themes`.

Commands:
- `auto-theme.py status` shows today's sunrise/sunset.
- `auto-theme.py dark` or `light` forces a mode until the next check (max 5 min).
- Logs: `journalctl --user -u auto-theme`.

Uninstall (config is kept):
```bash
curl -fsSL https://raw.githubusercontent.com/edouard-lopez/linux-auto-dark-light-desktop-theme/main/uninstall.sh | bash
```

Tests: `python3 -m unittest discover tests`


## Changelog

### 1.0.0
- Initial release: switch Cinnamon dark/light theme at sunrise/sunset.
- systemd user timer and service.
- Unit tests.
- curl one-liner installer and uninstaller.
