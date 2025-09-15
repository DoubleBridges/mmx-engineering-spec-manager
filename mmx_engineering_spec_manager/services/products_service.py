from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Optional

try:  # shared Result
    from .project_bootstrap_service import Result  # type: ignore
except Exception:  # pragma: no cover
    @dataclass
    class Result:  # type: ignore
        ok: bool
        value: Optional[Any] = None
        error: Optional[str] = None

        @classmethod
        def ok_value(cls, value: Any | None = None) -> "Result":
            return cls(ok=True, value=value, error=None)

        @classmethod
        def fail(cls, error: str) -> "Result":
            return cls(ok=False, value=None, error=error)


class ProductsService:
    """Service for product list persistence and Innergy fetch.

    This service wraps DataManager product operations and provides a UI-agnostic API.
    """

    def __init__(self, data_manager: Any) -> None:
        self._dm = data_manager

    # --- Reads ---
    def get_products_from_db(self, project_id: int) -> List[dict]:
        try:
            return list(self._dm.get_products_for_project_from_project_db(int(project_id)) or [])
        except Exception:
            return []

    # --- Writes ---
    def replace_products_for_project(self, project_id: int, products: List[dict]) -> Result:
        try:
            ok = bool(self._dm.replace_products_for_project(int(project_id), list(products or [])))
            if ok:
                return Result.ok_value(None)
            return Result.fail("replace_products_for_project returned False")
        except Exception as e:
            return Result.fail(str(e))

    # --- External fetch (Innergy) ---
    def fetch_products_from_innergy(self, project_number: str | int) -> List[dict]:
        try:
            return list(self._dm.fetch_products_from_innergy(str(project_number)) or [])
        except Exception:
            return []
