"""Dependency-free regression tests for URL and coverage helpers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse


PLUGIN = Path(__file__).resolve().parents[1] / "yandex_panorama_navigator"
sys.path.insert(0, str(PLUGIN))

from coverage_layer import (  # noqa: E402
    FALLBACK_VERSION,
    build_coverage_gdal_wms,
    extract_coverage_version,
)
from panorama_url import (  # noqa: E402
    build_yandex_panorama_url,
    initial_bearing,
)


class HelperTests(unittest.TestCase):
    def test_url_contains_panorama_parameters(self):
        url = build_yandex_panorama_url(37.6176, 55.7558, heading=90)
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        self.assertEqual(parsed.scheme, "https")
        self.assertEqual(parsed.netloc, "yandex.ru")
        self.assertEqual(query["panorama[point]"][0], "37.6176000,55.7558000")
        self.assertEqual(query["panorama[direction]"][0], "90.000000,0.000000")

    def test_cardinal_bearings(self):
        self.assertAlmostEqual(initial_bearing(0, 0, 0, 1), 0.0, places=6)
        self.assertAlmostEqual(initial_bearing(0, 0, 1, 0), 90.0, places=6)

    def test_renderer_version_and_projection(self):
        payload = f"prefix {FALLBACK_VERSION} suffix".encode("ascii")
        self.assertEqual(extract_coverage_version(payload), FALLBACK_VERSION)
        xml = build_coverage_gdal_wms(FALLBACK_VERSION)
        self.assertIn("<Projection>EPSG:3395</Projection>", xml)
        self.assertIn("&amp;x=${x}", xml)


if __name__ == "__main__":
    unittest.main()
