from __future__ import annotations
from typing import Any

from mmx_engineering_spec_manager.viewmodels import MainWindowViewModel, WorkspaceViewModel, AttributesViewModel


def build_main_window_view_model(data_manager: Any) -> MainWindowViewModel:
    """Factory to construct MainWindowViewModel with injected dependencies.

    Kept minimal for step 1; in later steps, split services and pass them here.
    """
    vm = MainWindowViewModel(data_manager=data_manager)
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
