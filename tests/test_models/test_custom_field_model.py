from mmx_engineering_spec_manager.models.custom_field_model import CustomFieldModel


def test_custom_field_model_initialization():
    data = {"Name": "Door_Type", "Value": "MV Profile Door"}
    model = CustomFieldModel(data)
    assert model.name == "Door_Type"
    assert model.value == "MV Profile Door"
