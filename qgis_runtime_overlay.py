"""QGIS-runtime regression test for the private canvas overlay lifecycle."""

from __future__ import annotations

import os
import sys
from pathlib import Path


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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from yandex_panorama_navigator.plugin import (  # noqa: E402
    YandexPanoramaNavigatorPlugin,
)


class FakeCanvas:
    def __init__(self, layers):
        self._layers = list(layers)

    def layers(self):
        return list(self._layers)

    def setLayers(self, layers):
        self._layers = list(layers)


class FakeIface:
    def __init__(self, canvas):
        self._canvas = canvas

    def mapCanvas(self):
        return self._canvas


class FakeLayer:
    def __init__(self):
        self.deleted_later = False

    def deleteLater(self):
        self.deleted_later = True


base_bottom = object()
base_top = object()
overlay = FakeLayer()
canvas = FakeCanvas([base_top, base_bottom])
plugin = YandexPanoramaNavigatorPlugin(FakeIface(canvas))
plugin.coverage_layer = overlay
plugin.coverage_visible = True

plugin._put_coverage_above_canvas_layers()
assert canvas.layers() == [overlay, base_top, base_bottom]

canvas.setLayers([base_bottom, base_top])
plugin._canvas_layers_changed()
assert canvas.layers() == [overlay, base_bottom, base_top]

plugin.hide_coverage_layer()
assert canvas.layers() == [base_bottom, base_top]
assert plugin.coverage_layer is None
assert overlay.deleted_later

print("virtual_overlay_ok")
