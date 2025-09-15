# PR Title

Briefly summarize the change in one sentence.

## Summary
- What does this change do and why?
- What user-visible behavior changes (if any)?
- Any follow-up tasks or out-of-scope notes?

## Type of change
- [ ] Feature
- [ ] Bug fix
- [ ] Refactor (no behavior change)
- [ ] Docs / CI / Chore

## Scope & Review Size
- Estimated changed lines (excluding generated files): ~___
- Affected files: ___
- Reviewer time: ~___ minutes
- [ ] PR is within the recommended slice size (150–400 lines, 1–5 files) from mvvm_refactor_plan.md

## Tests
- [ ] New unit tests added or existing tests updated for moved logic
- [ ] All tests pass locally (or explain)
- [ ] Manual smoke verified affected UI paths (if applicable)

## MVVM Quality Checklist
Follow junie/guidelines.md and the mvvm_refactor_plan acceptance criteria.

Views
- [ ] Views contain UI-only logic (rendering/event wiring). No I/O or business rules.
- [ ] No direct imports of services/* or repositories/* within mmx_engineering_spec_manager/views/* (forbidden dependency).
- [ ] No direct DataManager usage in views (temporary transitional adapters allowed only if already present).

ViewModels
- [ ] Public API exposes only serializable view_state, commands, and notifications.
- [ ] No UI toolkit types (e.g., PySide6) in any ViewModel public API or state.
- [ ] ViewModels orchestrate through Services; no direct I/O.

Services/Repositories
- [ ] All I/O and use-case orchestration happen in services/* (and repositories/*), not in views.
- [ ] Services return simple domain/DTO types or Result wrappers.

Composition Root / DI
- [ ] Dependencies are constructed in core/composition_root.py (or app_factory for UI assembly). No UI imports inside composition_root.
- [ ] ViewModels are created with dependencies via constructor injection; no globals.

Transitional Adapters
- [ ] If legacy controllers or adapters are still used, they are thin and clearly marked as transitional.

Change Safety
- [ ] Backward compatibility maintained where required (signals, adapters).
- [ ] Rollback plan noted below if risk > low.

## Screenshots / Demos (if UI)
Attach before/after screenshots or short demo GIF where relevant.

## Risk & Rollback Plan
- Risk level: Low / Medium / High
- Rollback steps if needed:

## Related Issues / Docs
- Plan: junie/mvvm_refactor_plan.md
- Guidelines: junie/guidelines.md
- Related issues/links: 
