class WallModel:
    def __init__(self, data):
        self.link_id = data.get("LinkID")
        self.link_id_location = data.get("LinkIDLocation")
        self.width = data.get("Width")
        self.height = data.get("Height")
        self.depth = data.get("Depth")
        self.x_origin = data.get("XOrigin")
        self.y_origin = data.get("YOrigin")
        self.z_origin = data.get("ZOrigin")
        self.angle = data.get("Angle")