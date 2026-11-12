"""Integration test using a real off-screen QgsMapCanvas."""

from __future__ import annotations

import os
import sys
from pathlib import Path


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_dll_handles = []
qgis_prefix = os.environ.get("QGIS_PREFIX_PATH", "").replace("/", os.sep)
if qgis_prefix and hasattr(os, "add_dll_directory"):
    install_root = os.path.dirname(os.path.dirname(qgis_prefix))
    for dll_dir in (
        os.path.join(install_root, "bin"),
        os.path.join(install_root, "apps", "Qt5", "bin"),
        os.path.join(install_root, "apps", "Qt6", "bin"),
        os.path.join(qgis_prefix, "bin"),
    ):
        if os.path.isdir(dll_dir):
            _dll_handles.append(os.add_dll_directory(dll_dir))

from qgis.core import QgsApplication, QgsProject, QgsVectorLayer  # noqa: E402
from qgis.gui import QgsMapCanvas  # noqa: E402


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from yandex_panorama_navigator.plugin import (  # noqa: E402
    YandexPanoramaNavigatorPlugin,
)


class FakeIface:
    def __init__(self, canvas):
        self._canvas = canvas

    def mapCanvas(self):
        return self._canvas


app = QgsApplication([], True)
app.initQgis()
canvas = QgsMapCanvas()
project = QgsProject.instance()
base = QgsVectorLayer("Point?crs=EPSG:4326", "base", "memory")
overlay = QgsVectorLayer(
    "Point?crs=EPSG:4326", "private coverage", "memory"
)
project.addMapLayer(base)
canvas.setLayers([base])

plugin = YandexPanoramaNavigatorPlugin(FakeIface(canvas))
plugin.coverage_layer = overlay
plugin.coverage_visible = True
plugin._put_coverage_above_canvas_layers()

assert canvas.layers()[0] is overlay
assert canvas.layers()[1] is base
assert project.mapLayer(overlay.id()) is None

plugin.hide_coverage_layer()
assert canvas.layers() == [base]
assert project.mapLayer(overlay.id()) is None

print("real_canvas_private_overlay_ok")
project.removeMapLayer(base.id())
app.exitQgis()
