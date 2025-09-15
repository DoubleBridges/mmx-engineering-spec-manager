from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional

try:
    # Only for typing; avoid runtime dependency where possible
    from mmx_engineering_spec_manager.data_manager.manager import DataManager
except Exception:  # pragma: no cover - typing aid only
    DataManager = Any  # type: ignore

# Utilities used for project activation. Keep UI toolkit out of VM.
try:  # pragma: no cover - import resilience for tests
    from mmx_engineering_spec_manager.utilities.settings import get_settings
except Exception:  # pragma: no cover
    def get_settings():  # type: ignore
        return type("S", (), {"innergy_api_key": None})()

try:  # pragma: no cover - import resilience for tests
    from mmx_engineering_spec_manager.utilities.persistence import project_sqlite_db_path
except Exception:  # pragma: no cover
    def project_sqlite_db_path(project):  # type: ignore
        return None


@dataclass
class MainWindowViewState:
    """Serializable state for MainWindow view.

    Keep UI toolkit types out of this state. Only domain-safe types.
    """
    active_project_id: Optional[int] = None
    status_message: str = ""
    is_busy: bool = False
    error: Optional[str] = None


class Event:
    """Lightweight pub-sub for ViewModel events (no Qt dependency)."""

    def __init__(self) -> None:
        self._subscribers: List[Callable[..., None]] = []

    def subscribe(self, callback: Callable[..., None]) -> None:
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[..., None]) -> None:
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def emit(self, *args: Any, **kwargs: Any) -> None:
        for cb in list(self._subscribers):
            try:
                cb(*args, **kwargs)
            except Exception:
                # ViewModel should not crash on observer exceptions
                pass


class MainWindowViewModel:
    """ViewModel for the Main Window.

    - Holds MainWindowViewState
    - Exposes events for user intents and cross-tab coordination
    - No direct UI toolkit usage or knowledge
    """

    def __init__(self, data_manager: DataManager | Any = None, project_bootstrap_service: Any | None = None) -> None:
        # Keep DataManager for legacy paths during phased migration
        self._data_manager = data_manager
        # Bootstrap service handles ensure/load/ingest orchestration
        if project_bootstrap_service is None:
            try:
                from mmx_engineering_spec_manager.services import ProjectBootstrapService  # type: ignore
                self._bootstrap_service = ProjectBootstrapService(data_manager)
            except Exception:  # pragma: no cover
                self._bootstrap_service = None  # type: ignore
        else:
            self._bootstrap_service = project_bootstrap_service
        self.view_state: MainWindowViewState = MainWindowViewState()

        # Events
        self.project_opened = Event()
        self.refresh_requested = Event()
        self.notification = Event()  # ephemeral messages

    # Intents / Commands
    def set_active_project(self, project: Any) -> None:
        """Activate a project and notify listeners with the enriched project.

        Orchestrates per-project DB preparation and optional ingestion (no UI code).
        """
        project_id = getattr(project, "id", None)
        self.view_state.active_project_id = project_id
        # Reset errors/status when switching context
        self.view_state.error = None
        self.view_state.status_message = ""

        enriched = project
        try:
            # Determine per-project DB path BEFORE preparing, so we can detect prior existence
            db_path = project_sqlite_db_path(project)
            existed_already = bool(db_path and os.path.exists(db_path))

            # Ensure the project's dedicated SQLite DB and schema exists (delegate to service)
            try:
                if getattr(self, "_bootstrap_service", None) is not None:
                    res = self._bootstrap_service.ensure_project_db(project)
                    if not getattr(res, "ok", False):
                        self.notify(f"Failed to prepare project DB: {getattr(res, 'error', 'unknown error')}", level="warning")
                elif getattr(self, "_data_manager", None) is not None:  # fallback during transition
                    self._data_manager.prepare_project_db(project)
            except Exception as e:  # pragma: no cover
                # Non-fatal in VM; proceed and let subsequent steps attempt to load/ingest
                self.notify(f"Failed to prepare project DB: {e}", level="warning")

            num = getattr(project, "number", None)
            pid = getattr(project, "id", None)

            # If a DB file existed already, prefer loading from it via the bootstrap service and SKIP any API calls
            if existed_already and pid is not None:
                try:
                    if getattr(self, "_bootstrap_service", None) is not None:
                        res = self._bootstrap_service.load_enriched_project(project)
                        if getattr(res, "ok", False):
                            loaded = getattr(res, "value", None)
                            if loaded is not None:
                                enriched = loaded
                                self.project_opened.emit(enriched)
                                return
                        else:
                            self.notify(f"Failed to load project from DB: {getattr(res, 'error', 'unknown error')}", level="warning")
                    elif getattr(self, "_data_manager", None) is not None:  # fallback during transition
                        loaded = self._data_manager.get_full_project_from_project_db(pid)
                        if loaded is not None:
                            enriched = loaded
                            self.project_opened.emit(enriched)
                            return
                except Exception as e:
                    # If load fails, fall back to the ingestion path below
                    self.notify(f"Failed to load project from DB: {e}", level="warning")

            # Otherwise, fall back to ingestion path (only if number is present)
            if num:
                success = None
                try:
                    settings = get_settings()
                except Exception:
                    settings = None
                has_api_key = bool(getattr(settings, "innergy_api_key", None))

                # Perform ingestion (blocking in current thread; no UI responsibilities here)
                try:
                    if has_api_key:
                        success = self._data_manager.ingest_project_details_to_project_db(str(num))
                except Exception as e:
                    self.set_error(str(e))
                    success = False

                # Try to load enriched project from per-project DB regardless via the bootstrap service
                try:
                    if getattr(self, "_bootstrap_service", None) is not None:
                        res = self._bootstrap_service.load_enriched_project(project)
                        if getattr(res, "ok", False):
                            loaded = getattr(res, "value", None)
                            if loaded is not None:
                                enriched = loaded
                        else:
                            self.notify(f"Failed to load project from DB: {getattr(res, 'error', 'unknown error')}", level="warning")
                    elif getattr(self, "_data_manager", None) is not None:  # fallback during transition
                        loaded = self._data_manager.get_full_project_from_project_db(pid)
                        if loaded is not None:
                            enriched = loaded
                except Exception:
                    pass

                # Surface failure as notification (UI can decide how to present)
                if has_api_key and success is False:
                    self.set_error(f"Failed to load project details from Innergy for project {num}.")
        except Exception as e:
            # Catch-all to keep VM safe
            self.set_error(str(e))
        finally:
            # Notify listeners with the best available project object
            self.project_opened.emit(enriched)

    def request_refresh(self) -> None:
        """Signal that a refresh of projects was requested (e.g., F5)."""
        self.refresh_requested.emit()

    # Convenience helpers
    def set_busy(self, busy: bool, message: str = "") -> None:
        self.view_state.is_busy = busy
        if message:
            self.view_state.status_message = message

    def set_error(self, message: str) -> None:
        self.view_state.error = message
        self.notification.emit({"level": "error", "message": message})

    def notify(self, message: str, level: str = "info") -> None:
        self.notification.emit({"level": level, "message": message})
