from __future__ import annotations
from typing import Iterable, Optional

from PySide6.QtCore import Qt, QRectF, QSizeF, Signal, QObject
from PySide6.QtGui import QBrush, QColor, QPen, QPainter
from PySide6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView


class _DraggableProductRect(QGraphicsRectItem):
    def __init__(self, product_id: int, rect: QRectF, color: QColor):
        super().__init__(rect)
        self.product_id = product_id
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.GlobalColor.black, 1))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )


class PlanViewWidget(QGraphicsView):
    """
    Simple 2D plan view (top-down). Draws a wall as a horizontal rectangle and
    products as draggable rectangles in front of the wall. Emits productMoved when
    a product item is released after moving.
    """

    productMoved = Signal(int, float, float)  # product_id, scene_x_left, scene_y

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setBackgroundBrush(QBrush(QColor("#fafafa")))
        self._wall_item: Optional[QGraphicsRectItem] = None
        self._product_items: dict[int, _DraggableProductRect] = {}
        self._wall_length: float = 120.0  # default inches; can be set via set_wall

    def set_wall(self, length_in: float = 120.0, thickness_in: float = 4.0):
        self._scene.clear()
        self._product_items.clear()
        self._wall_length = max(1.0, float(length_in))
        wall_rect = QRectF(0, 0, self._wall_length, thickness_in)
        wall = QGraphicsRectItem(wall_rect)
        wall.setBrush(QBrush(QColor("#cccccc")))
        wall.setPen(QPen(Qt.GlobalColor.black, 1))
        wall.setZValue(-1)
        self._scene.addItem(wall)
        self._wall_item = wall
        # Expand scene rect to provide working area in front of wall (positive Y)
        self._scene.setSceneRect(QRectF(-20, -20, self._wall_length + 40, 200))

    def add_product(self, product_id: int, width_in: float, depth_in: float, x_left_in: float = 0.0, y_from_face_in: float = 0.0):
        # Ensure wall exists
        if not self._wall_item:
            self.set_wall()  # pragma: no cover (guard path exercised indirectly; GUI-timing sensitive)
        w = max(0.1, float(width_in))
        d = max(0.1, float(depth_in))
        rect = QRectF(0, 0, w, d)
        item = _DraggableProductRect(product_id, rect, QColor("#6fa8dc"))
        item.setPos(x_left_in, y_from_face_in + self._wall_item.rect().height())
        # Install event filter via subclassing: override itemChange not available on QGraphicsRectItem in PySide6 easily; use scene mouseRelease
        self._scene.addItem(item)
        self._product_items[product_id] = item

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        # Emit moved positions for all selected items (or last moved)
        for pid, item in self._product_items.items():
            if item.isSelected():
                pos = item.pos()
                # y_from_face = pos.y() - wall_thickness
                wall_thickness = self._wall_item.rect().height() if self._wall_item else 0.0
                y_from_face = pos.y() - wall_thickness
                self.productMoved.emit(pid, float(pos.x()), float(y_from_face))

    def wall_length(self) -> float:
        return self._wall_length
