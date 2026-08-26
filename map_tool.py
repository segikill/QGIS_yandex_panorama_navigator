"""One-shot QGIS map tool for selecting a panorama point and heading."""

from __future__ import annotations

from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QCursor
from qgis.core import QgsPointXY, QgsWkbTypes
from qgis.gui import QgsMapTool, QgsRubberBand, QgsVertexMarker


def _left_button():
    value = getattr(Qt, "LeftButton", None)
    return value if value is not None else Qt.MouseButton.LeftButton


def _escape_key():
    value = getattr(Qt, "Key_Escape", None)
    return value if value is not None else Qt.Key.Key_Escape


def _cross_cursor():
    value = getattr(Qt, "CrossCursor", None)
    return value if value is not None else Qt.CursorShape.CrossCursor


def _line_geometry_type():
    value = getattr(QgsWkbTypes, "LineGeometry", None)
    return (
        value if value is not None else QgsWkbTypes.GeometryType.LineGeometry
    )


class PanoramaMapTool(QgsMapTool):
    """Capture a point and an optional drag endpoint; emit both map points."""

    selectionCompleted = pyqtSignal(object, object, bool)
    selectionCanceled = pyqtSignal()

    def __init__(self, canvas):
        super().__init__(canvas)
        self.canvas = canvas
        self.start_point = None
        self.start_pixel = None
        self.dragging = False

        self.line = QgsRubberBand(canvas, _line_geometry_type())
        self.line.setColor(QColor(220, 40, 40, 220))
        self.line.setWidth(2)

        self.marker = QgsVertexMarker(canvas)
        self.marker.setColor(QColor(220, 40, 40))
        self.marker.setFillColor(QColor(255, 255, 255, 180))
        self.marker.setIconSize(12)
        self.marker.setPenWidth(2)
        self.marker.hide()

        self.setCursor(QCursor(_cross_cursor()))

    def canvasPressEvent(self, event):
        if event.button() != _left_button():
            return
        self.start_point = QgsPointXY(event.mapPoint())
        self.start_pixel = event.pos()
        self.dragging = True
        self.marker.setCenter(self.start_point)
        self.marker.show()
        self._update_line(self.start_point)

    def canvasMoveEvent(self, event):
        if not self.dragging or self.start_point is None:
            return
        self._update_line(QgsPointXY(event.mapPoint()))

    def canvasReleaseEvent(self, event):
        if event.button() != _left_button() or self.start_point is None:
            return

        end_point = QgsPointXY(event.mapPoint())
        end_pixel = event.pos()
        delta_x = end_pixel.x() - self.start_pixel.x()
        delta_y = end_pixel.y() - self.start_pixel.y()
        has_direction = (delta_x * delta_x + delta_y * delta_y) >= 25

        start_point = QgsPointXY(self.start_point)
        self.dragging = False
        self._clear_graphics()
        self.selectionCompleted.emit(start_point, end_point, has_direction)

    def keyPressEvent(self, event):
        if event.key() == _escape_key():
            self.cancel()
            event.accept()
            return
        super().keyPressEvent(event)

    def deactivate(self):
        self.dragging = False
        self._clear_graphics()
        super().deactivate()

    def cancel(self):
        self.dragging = False
        self._clear_graphics()
        self.selectionCanceled.emit()

    def cleanup(self):
        self._clear_graphics()
        scene = self.canvas.scene()
        if self.line is not None:
            scene.removeItem(self.line)
            self.line = None
        if self.marker is not None:
            scene.removeItem(self.marker)
            self.marker = None

    def _update_line(self, end_point):
        self.line.reset(_line_geometry_type())
        self.line.addPoint(self.start_point, False)
        self.line.addPoint(end_point, True)

    def _clear_graphics(self):
        if self.line is not None:
            self.line.reset(_line_geometry_type())
        if self.marker is not None:
            self.marker.hide()
