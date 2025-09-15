from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Optional


class Event:
    def __init__(self) -> None:
        self._subs: list[Callable[..., None]] = []

    def subscribe(self, cb: Callable[..., None]) -> None:
        if cb not in self._subs:
            self._subs.append(cb)

    def emit(self, *args: Any, **kwargs: Any) -> None:
        for cb in list(self._subs):
            try:
                cb(*args, **kwargs)
            except Exception:
                # Never let observer exceptions bubble from VM logic
                pass


@dataclass
class ExportViewState:
    active_project_id: Optional[int] = None
    is_exporting: bool = False
    last_result: Optional[str] = None
    error: Optional[str] = None


class ExportViewModel:
    """Minimal ViewModel for Export tab.

    Commands:
      - set_active_project(project)
      - export(params)
    Events:
      - export_started()
      - export_progress(int)
      - export_completed(result: str | None)
      - notification({level, message})
    """

    def __init__(self, export_service: Any | None = None) -> None:
        self.view_state = ExportViewState()
        self._service = export_service  # may be None for now (placeholder)
        # Events
        self.export_started = Event()
        self.export_progress = Event()
        self.export_completed = Event()
        self.notification = Event()

    # ---- Commands ----
    def set_active_project(self, project: Any) -> None:
        self.view_state.active_project_id = getattr(project, "id", None)

    def export(self, params: dict | None = None) -> Optional[str]:
        """Trigger an export via the injected service if available.

        Returns a result string (e.g., file path) when successful; emits events.
        """
        pid = self.view_state.active_project_id
        if not pid:
            self._notify("No active project selected for export", level="warning")
            return None
        try:
            self.view_state.is_exporting = True
            try:
                self.export_started.emit()
            except Exception:
                pass
            result: Optional[str] = None
            if self._service is not None and hasattr(self._service, "export"):
                # The service may accept callbacks for progress; pass through our event
                try:
                    result = self._service.export(int(pid), params or {}, progress_cb=self.export_progress.emit)
                except TypeError:
                    # Service may not support progress callback yet
                    result = self._service.export(int(pid), params or {})
            # Persist in state and notify
            self.view_state.last_result = result
            try:
                self.export_completed.emit(result)
            except Exception:
                pass
            if result:
                self._notify("Export completed")
            else:
                self._notify("Export finished with no result", level="warning")
            return result
        except Exception as e:  # pragma: no cover
            self._set_error(str(e))
            return None
        finally:
            self.view_state.is_exporting = False

    # ---- Helpers ----
    def _set_error(self, message: str) -> None:
        self.view_state.error = message
        self.notification.emit({"level": "error", "message": message})

    def _notify(self, message: str, level: str = "info") -> None:
        self.notification.emit({"level": level, "message": message})
