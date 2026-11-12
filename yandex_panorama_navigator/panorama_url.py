"""Pure-Python helpers for Yandex Panorama URLs and view bearings."""

from __future__ import annotations

import math
from urllib.parse import urlencode


def _bounded(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


def initial_bearing(
    longitude_1: float,
    latitude_1: float,
    longitude_2: float,
    latitude_2: float,
) -> float:
    """Return the initial bearing in degrees clockwise from north."""
    lon_1 = math.radians(float(longitude_1))
    lat_1 = math.radians(float(latitude_1))
    lon_2 = math.radians(float(longitude_2))
    lat_2 = math.radians(float(latitude_2))

    delta_lon = lon_2 - lon_1
    y_value = math.sin(delta_lon) * math.cos(lat_2)
    x_value = math.cos(lat_1) * math.sin(lat_2) - math.sin(lat_1) * math.cos(
        lat_2
    ) * math.cos(delta_lon)
    if abs(x_value) < 1e-15 and abs(y_value) < 1e-15:
        return 0.0
    return (math.degrees(math.atan2(y_value, x_value)) + 360.0) % 360.0


def build_yandex_panorama_url(
    longitude: float,
    latitude: float,
    heading: float = 0.0,
    pitch: float = 0.0,
    horizontal_span: float = 90.0,
    vertical_span: float = 60.0,
    zoom: float = 17.0,
) -> str:
    """Build a public yandex.ru/maps URL that requests the nearest panorama."""
    longitude = _bounded(longitude, -180.0, 180.0)
    latitude = _bounded(latitude, -90.0, 90.0)
    heading = float(heading) % 360.0
    pitch = _bounded(pitch, -90.0, 90.0)
    horizontal_span = _bounded(horizontal_span, 10.0, 180.0)
    vertical_span = _bounded(vertical_span, 10.0, 120.0)
    zoom = _bounded(zoom, 0.0, 21.0)

    point = f"{longitude:.7f},{latitude:.7f}"
    parameters = [
        ("l", "stv,sta"),
        ("ll", point),
        ("panorama[point]", point),
        ("panorama[direction]", f"{heading:.6f},{pitch:.6f}"),
        ("panorama[span]", f"{horizontal_span:.6f},{vertical_span:.6f}"),
        ("z", f"{zoom:g}"),
    ]
    return "https://yandex.ru/maps/?" + urlencode(parameters)
