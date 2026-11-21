#!/usr/bin/env bats

setup() {
  PROJECT_ROOT="$(cd "$BATS_TEST_DIRNAME/.." && pwd)"
  export PROJECT_ROOT
  export HOME="$BATS_TEST_TMPDIR/home"
  export TEST_LOG="$BATS_TEST_TMPDIR/commands.log"
  mkdir -p "$HOME" "$BATS_TEST_TMPDIR/bin"
  export PATH="$BATS_TEST_TMPDIR/bin:$PATH"
  : > "$TEST_LOG"

  cat > "$BATS_TEST_TMPDIR/bin/systemctl" <<'EOF'
#!/usr/bin/env bash
printf 'systemctl %s\n' "$*" >> "$TEST_LOG"
if [[ "${FAIL_SYSTEMCTL:-}" == "$*" ]]; then
  exit 1
fi
EOF
  cat > "$BATS_TEST_TMPDIR/bin/curl" <<'EOF'
#!/usr/bin/env bash
printf 'curl %s\n' "$2" >> "$TEST_LOG"
if [[ "${FAIL_DOWNLOAD:-}" == "${2##*/}" ]]; then
  exit 22
fi
cp "$PROJECT_ROOT/${2##*/}" "$4"
EOF
  cat > "$BATS_TEST_TMPDIR/bin/gsettings" <<'EOF'
#!/usr/bin/env bash
printf 'gsettings %s\n' "$*" >> "$TEST_LOG"
if [[ "$1" == get ]]; then
  printf "'old-value'\n"
fi
EOF
  chmod +x "$BATS_TEST_TMPDIR/bin/systemctl" \
    "$BATS_TEST_TMPDIR/bin/curl" "$BATS_TEST_TMPDIR/bin/gsettings"
}

@test "local install copies files and enables the service and timer" {
  run bash "$PROJECT_ROOT/install.sh"
  [ "$status" -eq 0 ]
  [[ "$output" == *"sunrise/sunset:"* ]]
  [ -x "$HOME/.local/bin/auto-theme.py" ]
  cmp "$PROJECT_ROOT/auto-theme.py" "$HOME/.local/bin/auto-theme.py"
  cmp "$PROJECT_ROOT/auto-theme.example.conf" "$HOME/.config/auto-theme.conf"
  cmp "$PROJECT_ROOT/auto-theme.service" "$HOME/.config/systemd/user/auto-theme.service"
  cmp "$PROJECT_ROOT/auto-theme.timer" "$HOME/.config/systemd/user/auto-theme.timer"
  grep -Fx "systemctl --user daemon-reload" "$TEST_LOG"
  grep -Fx "systemctl --user enable --now auto-theme.timer" "$TEST_LOG"
  grep -Fx "systemctl --user enable auto-theme.service" "$TEST_LOG"
  grep -Fx "systemctl --user start auto-theme.service" "$TEST_LOG"
  ! grep -q '^curl ' "$TEST_LOG"
}

@test "reinstall preserves an existing configuration" {
  mkdir -p "$HOME/.config"
  printf '[theme]\nlatitude = 51.5\n' > "$HOME/.config/auto-theme.conf"
  run bash "$PROJECT_ROOT/install.sh"
  [ "$status" -eq 0 ]
  [ "$(cat "$HOME/.config/auto-theme.conf")" = $'[theme]\nlatitude = 51.5' ]
}

@test "piped install downloads every required file" {
  export AUTO_THEME_RAW_BASE="https://example.invalid/project"
  run bash -s < "$PROJECT_ROOT/install.sh"
  [ "$status" -eq 0 ]
  for file in auto-theme.py auto-theme.service auto-theme.timer auto-theme.example.conf; do
    grep -Fx "curl $AUTO_THEME_RAW_BASE/$file" "$TEST_LOG"
  done
  cmp "$PROJECT_ROOT/auto-theme.example.conf" "$HOME/.config/auto-theme.conf"
}

@test "download failure stops installation before enabling units" {
  export FAIL_DOWNLOAD=auto-theme.timer
  run bash -s < "$PROJECT_ROOT/install.sh"
  [ "$status" -ne 0 ]
  [ ! -e "$HOME/.local/bin/auto-theme.py" ]
  ! grep -q '^systemctl ' "$TEST_LOG"
}

@test "systemctl failure stops installation" {
  export FAIL_SYSTEMCTL="--user enable --now auto-theme.timer"
  run bash "$PROJECT_ROOT/install.sh"
  [ "$status" -ne 0 ]
  ! grep -Fx 'systemctl --user start auto-theme.service' "$TEST_LOG"
  [[ "$output" != *"Installed auto-theme"* ]]
}

@test "installed service and timer validate and service command applies a theme" {
  run bash "$PROJECT_ROOT/install.sh"
  [ "$status" -eq 0 ]
  run systemd-analyze --user verify \
    "$HOME/.config/systemd/user/auto-theme.service" \
    "$HOME/.config/systemd/user/auto-theme.timer"
  [ "$status" -eq 0 ]

  grep -Fx 'ExecStart=%h/.local/bin/auto-theme.py' \
    "$HOME/.config/systemd/user/auto-theme.service"
  grep -Fx 'OnCalendar=*:0/5' "$HOME/.config/systemd/user/auto-theme.timer"
  printf '[theme]\nfixed_sunrise = 00:00\nfixed_sunset = 00:00\n' \
    > "$HOME/.config/auto-theme.conf"
  run "$HOME/.local/bin/auto-theme.py"
  [ "$status" -eq 0 ]
  grep -Fx 'gsettings set org.gnome.desktop.interface color-scheme prefer-dark' "$TEST_LOG"
  grep -Fx 'gsettings set org.cinnamon.desktop.interface gtk-theme Mint-Y-Dark' "$TEST_LOG"
}
