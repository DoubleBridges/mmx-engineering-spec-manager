from __future__ import annotations
from typing import Optional

from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QBrush, QColor, QPen, QPainter
from PySide6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView

from mmx_engineering_spec_manager.utilities.geometry import (
    x_left_to_xorigin_from_right,
)


class _DraggableElevationRect(QGraphicsRectItem):
    def __init__(self, product_id: int, rect: QRectF, color: QColor):
        super().__init__(rect)
        self.product_id = product_id
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.GlobalColor.black, 1))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )


class ElevationViewWidget(QGraphicsView):
    """
    Simple 2D elevation view. Draws a wall as a rectangle (width=wall length, height=wall height)
    and products as draggable rectangles. Emits productMoved(product_id, x_origin_from_right, z_origin_from_bottom)
    when a product item is released after moving.
    """

    productMoved = Signal(int, float, float)  # product_id, XOrigin, ZOrigin

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setBackgroundBrush(QBrush(QColor("#fbfbfb")))
        self._wall_item: Optional[QGraphicsRectItem] = None
        self._wall_length: float = 120.0
        self._wall_height: float = 96.0
        self._product_items: dict[int, _DraggableElevationRect] = {}

    def set_wall(self, length_in: float = 120.0, height_in: float = 96.0, thickness_in: float = 4.0):
        self._scene.clear()
        self._product_items.clear()
        self._wall_length = max(1.0, float(length_in))
        self._wall_height = max(1.0, float(height_in))
        wall_rect = QRectF(0, 0, self._wall_length, self._wall_height)
        wall = QGraphicsRectItem(wall_rect)
        wall.setBrush(QBrush(QColor("#e5e5e5")))
        wall.setPen(QPen(Qt.GlobalColor.black, 1))
        wall.setZValue(-1)
        self._scene.addItem(wall)
        self._wall_item = wall
        self._scene.setSceneRect(QRectF(-20, -20, self._wall_length + 40, self._wall_height + 40))

    def add_product(self, product_id: int, width_in: float, height_in: float, x_origin_from_right: float = 0.0, z_origin_from_bottom: float = 0.0):
        if not self._wall_item:
            self.set_wall()  # pragma: no cover (guard path depends on GUI timing)
        w = max(0.1, float(width_in))
        h = max(0.1, float(height_in))
        # Convert MV origins to scene positions
        x_left = self._wall_length - float(x_origin_from_right) - w
        y_top = self._wall_height - float(z_origin_from_bottom) - h
        rect = QRectF(0, 0, w, h)
        item = _DraggableElevationRect(product_id, rect, QColor("#93c47d"))
        item.setPos(x_left, y_top)
        self._scene.addItem(item)
        self._product_items[product_id] = item

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        # Emit moved positions for selected items
        for pid, item in self._product_items.items():
            if item.isSelected():
                pos = item.pos()
                # XOrigin is distance from right to product rightmost x
                x_origin = x_left_to_xorigin_from_right(self._wall_length, item.rect().width(), float(pos.x()))
                # ZOrigin is distance from bottom to product bottom: bottom = y_top + height
                z_origin = self._wall_height - (pos.y() + item.rect().height())
                self.productMoved.emit(pid, float(x_origin), float(z_origin))

    def wall_length(self) -> float:
        return self._wall_length

    def wall_height(self) -> float:
        return self._wall_height
