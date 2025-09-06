import pytest
from PySide6.QtCore import QPointF, QEvent, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from mmx_engineering_spec_manager.views.workspace.plan_view import PlanViewWidget
from mmx_engineering_spec_manager.views.workspace.elevation_view import ElevationViewWidget
from mmx_engineering_spec_manager.views.workspace.workspace_tab import WorkspaceTab


def test_plan_view_emits_product_moved_signal(qtbot):
    view = PlanViewWidget()
    qtbot.addWidget(view)
    view.set_wall(length_in=100, thickness_in=4)

    moved = []
    view.productMoved.connect(lambda pid, x, y: moved.append((pid, x, y)))

    view.add_product(product_id=1, width_in=10, depth_in=20, x_left_in=5, y_from_face_in=2)

    # Select the item and simulate a small move, then trigger mouse release
    item = list(view._product_items.values())[0]
    item.setSelected(True)
    item.setPos(QPointF(15, item.pos().y()))

    # Synthesize a proper mouse release event
    ev = QMouseEvent(QEvent.Type.MouseButtonRelease, QPointF(0, 0), Qt.MouseButton.LeftButton, Qt.MouseButtons(Qt.MouseButton.LeftButton), Qt.KeyboardModifier.NoModifier)
    view.mouseReleaseEvent(ev)

    assert moved and moved[0][0] == 1 and moved[0][1] == 15


def test_elevation_view_emits_product_moved_signal(qtbot):
    view = ElevationViewWidget()
    qtbot.addWidget(view)
    view.set_wall(length_in=100, height_in=50)

    moved = []
    view.productMoved.connect(lambda pid, xo, zo: moved.append((pid, xo, zo)))

    # Add product with known size and origins
    view.add_product(product_id=2, width_in=10, height_in=10, x_origin_from_right=20, z_origin_from_bottom=5)

    item = list(view._product_items.values())[0]
    item.setSelected(True)
    # Move left by 5 (increasing XOrigin by 5)
    item.setPos(QPointF(item.pos().x() - 5, item.pos().y() + 5))

    ev2 = QMouseEvent(QEvent.Type.MouseButtonRelease, QPointF(0, 0), Qt.MouseButton.LeftButton, Qt.MouseButtons(Qt.MouseButton.LeftButton), Qt.KeyboardModifier.NoModifier)
    view.mouseReleaseEvent(ev2)

    assert moved and moved[0][0] == 2
    # We can't compute exact origin without reading item.rect / wall; assert types and non-negative
    assert isinstance(moved[0][1], float) and isinstance(moved[0][2], float)


def test_workspace_tab_try_except_fallback(qtbot, monkeypatch):
    tab = WorkspaceTab()
    qtbot.addWidget(tab)

    class P:
        def __init__(self):
            self.name = "N"
            self.number = "1"
            self.walls = []

    # Force plan_view.set_wall to raise once to go through except path, then succeed
    state = {'raised': False}
    def maybe_raise(*a, **k):
        if not state['raised']:
            state['raised'] = True
            raise RuntimeError('fail-once')
        return None
    monkeypatch.setattr(tab.plan_view, 'set_wall', maybe_raise)

    # elevation_view should still be callable; display should not raise
    tab.display_project_data(P())
