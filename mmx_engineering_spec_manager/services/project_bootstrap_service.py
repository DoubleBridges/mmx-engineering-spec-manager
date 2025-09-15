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

    Minimal implementation for Phase 1, step 3: wraps DataManager operations so
    ViewModels can delegate orchestration without touching UI or I/O directly.
    """

    def __init__(self, data_manager: Any, settings_provider: Any | None = None, db_path_provider: Any | None = None) -> None:
        # Keep dependencies simple and late-bound to avoid UI/toolkit imports here
        self._dm = data_manager
        # Inject providers to enable testing and avoid hard-coupling
        if settings_provider is None:
            try:  # pragma: no cover
                from mmx_engineering_spec_manager.utilities.settings import get_settings as _get_settings  # type: ignore
            except Exception:  # pragma: no cover
                def _get_settings():  # type: ignore
                    return type("S", (), {"innergy_api_key": None})()
            settings_provider = _get_settings
        if db_path_provider is None:
            try:  # pragma: no cover
                from mmx_engineering_spec_manager.utilities.persistence import project_sqlite_db_path as _db_path  # type: ignore
            except Exception:  # pragma: no cover
                def _db_path(project):  # type: ignore
                    return None
            db_path_provider = _db_path
        self._get_settings = settings_provider
        self._db_path = db_path_provider

    def ensure_project_db(self, project: Any) -> Result[None, str]:
        """Ensure the per-project SQLite DB exists and is schema-initialized.

        Parameters:
            project: Domain object (should at least have an 'id' and possibly 'number').

        Returns:
            Result.ok_value(None) on success, or Result.fail(error_message) on failure.
        """
        try:
            # Delegate to DataManager if available
            prepare = getattr(self._dm, "prepare_project_db", None)
            if prepare is None:
                return Result.fail("DataManager missing prepare_project_db")
            prepare(project)
            return Result.ok_value(None)
        except Exception as e:
            return Result.fail(str(e))

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
        try:
            # Decide if ingestion is needed (first-time open): DB path does not exist
            import os
            db_path = self._db_path(project)
            existed_already = bool(db_path and os.path.exists(db_path))
            if existed_already:
                return Result.ok_value(False)
            # Check API key
            settings = settings or self._get_settings()
            has_api_key = bool(getattr(settings, "innergy_api_key", None))
            if not has_api_key:
                return Result.ok_value(False)
            # Perform ingestion via DataManager
            ingest = getattr(self._dm, "ingest_project_details_to_project_db", None)
            num = getattr(project, "number", None)
            if ingest is None or not num:
                return Result.ok_value(False)
            success = bool(ingest(str(num)))
            if success:
                return Result.ok_value(True)
            return Result.fail(f"Ingestion failed for project {num}")
        except Exception as e:
            return Result.fail(str(e))

    def load_enriched_project(self, project: Any) -> Result[Any, str]:
        """Load the enriched project from the per-project DB if available.

        Parameters:
            project: Domain project object; should include 'id'.

        Returns:
            Result.ok_value(project_like) on success, or Result.fail(error_message) on failure.
        """
        try:
            getter = getattr(self._dm, "get_full_project_from_project_db", None)
            pid = getattr(project, "id", None)
            if getter is None or pid is None:
                return Result.ok_value(project)
            loaded = getter(pid)
            return Result.ok_value(loaded if loaded is not None else project)
        except Exception as e:
            return Result.fail(str(e))
