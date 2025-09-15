import ast
import os
from pathlib import Path

# Root of the project repository (this test file is under tests/)
REPO_ROOT = Path(__file__).resolve().parents[2]
VIEWS_DIR = REPO_ROOT / "mmx_engineering_spec_manager" / "views"

FORBIDDEN_PREFIXES = (
    "mmx_engineering_spec_manager.services",
    "mmx_engineering_spec_manager.repositories",
    "mmx_engineering_spec_manager.data_manager",
)

ALLOWED_EXCEPTIONS = set(
    [
        # Composition root is allowed in Views to obtain VMs
        "mmx_engineering_spec_manager.core.composition_root",
        # Utilities and other UI-safe modules
        "mmx_engineering_spec_manager.utilities",
    ]
)


def _iter_view_py_files():
    for root, _dirs, files in os.walk(VIEWS_DIR):
        for f in files:
            if f.endswith(".py"):
                yield Path(root) / f


def _is_forbidden_module(mod_name: str | None) -> bool:
    if not mod_name:
        return False
    # Allow explicit exceptions
    for allowed in ALLOWED_EXCEPTIONS:
        if mod_name == allowed or mod_name.startswith(allowed + "."):
            return False
    return mod_name.startswith(FORBIDDEN_PREFIXES)


def test_views_do_not_import_services_repositories_or_data_manager():
    """
    MVVM guard: Views must not import from services/*, repositories/*, or data_manager/*.
    This static test parses imports in mmx_engineering_spec_manager/views and fails on forbidden imports.
    """
    offenders: list[tuple[str, int, str]] = []  # (file, line, module)
    for py in _iter_view_py_files():
        src = py.read_text(encoding="utf-8")
        try:
            tree = ast.parse(src, filename=str(py))
        except SyntaxError:
            # Skip files that may depend on unavailable optional deps in test env
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    if _is_forbidden_module(name):
                        offenders.append((str(py), node.lineno, name))
            elif isinstance(node, ast.ImportFrom):
                mod = node.module
                if _is_forbidden_module(mod):
                    offenders.append((str(py), node.lineno, mod or ""))
    if offenders:
        msg_lines = [
            "Forbidden imports found in Views (violates MVVM: Views must not import services/repositories/data_manager):",
        ]
        for file, lineno, mod in offenders:
            msg_lines.append(f" - {file}:{lineno} imports from '{mod}'")
        msg_lines.append(
            "Allowed: import composition_root builders in views to obtain ViewModels."
        )
        raise AssertionError("\n".join(msg_lines))
