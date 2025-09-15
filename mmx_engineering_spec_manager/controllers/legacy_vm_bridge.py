from __future__ import annotations
from typing import Any, Optional


class ThinVMControllerBridge:
    """
    Thin adapter that bridges ViewModel events to legacy controllers.

    Purpose:
    - While migrating logic into ViewModels, keep legacy controllers wired
      without Views needing to know about them.
    - Subscribes to a MainWindowViewModel-like object that exposes
      `project_opened` and `refresh_requested` events with a simple
      subscribe(cb) API.

    This class intentionally avoids importing Qt; it relies on the
    controllers' public methods and the VM's event API only.
    """

    def __init__(
        self,
        view_model: Any,
        projects_controller: Optional[Any] = None,
        workspace_controller: Optional[Any] = None,
        export_controller: Optional[Any] = None,
    ) -> None:
        self._vm = view_model
        self._projects = projects_controller
        self._workspace = workspace_controller
        self._export = export_controller

        # Keep references to callbacks for potential unsubscription
        self._on_opened_cb = lambda p: self._on_project_opened(p)
        self._on_refresh_cb = lambda: self._on_refresh_requested()

        try:
            if hasattr(self._vm, "project_opened") and hasattr(self._vm.project_opened, "subscribe"):
                self._vm.project_opened.subscribe(self._on_opened_cb)
        except Exception:
            pass
        try:
            if hasattr(self._vm, "refresh_requested") and hasattr(self._vm.refresh_requested, "subscribe"):
                self._vm.refresh_requested.subscribe(self._on_refresh_cb)
        except Exception:
            pass

    # --- Event handlers ---
    def _on_project_opened(self, project: Any) -> None:
        try:
            if self._workspace is not None and hasattr(self._workspace, "set_active_project"):
                self._workspace.set_active_project(project)
        except Exception:
            pass
        try:
            if self._export is not None and hasattr(self._export, "set_active_project"):
                self._export.set_active_project(project)
        except Exception:
            pass

    def _on_refresh_requested(self) -> None:
        try:
            if self._projects is not None and hasattr(self._projects, "load_projects"):
                self._projects.load_projects()
        except Exception:
            pass

    def detach(self) -> None:
        """Detach subscriptions from the ViewModel (best-effort)."""
        try:
            if hasattr(self._vm, "project_opened") and hasattr(self._vm.project_opened, "unsubscribe"):
                self._vm.project_opened.unsubscribe(self._on_opened_cb)
        except Exception:
            pass
        try:
            if hasattr(self._vm, "refresh_requested") and hasattr(self._vm.refresh_requested, "unsubscribe"):
                self._vm.refresh_requested.unsubscribe(self._on_refresh_cb)
        except Exception:
            pass
