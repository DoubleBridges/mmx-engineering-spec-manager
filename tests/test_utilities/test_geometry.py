from mmx_engineering_spec_manager.utilities.geometry import (
    x_left_to_xorigin_from_right,
    xorigin_from_right_to_x_left,
    y_top_to_zorigin_from_bottom,
)


def test_x_left_and_xorigin_conversions_round_trip():
    wall_len = 120.0
    prod_w = 30.0
    x_left = 60.0
    x_origin = x_left_to_xorigin_from_right(wall_len, prod_w, x_left)
    assert x_origin == wall_len - (x_left + prod_w)
    # Inverse
    x_left_rt = xorigin_from_right_to_x_left(wall_len, prod_w, x_origin)
    assert x_left_rt == x_left


def test_y_top_to_zorigin_from_bottom():
    wall_h = 96.0
    prod_h = 34.0
    y_top = 50.0
    z_origin = y_top_to_zorigin_from_bottom(wall_h, prod_h, y_top)
    assert z_origin == wall_h - (y_top + prod_h)
