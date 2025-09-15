from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, Callable, Dict

try:  # pragma: no cover - import resilience for tests
    from mmx_engineering_spec_manager.services import WorkspaceService, Result  # type: ignore
except Exception:  # pragma: no cover
    WorkspaceService = Any  # type: ignore
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
                # Never surface observer exceptions
                pass


@dataclass
class WorkspaceViewState:
    active_project_id: Optional[int] = None
    tree: Dict[str, Any] = field(default_factory=dict)
    is_loading: bool = False
    error: Optional[str] = None
    dirty: bool = False


class WorkspaceViewModel:
    """ViewModel for the Workspace tab.

    - Holds a serializable tree for project → locations → walls → products
    - No UI toolkit imports
    - Delegates I/O to WorkspaceService
    """

    def __init__(self, workspace_service: WorkspaceService | None = None) -> None:
        self.view_state = WorkspaceViewState()
        self._service = workspace_service
        # Events for Views to subscribe to
        self.tree_loaded = Event()
        self.notification = Event()

    # ---- Commands ----
    def set_active_project(self, project: Any) -> None:
        self.view_state.active_project_id = getattr(project, "id", None)
        # Reset state specific to project
        self.view_state.tree = {}
        self.view_state.error = None
        self.view_state.dirty = False

    def load(self) -> Dict[str, Any]:
        """Load the project tree via service and update state.

        Returns the loaded tree (possibly empty) for convenience.
        """
        pid = self.view_state.active_project_id
        if not pid:
            return {}
        self.view_state.is_loading = True
        try:
            if self._service is None:
                # No service available; return empty tree in transitional mode
                tree: Dict[str, Any] = {}
            else:
                tree = self._service.load_project_tree(int(pid)) or {}
            self.view_state.tree = tree
            self.view_state.error = None
            self.tree_loaded.emit(tree)
            return tree
        except Exception as e:  # pragma: no cover
            self._set_error(str(e))
            return {}
        finally:
            self.view_state.is_loading = False

    def save_changes(self, changes: Dict[str, Any] | None = None) -> bool:
        """Persist changes to the project via the service.

        Returns True on success; emits notification and clears dirty flag.
        """
        pid = self.view_state.active_project_id
        if not pid or self._service is None:
            return False
        try:
            res: Result = self._service.save_changes(changes or {})
            if getattr(res, "ok", False):
                self.view_state.dirty = False
                self.notification.emit({"level": "info", "message": "Workspace saved"})
                return True
            self._set_error(getattr(res, "error", "Failed to save"))
            return False
        except Exception as e:  # pragma: no cover
            self._set_error(str(e))
            return False

    # ---- Helpers ----
    def mark_dirty(self, is_dirty: bool = True) -> None:
        self.view_state.dirty = bool(is_dirty)

    def _set_error(self, message: str) -> None:
        self.view_state.error = message
        self.notification.emit({"level": "error", "message": message})
