# Auto dark mode (Cinnamon, Fedora 44 / Ubuntu 26.10)

1. Install (or update) with:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/edouard-lopez/linux-auto-dark-light-desktop-theme/main/install.sh | bash
   ```
   Or from a clone: `./install.sh`.
2. Edit `~/.config/auto-theme.conf`: set latitude/longitude and theme names.
   List themes: `ls /usr/share/themes ~/.themes`.
   See [auto-theme.example.conf](auto-theme.example.conf) for all options.
   The installer creates the config from this example only if it does not
   already exist.

Commands:
- `auto-theme.py status` shows today's sunrise/sunset.
- `auto-theme.py dark` or `light` forces a mode until the next check (max 5 min).
- Logs: `journalctl --user -u auto-theme`.

Uninstall (config is kept):
```bash
curl -fsSL https://raw.githubusercontent.com/edouard-lopez/linux-auto-dark-light-desktop-theme/main/uninstall.sh | bash
```

Tests:
```bash
python3 -m unittest discover tests
bats tests/install.bats
```

The shell tests require Bats, Python 3, and `systemd-analyze`. They use a
temporary home and mock `systemctl`, `curl`, and `gsettings`; they validate
the unit files and run the installed service command, but do not start a real
systemd user session or change desktop settings.


## Changelog

See [CHANGELOG.md](CHANGELOG.md).
