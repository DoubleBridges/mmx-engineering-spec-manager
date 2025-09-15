from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Optional

try:  # shared Result
    from .project_bootstrap_service import Result  # type: ignore
except Exception:  # pragma: no cover
    @dataclass
    class Result:  # type: ignore
        ok: bool
        value: Optional[Any] = None
        error: Optional[str] = None

        @classmethod
        def ok_value(cls, value: Any | None = None) -> "Result":
            return cls(ok=True, value=value, error=None)

        @classmethod
        def fail(cls, error: str) -> "Result":
            return cls(ok=False, value=None, error=error)


class ProjectsService:
    """Service for Projects list/detail use-cases.

    Wraps DataManager to provide a UI-agnostic API. Projects may be returned as
    ORM objects or domain models depending on caller needs.
    """

    def __init__(self, data_manager: Any) -> None:
        self._dm = data_manager

    def get_all_projects(self) -> List[Any]:
        try:
            return list(self._dm.get_all_projects() or [])
        except Exception:
            return []

    def get_project_by_id(self, project_id: int) -> Any | None:
        try:
            return self._dm.get_project_by_id(int(project_id))
        except Exception:
            return None

    def load_enriched_project(self, project: Any) -> Result:
        """Load project with related entities from the project's DB when available."""
        try:
            pid = getattr(project, "id", None)
            if pid is None:
                return Result.ok_value(project)
            loaded = self._dm.get_full_project_from_project_db(int(pid))
            return Result.ok_value(loaded if loaded is not None else project)
        except Exception as e:
            return Result.fail(str(e))
