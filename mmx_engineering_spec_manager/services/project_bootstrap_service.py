from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, Optional, TypeVar, Any


T = TypeVar("T")
E = TypeVar("E")


@dataclass
class Result(Generic[T, E]):
    """A tiny Result type to model success/failure without raising exceptions.

    - On success: ok=True, value is set, error=None
    - On failure: ok=False, value=None, error is set
    """
    ok: bool
    value: Optional[T] = None
    error: Optional[E] = None

    @classmethod
    def ok_value(cls, value: T | None = None) -> "Result[T, E]":
        return cls(ok=True, value=value, error=None)

    @classmethod
    def fail(cls, error: E) -> "Result[T, E]":
        return cls(ok=False, value=None, error=error)


class ProjectBootstrapService:
    """Service responsible for ensuring a project's local DB, optionally ingesting
    additional details on first load, and returning an enriched project object.

    Step 1 (scaffolding): Only declare the API and docstrings.
    Concrete orchestration and DataManager/Repository usage will be implemented
    in subsequent steps of the MVVM refactor.
    """

    def ensure_project_db(self, project: Any) -> Result[None, str]:
        """Ensure the per-project SQLite DB exists and is schema-initialized.

        Parameters:
            project: Domain object (should at least have an 'id' and possibly 'number').

        Returns:
            Result.ok_value(None) on success, or Result.fail(error_message) on failure.
        """
        return Result.fail("Not implemented yet (Phase 1, step 1 scaffolding)")

    def ingest_project_details_if_needed(self, project: Any, settings: Any | None = None) -> Result[bool, str]:
        """If this is the first time opening the project and credentials are available,
        ingest project details (e.g., from Innergy) into the project's DB.

        Parameters:
            project: Domain project object; should include 'number'.
            settings: Optional settings/config that may include API credentials.

        Returns:
            Result.ok_value(True) if ingestion happened successfully,
            Result.ok_value(False) if no ingestion was needed or attempted,
            or Result.fail(error_message) on failure.
        """
        return Result.fail("Not implemented yet (Phase 1, step 1 scaffolding)")

    def load_enriched_project(self, project: Any) -> Result[Any, str]:
        """Load the enriched project from the per-project DB if available.

        Parameters:
            project: Domain project object; should include 'id'.

        Returns:
            Result.ok_value(project_like) on success, or Result.fail(error_message) on failure.
        """
        return Result.fail("Not implemented yet (Phase 1, step 1 scaffolding)")
