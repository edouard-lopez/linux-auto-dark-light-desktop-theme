"""Run: python3 -m unittest discover tests"""
import datetime as dt, importlib.util, os, unittest
from unittest import mock

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("auto_theme", os.path.join(HERE, "auto-theme.py"))
at = importlib.util.module_from_spec(spec); spec.loader.exec_module(at)
PARIS = dict(at.DEFAULT)
UTC = dt.timezone.utc

class SunTimes(unittest.TestCase):
    def test_paris_summer_solstice(self):
        r, s = at.sun_times(48.85, 2.35, dt.date(2026, 6, 21))
        r, s = r.astimezone(UTC), s.astimezone(UTC)
        self.assertAlmostEqual(r.hour*60 + r.minute, 3*60 + 47, delta=5)   # 05:47 CEST
        self.assertAlmostEqual(s.hour*60 + s.minute, 19*60 + 58, delta=5)  # 21:58 CEST

    def test_polar_night_returns_none(self):
        self.assertIsNone(at.sun_times(78.2, 15.6, dt.date(2026, 12, 21)))

class IsDark(unittest.TestCase):
    def at_utc(self, h):
        return dt.datetime(2026, 6, 21, h, 0, tzinfo=UTC)
    def test_noon_light(self):  self.assertFalse(at.is_dark(PARIS, self.at_utc(12)))
    def test_midnight_dark(self): self.assertTrue(at.is_dark(PARIS, self.at_utc(0)))
    def test_fixed_times(self):
        cfg = dict(PARIS, fixed_sunrise="07:00", fixed_sunset="19:00")
        self.assertTrue(at.is_dark(cfg, dt.datetime(2026, 1, 1, 6, 59)))
        self.assertFalse(at.is_dark(cfg, dt.datetime(2026, 1, 1, 7, 0)))
        self.assertTrue(at.is_dark(cfg, dt.datetime(2026, 1, 1, 19, 0)))

class Apply(unittest.TestCase):
    def run_apply(self, dark, current="'x'"):
        calls = []
        def fake(cmd, **kw):
            calls.append(cmd)
            return mock.Mock(returncode=0, stdout=current)
        with mock.patch.object(at.subprocess, "run", fake), mock.patch("builtins.print"):
            at.apply(dark, PARIS)
        return [c[2:] for c in calls if c[1] == "set"]
    def test_dark_sets_keys(self):
        sets = self.run_apply(True)
        self.assertIn(["org.x.apps.portal", "color-scheme", "prefer-dark"], sets)
        self.assertIn(["org.cinnamon.desktop.interface", "gtk-theme", "Mint-Y-Dark"], sets)
    def test_light_sets_default(self):
        self.assertIn(["org.gnome.desktop.interface", "color-scheme", "default"], self.run_apply(False))
    def test_no_write_when_already_set(self):
        sets = self.run_apply(True, current="'prefer-dark'")
        self.assertNotIn(["org.x.apps.portal", "color-scheme", "prefer-dark"], sets)

if __name__ == "__main__": unittest.main()
