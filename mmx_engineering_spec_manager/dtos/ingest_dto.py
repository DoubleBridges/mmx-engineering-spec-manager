from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

from .project_dto import ProjectDTO


@dataclass(frozen=True)
class IngestProjectDTO:
    """
    Wraps a mapped ProjectDTO with optional raw payloads for diagnostics.
    """
    project: ProjectDTO
    source: str = "innergy"
    raw_project_payload: Optional[Dict[str, Any]] = None
    raw_products_payload: Optional[Iterable[Dict[str, Any]]] = None
