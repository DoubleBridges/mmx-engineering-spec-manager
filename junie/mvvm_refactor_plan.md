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


---

## Controller Sunset Plan (Complete Removal)

Last updated: 2025-09-14

This section specifies the exact steps to fully remove legacy controllers and migrate their logic into the MVVM stack, strictly adhering to junie/guidelines.md.

### 0) Inventory: legacy controllers and where they’re referenced
- controllers/main_window_controller.py
- controllers/projects_controller.py
- controllers/workspace_controller.py
- controllers/export_controller.py
- controllers/legacy_vm_bridge.py
- Known references:
  - core/app_factory.py imports MainWindowController
  - views/main_window.py contains transitional notes; should not import any controller
  - tests/test_controllers/* depend on controllers

### 1) Mapping controller responsibilities → ViewModels and Services
- ProjectsController
  - import_from_innergy → ProjectsViewModel.import_from_innergy()
    - Events: import_started(), import_progress(int), import_completed(int), notification({level,message}), projects_loaded(list)
    - Service: ProjectsService.sync_projects_from_innergy(progress_cb)
  - load_projects → ProjectsViewModel.load_projects() → emits projects_loaded(list)
  - save_project → ProjectsViewModel.save_project(data) → emits notification + projects_loaded
  - open_project → MainWindowViewModel.set_active_project(project) emits project_opened(project)
  - products (load/save) → ProjectDetailsViewModel.load_products_from_innergy_if_needed() and save_products_changes() [already implemented]
- MainWindowController
  - Child controller wiring and bridging → eliminated. MainWindowView wires Views directly to ViewModels.
  - Use MainWindowViewModel for app-level coordination: refresh, active project selection, cross-tab signals.
- WorkspaceController
  - set_active_project → WorkspaceViewModel.set_active_project(project) and WorkspaceViewModel.load()
- ExportController
  - export actions → ExportViewModel with commands/events as needed (mirror Workspace pattern).
- Legacy VM Bridge
  - Delete after parity. Events now go View ← VM directly.

### 2) Cross-VM event contracts (consistent with guidelines)
- MainWindowViewModel
  - Commands: set_active_project(project), request_refresh()
  - Events: project_opened(project), refresh_requested(), notification({level,message})
- ProjectsViewModel
  - Commands: load_projects(), import_from_innergy(), save_project(data)
  - Events: projects_loaded(list), import_started(), import_progress(int), import_completed(int), notification({...})
- ProjectDetailsViewModel
  - Commands: set_active_project(project), load_details(), load_products_from_innergy_if_needed(), save_products_changes()
  - Events: project_loaded(project), products_loaded(list[dict]), notification({...})
- WorkspaceViewModel
  - Commands: set_active_project(project), load(), save_changes(changes)
  - Events: state_changed(state), notification({...})
- ExportViewModel (if applicable)
  - Commands: set_active_project(project), export(...)
  - Events: export_started(), export_progress(int), export_completed(result), notification({...})

### 3) Composition root changes (DI only; no UI imports)
- core/composition_root.py
  - Ensure builders exist for: build_main_window_view_model, build_projects_view_model, build_project_details_view_model, build_workspace_view_model, build_attributes_view_model, build_export_view_model.
  - Inject Services and Repositories into VMs. No controller imports anywhere.
  - Introduce an env flag USE_MVVM_ONLY (default True). If False, legacy path could be kept for backout, but target is removal.
- core/app_factory.py
  - Remove import of controllers.main_window_controller.MainWindowController.
  - Rely on composition root to provide VMs. Views should be instantiated in views/main_window.py (already happening) and wired to VMs.

### 4) View wiring changes (replace controller wiring with VM bindings)
- views/main_window.py
  - Keep existing MVVM wiring; ensure no controller usage remains.
  - ProjectsTab
    - Add set_view_model(vm) and wire:
      - import_button.clicked → vm.import_from_innergy
      - vm.projects_loaded → self.display_projects
      - Progress UI:
        - vm.import_started → show QProgressDialog("Importing projects from Innergy...")
        - vm.import_progress(int) → progress.setValue(int)
        - vm.import_completed(count) → progress.close(); QMessageBox.information(...)
      - vm.notification → map to QMessageBox by level
    - open_project_signal continues to flow to MainWindowViewModel.set_active_project
  - ProjectsDetailView already binds to ProjectDetailsViewModel for products load/save; keep enabling/disabling Save Changes via vm.products_loaded.
  - WorkspaceTab, AttributesTab, ExportTab: expose set_view_model(vm) and subscribe to state/notifications; replace any direct DataManager calls with VM commands.

### 5) Services
- Add or ensure services wrap DataManager or repositories cleanly:
  - ProjectBootstrapService: ensure_project_db, ingest_project_details_if_needed, load_enriched_project
  - ProjectsService: get_all_projects, sync_projects_from_innergy(progress_cb), save_project, load_enriched_project
  - ProductsService: fetch_products_from_innergy(project_number), get_products_from_db(project_id), replace_products_for_project(project_id, products)
  - WorkspaceService/AttributesService/ExportService as needed (IO only; no UI logic).

### 6) Tests migration plan
- Remove or skip tests/test_controllers/*.
  - Option A: delete folder; Option B: add pytest.ini ignore pattern.
- Add unit tests for new/updated VMs (mock services):
  - ProjectsViewModel: load_projects, import_from_innergy event sequence, save_project notifications
  - ProjectDetailsViewModel: load_details bootstrap flow, load_products_from_innergy_if_needed compares and stages, save_products_changes persists and reloads
  - WorkspaceViewModel/ExportViewModel: state transitions and notifications
- Keep Views tests shallow (rendering and wiring) using QtBot.
- Add a static guard (optional) to ensure no views/* import services/* or repositories/*.

### 7) Deletion checklist (final sweep)
- Delete files:
  - controllers/main_window_controller.py
  - controllers/projects_controller.py
  - controllers/workspace_controller.py
  - controllers/export_controller.py
  - controllers/legacy_vm_bridge.py
- Remove all imports/usages of controllers in runtime code (search: "controllers.")
- Update README/docs to reflect MVVM-only architecture.
- Ensure composition_root and views startup without controllers.
- Remove tests/test_controllers or exclude via pytest.ini.

### 8) Staged rollout and backout
- Feature flag: USE_MVVM_ONLY = True by default.
  - If regressions are found during rollout, temporarily set to False to re-enable hybrid path (if kept). The end goal is to delete controllers and remove flag.
- Keep telemetry/logging around import/export flows to monitor regressions.

### 9) Acceptance criteria (definition of done)
- No imports from controllers/* in application runtime.
- All previously controller-backed features operate via VMs:
  - Project list load/import/save, project open and details load, products load/save, workspace tree load/save, export flows.
- Views do not import DataManager/Service/Repository directly; only VMs.
- ViewModels have unit tests covering success/error paths. Views wiring tests pass.
- tests/test_controllers removed or disabled; CI green.

### 10) Execution cookbook (per file)
- views/main_window.py
  - Ensure VM builders are called; wire tabs to respective VMs; remove any DataManager usage.
- views/projects/projects_tab.py
  - Implement set_view_model(); wire import button and VM events for progress and notifications; keep open_project_signal → MainWindowViewModel.
- viewmodels/projects_view_model.py
  - Add import_from_innergy() with progress and notifications; add load_projects(), save_project().
- viewmodels/project_details_view_model.py
  - Already handles products; ensure notifications are bubbled to the view; keep compare normalization.
- viewmodels/workspace_view_model.py and export_view_model.py
  - Implement minimal evented state machines with load/save/export.
- services/*
  - Provide thin wrappers around DataManager/repositories; accept optional progress callbacks for long-running ops.
- core/app_factory.py + core/composition_root.py
  - Remove controller creation; expose VM builders only.
- tests/*
  - Delete controllers tests; add VM tests; keep/adjust view tests.

---
