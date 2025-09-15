# MVVM Refactor Plan (Stricter MVVM Adoption)

This plan operationalizes junie/guidelines.md to complete the migration to a strict MVVM architecture.

Last updated: 2025-09-14

## Goals
- Views contain UI-only logic (rendering and event wiring) with no I/O/business rules.
- ViewModels expose serializable view_state, commands, and notifications; no UI toolkit types in public API.
- Services/Repositories own all I/O and use-case orchestration.
- Composition root wires dependencies (constructor injection, no globals).
- Tests: add robust unit tests for ViewModels; keep View tests shallow.

## Current Assessment (quick audit)
- views/main_window.py: Transitional VM wiring present but still performs DataManager orchestration (ensure project DB, ingestion from Innergy, progress dialogs). Violates View-only rule.
- views/attributes/attributes_tab.py: Imports DataManager and likely performs load/save of callouts and location tables directly. Needs VM + Service extraction.
- views/workspace/workspace_tab.py: Thin, mostly presentation; has optional set_view_model hook. Low risk.
- controllers/main_window_controller.py: Legacy controller wiring remains. To be replaced by ViewModel orchestration and then removed.
- core/composition_root.py: Referenced by main_window.py (build_*_view_model functions). Ensure it exists/expand it to construct Services + VMs.

## Target Architecture Snapshot
- ViewModels: MainWindowViewModel, AttributesViewModel, WorkspaceViewModel, (optionally) ProjectsViewModel(s).
- Services: ProjectBootstrapService (project DB ensure/ingest/load), AttributesService (callouts + location tables), WorkspaceService (tree/geometry/persistence).
- Views: bind to VMs only; map UI toolkit types to domain DTOs when calling VM.
- DI: core/composition_root.py builds Repositories → Services → ViewModels.

## Phased Plan

### Phase 1 — Composition Root + MainWindow ViewModel and Project Bootstrap Service
1. Implement ProjectBootstrapService (services/project_bootstrap_service.py):
   - ensure_project_db(project) → Result[None, Error]
   - ingest_project_details_if_needed(project, settings) → Result[bool, Error]
   - load_enriched_project(project) → Result[Project, Error]
2. Implement MainWindowViewModel (viewmodels/main_window_view_model.py):
   - Events: project_opened, refresh_requested, notify
   - Commands: set_active_project(project_id or domain object), request_refresh()
   - Orchestrates project selection using ProjectBootstrapService; emits view_state snapshots for UI controls enabling/loading/error.
3. Expand core/composition_root.py:
   - build_main_window_view_model(data_manager?) uses proper repositories/services.
   - Ensure no UI imports here.
4. Refactor views/main_window.py:
   - Remove direct DataManager usage and ingestion logic; call vm.set_active_project and render via state/notifications.
   - Keep temporary adapters so existing signals continue to work (already partially present).
5. Tests:
   - tests/test_viewmodels/test_main_window_view_model.py covering happy/error paths.
   - Update/keep tests/test_views/test_main_window.py to assert wiring and rendering only.

### Phase 2 — Attributes: Service + ViewModel
1. Implement AttributesService (services/attributes_service.py):
   - load_callouts(project_id) → Dict[str, List[Row]]
   - save_callouts(project_id, rows) → Result[None, Error]
   - load_locations_and_tables(project_id) / save_location_table(...)
2. Implement AttributesViewModel (viewmodels/attributes_view_model.py):
   - State: per-category rows, current project, is_loading, is_saving, error.
   - Commands: set_active_project(project), load_callouts(), save_callouts(rows), load_locations(), mutate_location_rows(...).
3. Refactor views/attributes/attributes_tab.py:
   - Use set_view_model(vm); on button clicks call VM commands.
   - Render from vm.state only; remove direct DataManager usage.
4. Tests:
   - tests/test_viewmodels/test_attributes_view_model.py (happy/error).
   - Adjust tests/test_views/test_attributes_tab.py (wiring + rendering).

### Phase 3 — Workspace: Service + ViewModel
1. Implement WorkspaceService (services/workspace_service.py):
   - load_project_tree(project_id) → DTO
   - save_changes(changes) → Result[None, Error]
2. Implement WorkspaceViewModel (viewmodels/workspace_view_model.py):
   - State: nodes/tree, is_loading, error, dirty flags.
   - Commands: set_active_project(project), load(), save_changes(changes).
3. Refactor views/workspace/workspace_tab.py:
   - Bind signals; map UI widgets to domain DTOs before calling VM.
   - Render tree/labels from state.
4. Tests:
   - tests/test_viewmodels/test_workspace_view_model.py
   - Adjust tests/test_views/test_workspace_tab.py if needed.

### Phase 4 — Retire Controllers and Legacy Wiring
1. Migrate logic from controllers/* into corresponding ViewModels.
2. Keep a thin adapter if needed for one release; then remove controllers package.
3. Simplify main.py startup to use composition_root to assemble VMs and Views.

### Phase 5 — Quality Gates and Docs
1. Update PR template with checklist from junie/guidelines.md.
2. Add a static check in CI that forbids imports from services/* or repositories/* within views/*.
3. Document deviations (if any) in junie/guidelines.md.

## Acceptance Criteria
- No direct service/repository/DataManager usage in views/*.
- ViewModels expose immutable-ish view_state and domain types only.
- Services own all I/O; ViewModels orchestrate and map to view_state.
- composition_root constructs all dependencies; no globals.
- tests/test_viewmodels contains coverage for each VM (happy/error paths).
- controllers/* removed after parity; app functions without controllers.

## Risks and Mitigations
- UI regressions during extraction → Use transitional adapters (already present) and add VM tests.
- Test brittleness → Keep View tests shallow; concentrate logic tests in VMs.
- DI complexity → Keep composition_root small and explicit; use dataclasses for config.

## Work Breakdown Summary (by file)
- core/composition_root.py: ensure build_*_view_model functions wire services correctly.
- views/main_window.py: strip I/O/DM logic; bind VM commands and render state.
- views/attributes/attributes_tab.py: remove DataManager usage; bind to AttributesViewModel.
- views/workspace/workspace_tab.py: ensure full VM wiring for load/save.
- viewmodels/*: add main_window_view_model.py, attributes_view_model.py, workspace_view_model.py.
- services/*: add project_bootstrap_service.py, attributes_service.py, workspace_service.py.
- controllers/*: mark deprecated; delete after parity.
- tests/test_viewmodels/*: add new tests.

## Timeline (indicative)
- Week 1: Phase 1
- Week 2: Phase 2
- Week 3: Phase 3
- Week 4: Phase 4–5
