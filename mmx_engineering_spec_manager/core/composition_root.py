from __future__ import annotations
from typing import Any

from mmx_engineering_spec_manager.viewmodels import MainWindowViewModel, WorkspaceViewModel, AttributesViewModel
from mmx_engineering_spec_manager.services import ProjectBootstrapService


def build_main_window_view_model(data_manager: Any) -> MainWindowViewModel:
    """Factory to construct MainWindowViewModel with injected dependencies.

    Now inject ProjectBootstrapService to handle project DB ensure/ingest/load orchestration.
    """
    bootstrap = ProjectBootstrapService(data_manager)
    vm = MainWindowViewModel(data_manager=data_manager, project_bootstrap_service=bootstrap)
    return vm


def build_workspace_view_model() -> WorkspaceViewModel:
    """Factory to construct WorkspaceViewModel.

    No dependencies yet; will inject domain services as they are extracted.
    """
    return WorkspaceViewModel()


def build_attributes_view_model(data_manager: Any | None = None) -> AttributesViewModel:
    """Factory to construct AttributesViewModel.

    Inject DataManager to enable DB-backed operations.
    """
    return AttributesViewModel(data_manager=data_manager)
