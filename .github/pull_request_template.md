## Summary

Describe the changes and the problem they solve.

## Checklist (MVVM Quality Gates)

- [ ] Views contain UI-only logic (no I/O, no business rules)
- [ ] No files under mmx_engineering_spec_manager/views import from:
  - mmx_engineering_spec_manager/services/*
  - mmx_engineering_spec_manager/repositories/*
  - mmx_engineering_spec_manager/data_manager/*
- [ ] Composition root (core/composition_root.py) builds Services and ViewModels; Views obtain VMs via builders
- [ ] ViewModels expose serializable state + events (no UI toolkit types in public API)
- [ ] Services/Repositories own I/O and are injected into ViewModels
- [ ] Tests updated/added:
  - [ ] ViewModel unit tests (happy/error paths)
  - [ ] Static guard passes: tests/test_quality/test_views_no_service_repo_imports.py
- [ ] No runtime imports from controllers/* (controllers sunset complete)

## Testing

Describe how you tested the changes locally (commands, screenshots, etc.).

## Related Issues

Link related issues/PRs.
