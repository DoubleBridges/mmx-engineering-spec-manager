from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class WorkspaceViewState:
    active_project_id: Optional[int] = None


class WorkspaceViewModel:
    def __init__(self) -> None:
        self.view_state = WorkspaceViewState()

    def set_active_project(self, project: Any) -> None:
        self.view_state.active_project_id = getattr(project, "id", None)
