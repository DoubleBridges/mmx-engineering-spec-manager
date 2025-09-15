from __future__ import annotations
from typing import Any

from mmx_engineering_spec_manager.viewmodels import MainWindowViewModel, WorkspaceViewModel, AttributesViewModel, ProjectsViewModel
from mmx_engineering_spec_manager.services import ProjectBootstrapService, AttributesService


def build_main_window_view_model(data_manager: Any | None = None) -> MainWindowViewModel:
    """Factory to construct MainWindowViewModel with injected dependencies.

    Now inject ProjectBootstrapService to handle project DB ensure/ingest/load orchestration.
    Lazily constructs a DataManager if one is not provided to keep Views UI-only.
    """
    if data_manager is None:
        try:  # lazily construct a DataManager if one wasn't provided
            from mmx_engineering_spec_manager.data_manager.manager import DataManager  # type: ignore
            data_manager = DataManager()
        except Exception:  # pragma: no cover
            data_manager = None
    bootstrap = ProjectBootstrapService(data_manager) if data_manager is not None else None
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
    Lazily constructs a DataManager if one wasn't provided.
    """
    if data_manager is None:
        try:  # lazily construct a DataManager if one wasn't provided
            from mmx_engineering_spec_manager.data_manager.manager import DataManager  # type: ignore
            data_manager = DataManager()
        except Exception:  # pragma: no cover
            data_manager = None
    service = AttributesService(data_manager) if data_manager is not None else None
    return AttributesViewModel(data_manager=data_manager, attributes_service=service)


def build_projects_view_model(data_manager: Any | None = None) -> ProjectsViewModel:
    """Factory to construct ProjectsViewModel.

    Keep DataManager lazy to avoid heavy side effects during View construction in tests.
    The ViewModel will resolve DataManager on-demand when commands are invoked.
    """
    # Intentionally do not create DataManager here to keep Views UI-only and tests lightweight
    return ProjectsViewModel(data_manager=data_manager)


# --- existing imports and builders above ---


def build_project_details_view_model(data_manager: Any | None = None):
    """Factory to construct ProjectDetailsViewModel with injected services.

    Lazily constructs a DataManager if not provided; wires ProjectBootstrapService,
    ProjectsService, and ProductsService.
    """
    if data_manager is None:
        try:  # lazily construct a DataManager if one wasn't provided
            from mmx_engineering_spec_manager.data_manager.manager import DataManager  # type: ignore
            data_manager = DataManager()
        except Exception:  # pragma: no cover
            data_manager = None
    try:
        from mmx_engineering_spec_manager.viewmodels import ProjectDetailsViewModel  # type: ignore
    except Exception:  # pragma: no cover
        ProjectDetailsViewModel = None  # type: ignore
    try:
        from mmx_engineering_spec_manager.services import ProjectsService  # type: ignore
        from mmx_engineering_spec_manager.services import ProductsService  # type: ignore
        from mmx_engineering_spec_manager.services import ProjectBootstrapService  # type: ignore
    except Exception:  # pragma: no cover
        ProjectsService = None  # type: ignore
        ProductsService = None  # type: ignore
    if data_manager is None or ProjectDetailsViewModel is None:
        return None
    projects_service = ProjectsService(data_manager) if ProjectsService is not None else None
    products_service = ProductsService(data_manager) if ProductsService is not None else None
    bootstrap = ProjectBootstrapService(data_manager) if data_manager is not None else None
    return ProjectDetailsViewModel(
        project_bootstrap_service=bootstrap,
        projects_service=projects_service,
        products_service=products_service,
        data_manager=data_manager,
    )
