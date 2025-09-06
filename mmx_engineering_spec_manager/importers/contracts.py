from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable, Optional


@dataclass(frozen=True)
class ProjectSummaryDTO:
    id: Any
    number: str
    name: str = ""
    address: str = ""


class ProjectImporter(ABC):
    """Abstract importer for project data sources."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def list_projects(self) -> Iterable[ProjectSummaryDTO]:
        """Return a list of projects available from the source."""
        ...

    @abstractmethod
    def fetch_project(self, job_id: Any) -> dict:
        """Fetch a complete project payload for a given job/project id."""
        ...

    def fetch_products(self, job_id: Any) -> Optional[Iterable[dict]]:
        """Optional: Fetch product list payloads for the given job/project id."""
        return None
