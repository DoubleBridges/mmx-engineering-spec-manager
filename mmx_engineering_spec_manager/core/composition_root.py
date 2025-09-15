from __future__ import annotations
from typing import Any

from mmx_engineering_spec_manager.viewmodels import MainWindowViewModel, WorkspaceViewModel, AttributesViewModel
from mmx_engineering_spec_manager.services import ProjectBootstrapService, AttributesService


def build_main_window_view_model(data_manager: Any) -> MainWindowViewModel:
    """Factory to construct MainWindowViewModel with injected dependencies.

    Now inject ProjectBootstrapService to handle project DB ensure/ingest/load orchestration.
    """
    bootstrap = ProjectBootstrapService(data_manager)
    vm = MainWindowViewModel(data_manager=data_manager, project_bootstrap_service=bootstrap)
    return vm


def build_workspace_view_model(data_manager: Any | None = None) -> WorkspaceViewModel:
    """Factory to construct WorkspaceViewModel.

    Builds and injects WorkspaceService for domain data loading/saving.
    """
    try:
        from mmx_engineering_spec_manager.services import WorkspaceService  # local import to avoid cycles
    except Exception:  # pragma: no cover
        WorkspaceService = None  # type: ignore
    if data_manager is None:
        try:  # lazily construct a DataManager if one wasn't provided
            from mmx_engineering_spec_manager.data_manager.manager import DataManager  # type: ignore
            data_manager = DataManager()
        except Exception:  # pragma: no cover
            data_manager = None
    service = WorkspaceService(data_manager) if (data_manager is not None and WorkspaceService is not None) else None
    return WorkspaceViewModel(workspace_service=service)


def build_attributes_view_model(data_manager: Any | None = None) -> AttributesViewModel:
    """Factory to construct AttributesViewModel.

    Provide AttributesService built from DataManager for MVVM-compliant loading/saving.
    """
    service = AttributesService(data_manager) if data_manager is not None else None
    return AttributesViewModel(data_manager=data_manager, attributes_service=service)
