# Changelog

Versions follow [Semantic Versioning](https://semver.org/).

## Unreleased

### Added
- An example configuration documenting each option.
- Isolated Bats tests for installation and the service and timer units.

### Changed
- Refactored the theme switcher, installer, and Python tests for readability.
- The installer now uses the example configuration for new installations and
  continues to preserve existing user configurations.

### Removed
- The repository's `auto-theme.conf` template, replaced by
  `auto-theme.example.conf`. Existing user configurations are not removed.

## 1.0.0

### Added
- Automatic Cinnamon dark/light theme switching at sunrise and sunset.
- systemd user timer and service.
- Unit tests.
- curl one-liner installer and uninstaller.
