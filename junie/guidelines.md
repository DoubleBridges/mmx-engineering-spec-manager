### Architectural Standard: MVVM (Model–View–ViewModel)
- View (`View`): UI only. Declares widgets, binds to a ViewModel, forwards user intents, renders state. No business logic, no I/O, no database calls.
- ViewModel (`VM`): State holder and UI-facing logic. Transforms domain data to view state, exposes commands/intents, orchestrates use cases/services. No UI toolkit types should leak out of the ViewModel.
- Model (`Model`): Domain entities and pure business rules. Ideally framework-agnostic, serializable, and unit-testable.
- Services/Use Cases/Repositories: Imperative operations, I/O, and integrations (DB, network, filesystem). Injected into ViewModels.

### Directory and Naming Conventions
- `mmx_engineering_spec_manager/models/` → domain models, value objects, DTOs
- `mmx_engineering_spec_manager/viewmodels/` → one `*ViewModel` per screen/region
- `mmx_engineering_spec_manager/views/` → UI components (e.g., PyQt, Tkinter, or framework-specific)
- `mmx_engineering_spec_manager/services/` → stateless services, use cases, gateways
- `mmx_engineering_spec_manager/repositories/` → persistence boundaries
- `mmx_engineering_spec_manager/core/` → shared utilities, `result` types, event bus, DI setup
- Names:
  - Views end with `View` or `*Tab` (e.g., `MainWindowView`, `WorkspaceTab`)
  - ViewModels end with `ViewModel` (e.g., `MainWindowViewModel`)
  - Tests mirror structure: `tests/test_viewmodels/test_main_window_view_model.py`

### Communication and Data Flow
- Views bind to ViewModels:
  - Views subscribe to `view_state` changes (signals/observables or callbacks).
  - Views forward user events to ViewModel commands (`on_save_clicked()` → `vm.save_changes()`).
- ViewModels depend only on Models + Services/Repositories.
- Services perform I/O and return domain results to ViewModels.
- No View depends on Service/Repository directly.

### Allowed Dependencies
- View → ViewModel (allowed)
- ViewModel → Model/Service/Repository (allowed)
- Service → Repository (allowed)
- Model → nothing framework-specific (keep pure)
- View ←X→ Service/Repository (forbidden)
- ViewModel ←X→ View toolkit types in public API (forbidden)

### ViewModel Interface Pattern (Python-friendly)
Expose:
- Immutable-ish `view_state` object (dataclass or pydantic model)
- Methods for user intents (commands)
- Events/Signals for one-off notifications (toasts, dialogs)

Example:
```python
from dataclasses import dataclass
from typing import Callable, Optional, List

@dataclass(frozen=True)
class WorkspaceViewState:
    is_loading: bool
    nodes: List[str]
    error: Optional[str] = None

class WorkspaceViewModel:
    def __init__(self, spec_service, on_state: Callable[[WorkspaceViewState], None], on_notify: Callable[[str], None]):
        self._service = spec_service
        self._on_state = on_state
        self._on_notify = on_notify
        self._state = WorkspaceViewState(is_loading=False, nodes=[])

    @property
    def state(self) -> WorkspaceViewState:
        return self._state

    def load(self) -> None:
        self._emit(self._state.__class__(is_loading=True, nodes=self._state.nodes))
        try:
            nodes = self._service.fetch_nodes()
            self._emit(WorkspaceViewState(is_loading=False, nodes=nodes))
        except Exception as ex:
            self._emit(WorkspaceViewState(is_loading=False, nodes=[], error=str(ex)))

    def save_changes(self, changes) -> None:
        try:
            self._service.save(changes)
            self._on_notify("Changes saved")
        except Exception as ex:
            self._on_notify(f"Save failed: {ex}")

    def _emit(self, new_state: WorkspaceViewState) -> None:
        self._state = new_state
        self._on_state(new_state)
```

### View Binding Pattern
- The View constructs a ViewModel (or receives it via DI), subscribes to state changes, and updates widgets accordingly.
- The View wires UI events to ViewModel commands.

Example (pseudo-PyQt):
```python
class WorkspaceTab(QWidget):
    def __init__(self, vm: WorkspaceViewModel):
        super().__init__()
        self.vm = vm
        self.tree = QTreeView()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(lambda: self.vm.save_changes(self._collect_changes()))
        vm._on_state = self._render  # if not using signal/slot, set callback
        vm._on_notify = self._notify

    def showEvent(self, e):
        self.vm.load()

    def _render(self, state: WorkspaceViewState):
        self.save_btn.setEnabled(not state.is_loading)
        self.tree.setModel(self._to_model(state.nodes))
        if state.error:
            self._notify(state.error)

    def _notify(self, msg: str):
        QMessageBox.information(self, "Info", msg)
```

### Services/Repositories Pattern
- Services implement application use cases and depend on repositories.
- Repositories encapsulate storage details (DB, files, network).

