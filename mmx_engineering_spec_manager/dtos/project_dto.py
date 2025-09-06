from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class CustomFieldDTO:
    name: str
    value: Optional[str] = None


@dataclass(frozen=True)
class ProductDTO:
    name: str
    quantity: Optional[int] = None
    description: str = ""
    custom_fields: List[CustomFieldDTO] = field(default_factory=list)


@dataclass(frozen=True)
class LocationDTO:
    name: str


@dataclass(frozen=True)
class ProjectDTO:
    number: str
    name: str = ""
    job_description: str = ""
    job_address: str = ""
    locations: List[LocationDTO] = field(default_factory=list)
    products: List[ProductDTO] = field(default_factory=list)
    custom_fields: List[CustomFieldDTO] = field(default_factory=list)
