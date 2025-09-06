from __future__ import annotations
from typing import Any, Dict, Iterable, List

from mmx_engineering_spec_manager.dtos.project_dto import (
    ProjectDTO,
    LocationDTO,
    ProductDTO,
    CustomFieldDTO,
)


def map_custom_fields_to_dtos(custom_fields: Iterable[Dict[str, Any]] | None) -> List[CustomFieldDTO]:
    dtos: List[CustomFieldDTO] = []
    if not custom_fields:
        return dtos
    for cf in custom_fields:
        name = cf.get("Name") or cf.get("name") or ""
        value = cf.get("Value") if "Value" in cf else cf.get("value")
        dtos.append(CustomFieldDTO(name=name, value=value))
    return dtos


def map_products_payload_to_dtos(products_payload: Any) -> List[ProductDTO]:
    items: Iterable[Dict[str, Any]]
    if isinstance(products_payload, dict) and "Items" in products_payload:
        items = products_payload.get("Items", [])
    elif isinstance(products_payload, list):
        items = products_payload
    else:
        items = []

    products: List[ProductDTO] = []
    for item in items:
        products.append(
            ProductDTO(
                name=item.get("Name") or item.get("name") or "",
                quantity=item.get("QuantCount") or item.get("quantity"),
                description=item.get("Description") or item.get("description") or "",
                custom_fields=map_custom_fields_to_dtos(item.get("CustomFields") or item.get("custom_fields")),
            )
        )
    return products


def map_project_payload_to_dto(project_payload: Dict[str, Any], products_payload: Any | None = None) -> ProjectDTO:
    number = project_payload.get("Number") or project_payload.get("number") or ""
    name = project_payload.get("Name") or project_payload.get("name") or ""
    job_description = project_payload.get("JobDescription") or project_payload.get("job_description") or ""
    addr = project_payload.get("Address") or {}
    if isinstance(addr, dict):
        job_address = addr.get("Address1") or addr.get("address1") or addr.get("Address") or ""
    else:
        job_address = str(addr)

    locations_payload = project_payload.get("locations") or project_payload.get("Locations") or []
    locations = [LocationDTO(name=loc.get("name") or loc.get("Name") or "") for loc in locations_payload]

    products = map_products_payload_to_dtos(products_payload) if products_payload is not None else []

    return ProjectDTO(
        number=number,
        name=name,
        job_description=job_description,
        job_address=job_address,
        locations=locations,
        products=products,
        custom_fields=map_custom_fields_to_dtos(project_payload.get("CustomFields") or project_payload.get("custom_fields")),
    )
