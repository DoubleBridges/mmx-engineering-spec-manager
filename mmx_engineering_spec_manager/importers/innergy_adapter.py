from __future__ import annotations
from typing import Iterable, Optional, Any

from mmx_engineering_spec_manager.importers.contracts import ProjectImporter, ProjectSummaryDTO
from mmx_engineering_spec_manager.importers.innergy import InnergyImporter


class InnergyProjectImporterAdapter(ProjectImporter):
    """Adapter to expose InnergyImporter via the generic ProjectImporter contract."""

    def __init__(self, innergy: Optional[InnergyImporter] = None):
        self._innergy = innergy or InnergyImporter()

    @property
    def name(self) -> str:
        return "innergy"

    def list_projects(self) -> Iterable[ProjectSummaryDTO]:
        projects = self._innergy.get_projects() or []
        result: list[ProjectSummaryDTO] = []
        for p in projects:
            # p contains: Id, Number, Name, Address (per InnergyImporter filtering)
            result.append(
                ProjectSummaryDTO(
                    id=p.get("Id"),
                    number=p.get("Number", ""),
                    name=p.get("Name", ""),
                    address=p.get("Address", ""),
                )
            )
        return result

    def fetch_project(self, job_id: Any) -> dict:
        return self._innergy.get_job_details(job_id) or {}

    def fetch_products(self, job_id: Any) -> Optional[Iterable[dict]]:
        payload = self._innergy.get_products(job_id)
        if not payload:
            return []
        # Normalize to a list of dicts
        if isinstance(payload, dict) and "Items" in payload:
            return payload.get("Items", [])
        if isinstance(payload, list):
            return payload
        return []
