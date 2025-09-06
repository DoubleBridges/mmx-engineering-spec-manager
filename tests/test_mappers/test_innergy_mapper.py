from mmx_engineering_spec_manager.mappers.innergy_mapper import (
    map_custom_fields_to_dtos,
    map_products_payload_to_dtos,
    map_project_payload_to_dto,
)


def test_map_custom_fields_handles_none_and_list():
    assert map_custom_fields_to_dtos(None) == []
    dtos = map_custom_fields_to_dtos([
        {"Name": "CF1", "Value": "V1"},
        {"name": "cf2", "value": "v2"},
    ])
    assert len(dtos) == 2
    assert dtos[0].name == "CF1" and dtos[0].value == "V1"
    assert dtos[1].name.lower() == "cf2" and dtos[1].value == "v2"


def test_map_products_payload_supports_dict_items_and_list_and_invalid():
    # Dict with Items key
    payload_dict = {
        "Items": [
            {"Name": "Cabinet", "QuantCount": 2, "Description": "Desc", "CustomFields": [{"Name": "CF1", "Value": "V1"}]}
        ]
    }
    products = map_products_payload_to_dtos(payload_dict)
    assert len(products) == 1
    assert products[0].name == "Cabinet"
    assert products[0].quantity == 2
    assert products[0].custom_fields and products[0].custom_fields[0].name == "CF1"

    # List shape
    payload_list = [
        {"name": "Drawer", "quantity": 5, "description": "D", "custom_fields": [{"name": "cf2", "value": "v2"}]}
    ]
    products2 = map_products_payload_to_dtos(payload_list)
    assert len(products2) == 1
    assert products2[0].name == "Drawer"
    assert products2[0].quantity == 5
    assert products2[0].custom_fields and products2[0].custom_fields[0].name == "cf2"

    # Invalid type (e.g., None) should yield empty list (else branch)
    assert map_products_payload_to_dtos(None) == []


def test_map_project_payload_to_dto_handles_address_and_locations_and_products():
    project_payload = {
        "Number": "P-321",
        "Name": "Proj 321",
        "JobDescription": "JD",
        "Address": {"Address1": "123 Main"},
        "locations": [{"name": "Kitchen"}, {"Name": "Bath"}],
        "CustomFields": [{"Name": "P_CF", "Value": "pv"}],
    }
    products_payload = {
        "Items": [
            {"Name": "Cabinet", "QuantCount": 1, "Description": "Desc"}
        ]
    }
    dto = map_project_payload_to_dto(project_payload, products_payload)
    assert dto.number == "P-321"
    assert dto.name == "Proj 321"
    assert dto.job_description == "JD"
    assert dto.job_address == "123 Main"
    assert [l.name for l in dto.locations] == ["Kitchen", "Bath"]
    assert dto.products and dto.products[0].name == "Cabinet"
    assert dto.custom_fields and dto.custom_fields[0].name == "P_CF"

    # Address as plain string fallback
    dto2 = map_project_payload_to_dto({"number": "N", "Address": "Somewhere"})
    assert dto2.job_address == "Somewhere"
