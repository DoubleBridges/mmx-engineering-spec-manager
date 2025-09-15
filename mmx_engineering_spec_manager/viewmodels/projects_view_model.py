from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional


try:  # pragma: no cover - import resilience for tests
    from mmx_engineering_spec_manager.data_manager.manager import DataManager
except Exception:  # pragma: no cover
    DataManager = Any  # type: ignore


class Event:
    def __init__(self) -> None:
        self._subs: List[Callable[..., None]] = []

    def subscribe(self, cb: Callable[..., None]) -> None:
        if cb not in self._subs:
            self._subs.append(cb)

    def unsubscribe(self, cb: Callable[..., None]) -> None:
        if cb in self._subs:
            self._subs.remove(cb)

    def emit(self, *args: Any, **kwargs: Any) -> None:
        for cb in list(self._subs):
            try:
                cb(*args, **kwargs)
            except Exception:
                # Never let observer exceptions bubble from a VM
                pass


@dataclass
class ProjectsViewState:
    projects: List[Any] = field(default_factory=list)
    error: Optional[str] = None


class ProjectsViewModel:
    """ViewModel for the Projects tab/domain.

    Responsibilities (UI-agnostic):
    - Load the projects list from a DataManager/Repository
    - Open a project by id (return a detailed project object)
    - Emit events the View/Controller can subscribe to
    """

    def __init__(self, data_manager: DataManager | Any = None) -> None:
        self._dm = data_manager
        self.view_state = ProjectsViewState()
        # Events
        self.projects_loaded = Event()
        self.project_opened = Event()
        self.notification = Event()

    # ---- Commands ----
    def load_projects(self) -> List[Any]:
        try:
            projects = []
            if getattr(self, "_dm", None) is not None:
                projects = self._dm.get_all_projects()
            self.view_state.projects = list(projects or [])
            self.view_state.error = None
            self.projects_loaded.emit(self.view_state.projects)
            return self.view_state.projects
        except Exception as e:  # pragma: no cover
            self._set_error(str(e))
            return []

    def open_project(self, project: Any) -> Any | None:
        """Return a detailed project domain object and emit project_opened.

        Accepts a lightweight project (with .id), fetches the detailed
        project via DataManager, and emits the event.
        """
        try:
            detailed = None
            if getattr(self, "_dm", None) is not None and project is not None:
                pid = getattr(project, "id", None)
                if pid is not None:
                    detailed = self._dm.get_project_by_id(pid)
            # Fallback to input if fetch unavailable
            if detailed is None:
                detailed = project
            self.project_opened.emit(detailed)
            return detailed
        except Exception as e:  # pragma: no cover
            self._set_error(str(e))
            return None

    # ---- Helpers ----
    def _set_error(self, message: str) -> None:
        self.view_state.error = message
        self.notification.emit({"level": "error", "message": message})
