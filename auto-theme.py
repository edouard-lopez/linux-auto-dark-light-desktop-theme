#!/usr/bin/env python3
"""Switch Cinnamon/GNOME light/dark at sunrise/sunset. Config: ~/.config/auto-theme.conf"""
import math, datetime as dt, subprocess, configparser, os, sys

CONF = os.path.expanduser("~/.config/auto-theme.conf")
DEFAULT = {"latitude": "48.85", "longitude": "2.35", "fixed_sunrise": "", "fixed_sunset": "",
           "light_gtk": "Mint-Y", "dark_gtk": "Mint-Y-Dark",
           "light_cinnamon": "", "dark_cinnamon": ""}

def load():
    c = configparser.ConfigParser(); c["theme"] = DEFAULT; c.read(CONF); return c["theme"]

def sun_times(lat, lon, day):
    """NOAA approximation. Returns (sunrise, sunset) as local aware datetimes, or None at polar day/night."""
    n = day.timetuple().tm_yday
    g = 2 * math.pi / 365 * (n - 1)
    eq = 229.18 * (0.000075 + 0.001868*math.cos(g) - 0.032077*math.sin(g)
                   - 0.014615*math.cos(2*g) - 0.040849*math.sin(2*g))
    decl = (0.006918 - 0.399912*math.cos(g) + 0.070257*math.sin(g) - 0.006758*math.cos(2*g)
            + 0.000907*math.sin(2*g) - 0.002697*math.cos(3*g) + 0.00148*math.sin(3*g))
    la = math.radians(lat)
    cosha = math.cos(math.radians(90.833)) / (math.cos(la)*math.cos(decl)) - math.tan(la)*math.tan(decl)
    if abs(cosha) > 1: return None
    ha = math.degrees(math.acos(cosha))
    base = dt.datetime(day.year, day.month, day.day, tzinfo=dt.timezone.utc)
    rise = base + dt.timedelta(minutes=720 - 4*(lon + ha) - eq)
    sset = base + dt.timedelta(minutes=720 - 4*(lon - ha) - eq)
    return rise.astimezone(), sset.astimezone()

def is_dark(cfg, now):
    if cfg["fixed_sunrise"] and cfg["fixed_sunset"]:
        r = dt.time.fromisoformat(cfg["fixed_sunrise"]); s = dt.time.fromisoformat(cfg["fixed_sunset"])
        t = now.time(); return not (r <= t < s)
    st = sun_times(float(cfg["latitude"]), float(cfg["longitude"]), now.date())
    if st is None: return now.month in (11, 12, 1) if float(cfg["latitude"]) > 0 else now.month in (5, 6, 7)
    return not (st[0] <= now < st[1])

def gset(schema, key, val):
    if subprocess.run(["gsettings", "writable", schema, key], capture_output=True).returncode != 0: return
    cur = subprocess.run(["gsettings", "get", schema, key], capture_output=True, text=True).stdout.strip()
    if cur != f"'{val}'":
        subprocess.run(["gsettings", "set", schema, key, val]); print(f"{schema} {key} -> {val}")

def apply(dark, cfg):
    mode = "dark" if dark else "light"
    gset("org.x.apps.portal", "color-scheme", "prefer-dark" if dark else "prefer-light")
    gset("org.gnome.desktop.interface", "color-scheme", "prefer-dark" if dark else "default")
    gtk = cfg[f"{mode}_gtk"]
    if gtk:
        gset("org.cinnamon.desktop.interface", "gtk-theme", gtk)
        gset("org.gnome.desktop.interface", "gtk-theme", gtk)
    cin = cfg[f"{mode}_cinnamon"]
    if cin: gset("org.cinnamon.theme", "name", cin)

if __name__ == "__main__":
    cfg = load(); now = dt.datetime.now().astimezone()
    arg = sys.argv[1] if len(sys.argv) > 1 else "auto"
    if arg == "status":
        st = sun_times(float(cfg["latitude"]), float(cfg["longitude"]), now.date())
        print("sunrise/sunset:", st and [t.strftime("%H:%M") for t in st], "| dark now:", is_dark(cfg, now)); sys.exit()
    apply(is_dark(cfg, now) if arg == "auto" else arg == "dark", cfg)
