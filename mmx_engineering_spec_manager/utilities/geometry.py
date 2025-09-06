from __future__ import annotations

def x_left_to_xorigin_from_right(wall_length: float, product_width: float, x_left_from_left: float) -> float:
    """
    Convert a scene X position (product's left edge from the wall's left end) to Microvellum XOrigin,
    which is measured from the right side of the wall to the product's rightmost x.

    XOrigin = wall_length - (x_left + product_width)
    """
    return float(wall_length) - (float(x_left_from_left) + float(product_width))


def xorigin_from_right_to_x_left(wall_length: float, product_width: float, x_origin_from_right: float) -> float:
    """
    Inverse of x_left_to_xorigin_from_right: given MV XOrigin, compute the scene left x.

    x_left = wall_length - XOrigin - product_width
    """
    return float(wall_length) - float(x_origin_from_right) - float(product_width)


def y_top_to_zorigin_from_bottom(wall_height: float, product_height: float, y_top_from_top: float) -> float:
    """
    Convert a scene Y position (product top from top) to Microvellum ZOrigin (distance from bottom to product bottom).

    ZOrigin = wall_height - (y_top + product_height)
    """
    return float(wall_height) - (float(y_top_from_top) + float(product_height))
