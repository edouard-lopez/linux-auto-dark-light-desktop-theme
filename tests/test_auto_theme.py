"""Run: python3 -m unittest discover tests"""

import configparser
import datetime as dt
import importlib.util
from pathlib import Path
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("auto_theme", ROOT / "auto-theme.py")
auto_theme = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auto_theme)
PARIS = dict(auto_theme.DEFAULT)
UTC = dt.timezone.utc


class ExampleConfig(unittest.TestCase):
    def test_example_matches_defaults(self):
        config = configparser.ConfigParser()
        config.read(ROOT / "auto-theme.example.conf")
        self.assertEqual(dict(config["theme"]), auto_theme.DEFAULT)


class SunTimes(unittest.TestCase):
    def test_paris_summer_solstice(self):
        sunrise, sunset = auto_theme.sun_times(48.85, 2.35, dt.date(2026, 6, 21))
        sunrise, sunset = sunrise.astimezone(UTC), sunset.astimezone(UTC)
        self.assertAlmostEqual(sunrise.hour * 60 + sunrise.minute, 3 * 60 + 47, delta=5)
        self.assertAlmostEqual(sunset.hour * 60 + sunset.minute, 19 * 60 + 58, delta=5)

    def test_polar_night_returns_none(self):
        self.assertIsNone(auto_theme.sun_times(78.2, 15.6, dt.date(2026, 12, 21)))


class IsDark(unittest.TestCase):
    def at_utc(self, hour):
        return dt.datetime(2026, 6, 21, hour, 0, tzinfo=UTC)

    def test_noon_light(self):
        self.assertFalse(auto_theme.is_dark(PARIS, self.at_utc(12)))

    def test_midnight_dark(self):
        self.assertTrue(auto_theme.is_dark(PARIS, self.at_utc(0)))

    def test_fixed_times(self):
        config = dict(PARIS, fixed_sunrise="07:00", fixed_sunset="19:00")
        self.assertTrue(auto_theme.is_dark(config, dt.datetime(2026, 1, 1, 6, 59)))
        self.assertFalse(auto_theme.is_dark(config, dt.datetime(2026, 1, 1, 7, 0)))
        self.assertTrue(auto_theme.is_dark(config, dt.datetime(2026, 1, 1, 19, 0)))


class Apply(unittest.TestCase):
    def run_apply(self, dark, current="'x'"):
        calls = []

        def fake_run(command, **kwargs):
            calls.append(command)
            return mock.Mock(returncode=0, stdout=current)

        with mock.patch.object(auto_theme.subprocess, "run", fake_run), mock.patch("builtins.print"):
            auto_theme.apply(dark, PARIS)
        return [command[2:] for command in calls if command[1] == "set"]

    def test_dark_sets_keys(self):
        settings = self.run_apply(True)
        self.assertIn(["org.x.apps.portal", "color-scheme", "prefer-dark"], settings)
        self.assertIn(["org.cinnamon.desktop.interface", "gtk-theme", "Mint-Y-Dark"], settings)

    def test_light_sets_default(self):
        self.assertIn(
            ["org.gnome.desktop.interface", "color-scheme", "default"],
            self.run_apply(False),
        )

    def test_no_write_when_already_set(self):
        settings = self.run_apply(True, current="'prefer-dark'")
        self.assertNotIn(["org.x.apps.portal", "color-scheme", "prefer-dark"], settings)


if __name__ == "__main__":
    unittest.main()
