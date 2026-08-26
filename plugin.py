"""Main plugin controller."""

from __future__ import annotations

import os

from qgis.PyQt.QtCore import QByteArray, QDateTime, QSettings, QUrl
from qgis.PyQt.QtGui import QDesktopServices, QIcon
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.PyQt.QtWidgets import QAction, QApplication, QMessageBox
from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsCsException,
    QgsNetworkAccessManager,
    QgsProject,
    QgsRasterLayer,
)

from .coverage_layer import (
    COVERAGE_LAYER_NAME,
    COVERAGE_VERSION_PROPERTY,
    FALLBACK_VERSION,
    build_coverage_gdal_wms,
    extract_coverage_version,
    is_valid_coverage_version,
)
from .map_tool import PanoramaMapTool
from .panorama_url import build_yandex_panorama_url, initial_bearing


def _qgis_level(name: str):
    value = getattr(Qgis, name, None)
    return value if value is not None else getattr(Qgis.MessageLevel, name)


class YandexPanoramaNavigatorPlugin:
    """QGIS GUI integration for opening panoramas in the system browser."""

    MENU_NAME = "&Яндекс Панорамы"
    SETTINGS_PREFIX = "yandex_panorama_navigator"

    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.toolbar = None
        self.map_tool = None
        self.previous_map_tool = None
        self.coverage_action = None
        self.coverage_layer = None
        self.coverage_visible = False
        self.syncing_canvas_layers = False
        self.coverage_reply = None
        self.coverage_buffer = bytearray()
        self.coverage_version_candidate = None

    def initGui(self):
        icon_path = os.path.join(
            self.plugin_dir, "icons", "yandex_panorama.svg"
        )
        icon = QIcon(icon_path)

        self.toolbar = self.iface.addToolBar("Яндекс Панорамы")
        self.toolbar.setObjectName("YandexPanoramaNavigatorToolbar")

        external_action = QAction(
            icon,
            "Показать покрытие и открыть панораму",
            self.iface.mainWindow(),
        )
        external_action.setToolTip(
            "Показать синее покрытие панорам, затем выбрать точку "
            "и направление"
        )
        external_action.triggered.connect(self._main_action_triggered)
        self._register_action(external_action, toolbar=True)

        self.coverage_action = QAction(
            "Показывать временное покрытие панорам",
            self.iface.mainWindow(),
        )
        self.coverage_action.setCheckable(True)
        self.coverage_action.triggered.connect(self._coverage_toggled)
        self._register_action(self.coverage_action, toolbar=False)

        refresh_action = QAction(
            "Обновить покрытие панорам",
            self.iface.mainWindow(),
        )
        refresh_action.triggered.connect(
            lambda: self.refresh_coverage_version(force=True)
        )
        self._register_action(refresh_action, toolbar=False)

        if hasattr(self.canvas, "layersChanged"):
            self.canvas.layersChanged.connect(self._canvas_layers_changed)

    def unload(self):
        if self.coverage_reply is not None:
            self.coverage_reply.abort()
            self.coverage_reply.deleteLater()
            self.coverage_reply = None

        if self.map_tool is not None:
            if self.canvas.mapTool() is self.map_tool:
                self.canvas.unsetMapTool(self.map_tool)
            self.map_tool.cleanup()
            self.map_tool = None

        self.hide_coverage_layer()

        if hasattr(self.canvas, "layersChanged"):
            try:
                self.canvas.layersChanged.disconnect(
                    self._canvas_layers_changed
                )
            except (TypeError, RuntimeError):
                pass

        for action in self.actions:
            self.iface.removePluginWebMenu(self.MENU_NAME, action)
            if self.toolbar is not None:
                self.toolbar.removeAction(action)
            action.deleteLater()
        self.actions.clear()

        if self.toolbar is not None:
            self.toolbar.deleteLater()
            self.toolbar = None

    def _main_action_triggered(self):
        self.show_coverage_layer()
        self.activate_map_tool()

    def _coverage_toggled(self, checked: bool):
        if checked:
            self.show_coverage_layer()
        else:
            self.hide_coverage_layer()

    def show_coverage_layer(self):
        """Render private coverage without adding it to the project."""
        layer = self.coverage_layer
        if layer is None:
            settings = QSettings()
            version = settings.value(
                f"{self.SETTINGS_PREFIX}/coverage_version",
                FALLBACK_VERSION,
                type=str,
            )
            if not is_valid_coverage_version(version):
                version = FALLBACK_VERSION

            layer = QgsRasterLayer(
                build_coverage_gdal_wms(version),
                COVERAGE_LAYER_NAME,
                "gdal",
            )
            if not layer.isValid():
                self.iface.messageBar().pushMessage(
                    "Яндекс Панорамы",
                    "Не удалось создать виртуальное покрытие через GDAL.",
                    level=_qgis_level("Critical"),
                    duration=8,
                )
                if self.coverage_action is not None:
                    self.coverage_action.setChecked(False)
                return None

            layer.setCustomProperty(COVERAGE_VERSION_PROPERTY, version)
            self.coverage_layer = layer

        self.coverage_visible = True
        self._put_coverage_above_canvas_layers()
        if self.coverage_action is not None:
            self.coverage_action.setChecked(True)
        layer.triggerRepaint()
        self.refresh_coverage_version(force=False)
        return layer

    def hide_coverage_layer(self):
        """Remove the private overlay and release its raster layer."""
        layer = self.coverage_layer
        self.coverage_visible = False
        if layer is not None:
            remaining_layers = [
                canvas_layer
                for canvas_layer in self.canvas.layers()
                if canvas_layer is not layer
            ]
            self._set_canvas_layers(remaining_layers)
            self.coverage_layer = None
            layer.deleteLater()
        if self.coverage_action is not None:
            self.coverage_action.setChecked(False)

    def _put_coverage_above_canvas_layers(self):
        layer = self.coverage_layer
        if layer is None or not self.coverage_visible:
            return
        remaining_layers = [
            canvas_layer
            for canvas_layer in self.canvas.layers()
            if canvas_layer is not layer
        ]
        self._set_canvas_layers([layer] + remaining_layers)

    def _set_canvas_layers(self, layers):
        if self.syncing_canvas_layers:
            return
        self.syncing_canvas_layers = True
        try:
            self.canvas.setLayers(layers)
        finally:
            self.syncing_canvas_layers = False

    def _canvas_layers_changed(self):
        """Keep private coverage first after layer-tree visibility changes."""
        if self.syncing_canvas_layers or not self.coverage_visible:
            return
        layer = self.coverage_layer
        canvas_layers = self.canvas.layers()
        if layer is not None and (
            not canvas_layers or canvas_layers[0] is not layer
        ):
            self._put_coverage_above_canvas_layers()

    def refresh_coverage_version(self, force: bool = False):
        """Discover the current renderer version from Yandex Maps."""
        if self.coverage_reply is not None:
            return

        settings = QSettings()
        now = QDateTime.currentSecsSinceEpoch()
        last_check = int(
            settings.value(f"{self.SETTINGS_PREFIX}/coverage_last_check", 0)
        )
        if not force and now - last_check < 24 * 60 * 60:
            return

        settings.setValue(f"{self.SETTINGS_PREFIX}/coverage_last_check", now)
        request = QNetworkRequest(
            QUrl(
                "https://yandex.ru/maps/213/moscow/"
                "?l=stv%2Csta&ll=37.6176%2C55.7558&z=15"
            )
        )
        request.setRawHeader(
            QByteArray(b"User-Agent"),
            QByteArray(b"Mozilla/5.0 QGIS YandexPanoramaNavigator/1.1"),
        )
        self.coverage_buffer = bytearray()
        self.coverage_version_candidate = None
        self.coverage_reply = QgsNetworkAccessManager.instance().get(request)
        self.coverage_reply.readyRead.connect(self._coverage_reply_ready)
        self.coverage_reply.finished.connect(self._coverage_reply_finished)

    def _coverage_reply_ready(self):
        reply = self.coverage_reply
        if reply is None:
            return
        self.coverage_buffer.extend(bytes(reply.readAll()))
        version = extract_coverage_version(bytes(self.coverage_buffer))
        if version:
            self.coverage_version_candidate = version
            reply.abort()
        elif len(self.coverage_buffer) > 1_500_000:
            reply.abort()

    def _coverage_reply_finished(self):
        reply = self.coverage_reply
        if reply is None:
            return

        self.coverage_buffer.extend(bytes(reply.readAll()))
        version = self.coverage_version_candidate or extract_coverage_version(
            bytes(self.coverage_buffer)
        )
        self.coverage_reply = None
        reply.deleteLater()
        self.coverage_buffer = bytearray()
        self.coverage_version_candidate = None

        if version:
            self._apply_coverage_version(version)

    def _apply_coverage_version(self, version: str):
        settings = QSettings()
        settings.setValue(f"{self.SETTINGS_PREFIX}/coverage_version", version)
        layer = self.coverage_layer
        if layer is None:
            return
        current = str(layer.customProperty(COVERAGE_VERSION_PROPERTY, ""))
        if current == version:
            return

        layer.setDataSource(
            build_coverage_gdal_wms(version),
            COVERAGE_LAYER_NAME,
            "gdal",
        )
        layer.setCustomProperty(COVERAGE_VERSION_PROPERTY, version)
        self._put_coverage_above_canvas_layers()
        layer.triggerRepaint()
        self.iface.messageBar().pushMessage(
            "Яндекс Панорамы",
            "Покрытие панорам обновлено.",
            level=_qgis_level("Success"),
            duration=3,
        )

    def _register_action(self, action, toolbar: bool):
        self.iface.addPluginToWebMenu(self.MENU_NAME, action)
        if toolbar:
            self.toolbar.addAction(action)
        self.actions.append(action)

    def activate_map_tool(self):
        self.previous_map_tool = self.canvas.mapTool()

        if self.map_tool is not None:
            self.map_tool.cleanup()

        self.map_tool = PanoramaMapTool(self.canvas)
        self.map_tool.selectionCompleted.connect(self._selection_completed)
        self.map_tool.selectionCanceled.connect(self._selection_canceled)
        self.canvas.setMapTool(self.map_tool)
        self.iface.messageBar().pushMessage(
            "Яндекс Панорамы",
            "Кликните для направления на север или протяните мышью "
            "направление взгляда. Esc — отмена.",
            level=_qgis_level("Info"),
            duration=7,
        )

    def _selection_completed(
        self, start_point, end_point, has_direction: bool
    ):
        try:
            start_wgs84 = self._to_wgs84(start_point)
            end_wgs84 = self._to_wgs84(end_point)
        except QgsCsException as error:
            self.iface.messageBar().pushMessage(
                "Яндекс Панорамы",
                f"Не удалось преобразовать координаты: {error}",
                level=_qgis_level("Critical"),
                duration=8,
            )
            self._restore_previous_tool()
            return

        heading = 0.0
        if has_direction:
            heading = initial_bearing(
                start_wgs84.x(),
                start_wgs84.y(),
                end_wgs84.x(),
                end_wgs84.y(),
            )

        settings = QSettings()
        horizontal_span = float(
            settings.value(f"{self.SETTINGS_PREFIX}/horizontal_span", 90.0)
        )
        vertical_span = float(
            settings.value(f"{self.SETTINGS_PREFIX}/vertical_span", 60.0)
        )
        url = build_yandex_panorama_url(
            start_wgs84.x(),
            start_wgs84.y(),
            heading=heading,
            horizontal_span=horizontal_span,
            vertical_span=vertical_span,
        )

        opened = self._open_external(url)
        if opened:
            self.hide_coverage_layer()
        self._restore_previous_tool()

    def _selection_canceled(self):
        self.hide_coverage_layer()
        self._restore_previous_tool()
        self.iface.messageBar().pushMessage(
            "Яндекс Панорамы",
            "Выбор отменён",
            level=_qgis_level("Info"),
            duration=3,
        )

    def _to_wgs84(self, point):
        source_crs = self.canvas.mapSettings().destinationCrs()
        target_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        transform = QgsCoordinateTransform(
            source_crs, target_crs, QgsProject.instance()
        )
        return transform.transform(point)

    def _restore_previous_tool(self):
        current_tool = self.map_tool
        if (
            self.previous_map_tool is not None
            and self.previous_map_tool is not current_tool
        ):
            self.canvas.setMapTool(self.previous_map_tool)
        elif (
            current_tool is not None and self.canvas.mapTool() is current_tool
        ):
            self.canvas.unsetMapTool(current_tool)

        if current_tool is not None:
            current_tool.cleanup()
        self.map_tool = None
        self.previous_map_tool = None

    def _open_external(self, url: str):
        opened = QDesktopServices.openUrl(QUrl(url))
        if not opened:
            QApplication.clipboard().setText(url)
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Яндекс Панорамы",
                "Не удалось открыть браузер. Ссылка скопирована "
                "в буфер обмена.",
            )
        return opened
