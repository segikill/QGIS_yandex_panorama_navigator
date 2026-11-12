"""Static release-contract checks that do not require a QGIS runtime."""

from __future__ import annotations

import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1] / "yandex_panorama_navigator"


class ReleaseContractTests(unittest.TestCase):
    def test_coverage_is_not_registered_in_qgis_project(self):
        source = (PLUGIN / "plugin.py").read_text(encoding="utf-8")
        self.assertNotIn("addMapLayer", source)
        self.assertNotIn("insertLayer", source)
        self.assertNotIn("layerTreeRoot", source)
        self.assertIn("self.canvas.setLayers(layers)", source)

    def test_webengine_is_absent_from_executable_python(self):
        source = "\n".join(
            path.read_text(encoding="utf-8", errors="strict")
            for path in PLUGIN.glob("*.py")
        ).lower()
        self.assertNotIn("webengine", source)
        self.assertNotIn("pyqt5", source)
        self.assertNotIn("pyqt6", source)

    def test_removed_webengine_files_are_absent(self):
        self.assertFalse((PLUGIN / "webengine_support.py").exists())
        self.assertFalse((PLUGIN / "panorama_dock.py").exists())
        self.assertFalse((PLUGIN / "INSTALL_WEBENGINE_RU.md").exists())


if __name__ == "__main__":
    unittest.main()