```python
class SpecService:
    def __init__(self, repo):
        self._repo = repo

    def fetch_nodes(self):
        return self._repo.get_all_nodes()

    def save(self, changes):
        return self._repo.apply(changes)
```

### Dependency Injection (DI)
- Instantiate and wire dependencies at composition root (e.g., app startup):
```python
# composition_root.py
repo = FileRepo(path=...)
service = SpecService(repo)
workspace_vm = WorkspaceViewModel(service, on_state=lambda s: None, on_notify=lambda m: None)
workspace_view = WorkspaceTab(workspace_vm)
```
- ViewModels receive all dependencies via constructor injection, not via globals/singletons.

### Testing Policy
- ViewModel tests: pure unit tests with fake services/repos. No UI framework imports.
- Service tests: can hit filesystem/network only if marked as integration; otherwise mock.
- View tests: shallow tests verifying rendering given a `view_state` and event wiring to VM commands.

### Do/Don’t Summary
Do:
- Keep Views dumb; update UI only.
- Keep ViewModels free of UI toolkit objects in public API.
- Use immutable `view_state` snapshots to render.
- Isolate I/O in Services/Repositories.
- Prefer pure functions in Models.

Don’t:
- Put business logic in Views.
- Call Services/Repositories from Views.
- Access global application state from ViewModels.
- Let Errors/exceptions leak into Views without mapping to user-friendly notifications/state.

### Migration Guidance (from MVC/MVP/Controller)
- Replace `*Controller` with `*ViewModel` classes.
- Move: event handling and business logic from `views/*` and `controllers/*` into `viewmodels/*`.
- Keep `views/*` focused on binding and rendering.
- If a controller currently holds I/O or orchestration, split it into `Service` and `ViewModel` parts.
- Create a transitional adapter if needed: View → Adapter → ViewModel.

### File-Level Rules Junie Should Enforce
- New UI elements must have a matching ViewModel or extend an existing one; reject PRs that put logic in Views.
- Any method in `views/*` that does computation/business rules should be flagged and suggested to move to the corresponding ViewModel.
- Any direct import in `views/*` from `services/*` or `repositories/*` is forbidden.
- Any `print` or logging of domain events in Views should be replaced with ViewModel notifications.
- Public ViewModel API must use domain types, not UI toolkit types (e.g., no `QModelIndex` in signatures). Map in the View.

### PR Review Checklist (copy into PR template)
- Does each View have a ViewModel?
- Are all user intents handled by the ViewModel?
- Is UI state represented by a serializable `view_state`?
- Do Services/Repositories handle I/O exclusively?
- Are dependencies injected (no globals)?
- Are there unit tests for the ViewModel covering happy/error paths?
- Are Views thin and free of business logic?

### How Junie Should Act When Generating or Modifying Code
- Prefer creating `viewmodels/*` first, then `views/*` bind to them.
- If asked to add a feature to a View, propose/introduce corresponding ViewModel changes.
- When encountering direct service calls in Views, recommend refactoring into ViewModel and provide a patch plan.
- Default scaffolding for a new screen:
  - `viewmodels/<screen>_view_model.py` with `ViewState`, commands, and events
  - `views/<screen>_view.py` binding UI to VM
  - `services/<screen>_service.py` if new use cases exist
  - tests in `tests/test_viewmodels/test_<screen>_view_model.py`

### Example Anti-Patterns and Fixes
- Anti-pattern: `MainWindowView` calls `SpecService.save()` directly.
  - Fix: add `MainWindowViewModel.save_changes()` that calls the service; View calls VM only.
- Anti-pattern: ViewModel method signature uses `QTreeWidgetItem`.
  - Fix: map `QTreeWidgetItem` → domain DTO in View before calling VM.
- Anti-pattern: State spread across View widgets.
  - Fix: single source of truth in `view_state`; widgets read from it.

### Error Handling & Results
- Services return `Result[T, E]` or raise exceptions that ViewModels catch and convert into `view_state.error` or ephemeral notifications.
- No exception-handling logic in Views beyond presenting a message.

### Concurrency/Async
- If async is used, keep it in Service layer or inside ViewModel orchestration.
- Views should await only ViewModel commands or subscribe to state changes; they shouldn’t own background tasks.

### Telemetry/Logging
- Log in Services/ViewModels; Views forward user actions but do not log business events.

### Minimum Example Layout
```
mmx_engineering_spec_manager/
  models/
  viewmodels/
    main_window_view_model.py
    workspace_view_model.py
  views/
    main_window.py        # UI only
    workspace/workspace_tab.py
  services/
  repositories/
  core/
    composition_root.py
```

### Notes Specific to This Codebase
- Where `controllers/*` exist (e.g., `main_window_controller.py`), plan to migrate logic into `viewmodels/*` and delete controllers after feature parity.
- Existing tests in `tests/test_views/*` should be complemented with `tests/test_viewmodels/*` to cover logic extracted from views.

### Versioning This Guideline
- Any deviation from these rules must be recorded in this file with justification.
- Keep Junie aligned by referencing this file explicitly in tasks and PRs.