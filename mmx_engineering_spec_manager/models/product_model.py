from mmx_engineering_spec_manager.models.prompt_model import PromptModel

class ProductModel:
    def __init__(self, data):
        self.name = data.get("Name")
        self.quantity = data.get("Quantity")
        self.width = data.get("Width")
        self.height = data.get("Height")
        self.depth = data.get("Depth")
        self.item_number = data.get("ItemNumber")
        self.comment = data.get("Comment")
        self.angle = data.get("Angle")
        self.x_origin = data.get("XOrigin")
        self.y_origin = data.get("YOrigin")
        self.z_origin = data.get("ZOrigin")
        self.link_id_specification_group = data.get("LinkIDSpecificationGroup")
        self.link_id_location = data.get("LinkIDLocation")
        self.link_id_wall = data.get("LinkIDWall")
        self.file_name = data.get("FileName")
        self.picture_name = data.get("PictureName")

        # Explicitly handle the 'Prompts' collection
        prompts_data = data.get("Prompts", [])
        self.prompts = [PromptModel(prompt_data) for prompt_data in prompts_data]