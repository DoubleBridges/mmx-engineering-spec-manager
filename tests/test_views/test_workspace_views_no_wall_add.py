from mmx_engineering_spec_manager.views.workspace.plan_view import PlanViewWidget
from mmx_engineering_spec_manager.views.workspace.elevation_view import ElevationViewWidget


def test_plan_view_add_product_initializes_wall(qtbot):
    v = PlanViewWidget()
    qtbot.addWidget(v)
    # Don't call set_wall; add_product should initialize
    v.add_product(product_id=7, width_in=5, depth_in=5, x_left_in=1, y_from_face_in=1)
    assert v.wall_length() > 0


def test_elevation_view_add_product_initializes_wall(qtbot):
    v = ElevationViewWidget()
    qtbot.addWidget(v)
    v.add_product(product_id=8, width_in=5, height_in=5, x_origin_from_right=1, z_origin_from_bottom=1)
    assert v.wall_length() > 0 and v.wall_height() > 0
