#!/usr/bin/env python3
"""Switch Cinnamon/GNOME light/dark at sunrise/sunset. Config: ~/.config/auto-theme.conf"""

import configparser
import datetime as dt
import math
import os
import subprocess
import sys


CONF = os.path.expanduser("~/.config/auto-theme.conf")
DEFAULT = {
    "latitude": "48.85",
    "longitude": "2.35",
    "fixed_sunrise": "",
    "fixed_sunset": "",
    "light_gtk": "Mint-Y",
    "dark_gtk": "Mint-Y-Dark",
    "light_cinnamon": "",
    "dark_cinnamon": "",
}


def load():
    config = configparser.ConfigParser()
    config["theme"] = DEFAULT
    config.read(CONF)
    return config["theme"]


def sun_times(lat, lon, day):
    """Return local aware sunrise/sunset times, or None during polar day/night."""
    day_of_year = day.timetuple().tm_yday
    angle = 2 * math.pi / 365 * (day_of_year - 1)
    equation_of_time = 229.18 * (
        0.000075
        + 0.001868 * math.cos(angle)
        - 0.032077 * math.sin(angle)
        - 0.014615 * math.cos(2 * angle)
        - 0.040849 * math.sin(2 * angle)
    )
    solar_declination = (
        0.006918
        - 0.399912 * math.cos(angle)
        + 0.070257 * math.sin(angle)
        - 0.006758 * math.cos(2 * angle)
        + 0.000907 * math.sin(2 * angle)
        - 0.002697 * math.cos(3 * angle)
        + 0.00148 * math.sin(3 * angle)
    )
    latitude = math.radians(lat)
    hour_angle_cosine = (
        math.cos(math.radians(90.833))
        / (math.cos(latitude) * math.cos(solar_declination))
        - math.tan(latitude) * math.tan(solar_declination)
    )
    if abs(hour_angle_cosine) > 1:
        return None

    hour_angle = math.degrees(math.acos(hour_angle_cosine))
    utc_midnight = dt.datetime(
        day.year, day.month, day.day, tzinfo=dt.timezone.utc
    )
    sunrise = utc_midnight + dt.timedelta(
        minutes=720 - 4 * (lon + hour_angle) - equation_of_time
    )
    sunset = utc_midnight + dt.timedelta(
        minutes=720 - 4 * (lon - hour_angle) - equation_of_time
    )
    return sunrise.astimezone(), sunset.astimezone()


def is_dark(cfg, now):
    if cfg["fixed_sunrise"] and cfg["fixed_sunset"]:
        sunrise = dt.time.fromisoformat(cfg["fixed_sunrise"])
        sunset = dt.time.fromisoformat(cfg["fixed_sunset"])
        current_time = now.time()
        return not (sunrise <= current_time < sunset)

    latitude = float(cfg["latitude"])
    times = sun_times(latitude, float(cfg["longitude"]), now.date())
    if times is None:
        polar_winter_months = (11, 12, 1) if latitude > 0 else (5, 6, 7)
        return now.month in polar_winter_months

    sunrise, sunset = times
    return not (sunrise <= now < sunset)


def gset(schema, key, value):
    writable = subprocess.run(
        ["gsettings", "writable", schema, key],
        capture_output=True,
    )
    if writable.returncode != 0:
        return

    current = subprocess.run(
        ["gsettings", "get", schema, key],
        capture_output=True,
        text=True,
    ).stdout.strip()
    if current != f"'{value}'":
        subprocess.run(["gsettings", "set", schema, key, value])
        print(f"{schema} {key} -> {value}")


def apply(dark, cfg):
    mode = "dark" if dark else "light"
    color_scheme = "prefer-dark" if dark else "prefer-light"
    gset("org.x.apps.portal", "color-scheme", color_scheme)
    gset(
        "org.gnome.desktop.interface",
        "color-scheme",
        "prefer-dark" if dark else "default",
    )

    gtk_theme = cfg[f"{mode}_gtk"]
    if gtk_theme:
        gset("org.cinnamon.desktop.interface", "gtk-theme", gtk_theme)
        gset("org.gnome.desktop.interface", "gtk-theme", gtk_theme)

    cinnamon_theme = cfg[f"{mode}_cinnamon"]
    if cinnamon_theme:
        gset("org.cinnamon.theme", "name", cinnamon_theme)


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    config = load()
    now = dt.datetime.now().astimezone()
    command = args[0] if args else "auto"
    if command == "status":
        times = sun_times(
            float(config["latitude"]),
            float(config["longitude"]),
            now.date(),
        )
        formatted_times = times and [time.strftime("%H:%M") for time in times]
        print("sunrise/sunset:", formatted_times, "| dark now:", is_dark(config, now))
        return

    dark = is_dark(config, now) if command == "auto" else command == "dark"
    apply(dark, config)


if __name__ == "__main__":
    main()
