
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
