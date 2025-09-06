from __future__ import annotations
from typing import Protocol, Optional, Iterable, Any


class ProjectRepository(Protocol):
    """
    Repository protocol for Project aggregate. Minimal interface for MVP.
    """

    def get_all(self) -> Iterable[Any]:
        ...

    def get_by_id(self, project_id: int) -> Optional[Any]:
        ...

    def get_by_number(self, number: str) -> Optional[Any]:
        ...

    def add(self, project: Any) -> None:
        ...

    def update(self, project: Any) -> None:
        ...
