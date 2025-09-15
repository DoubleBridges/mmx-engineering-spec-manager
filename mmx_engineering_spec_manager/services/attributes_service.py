from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:  # Prefer shared Result type used by other services
    from .project_bootstrap_service import Result  # type: ignore
except Exception:  # pragma: no cover - fallback tiny Result to avoid import issues in isolation
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


class AttributesService:
    """Service for Attributes domain use-cases (callouts and Location Tables).

    Responsibility:
    - Provide a stable, UI-agnostic API for loading/saving callouts and
      location-table callouts for a specific project.
    - Wrap DataManager operations and normalize data shapes to simple dicts
      so ViewModels can depend on domain-only types.
    """

    def __init__(self, data_manager: Any) -> None:
        self._dm = data_manager

    # --- Callouts ---
    def load_callouts(self, project_id: int) -> Dict[str, List[Dict[str, str]]]:
        """Load grouped callouts for the project.

        Returns a dict with keys: "Finishes", "Hardware", "Sinks",
        "Appliances", "Uncategorized". Each value is a list of rows with
        keys: Type, Name, Tag, Description (all strings).
        """
        try:
            grouped = self._dm.get_callouts_for_project(project_id) or {}
        except Exception:
            return {}
        # Normalize to expected shape (dict of list of dict[str,str])
        out: Dict[str, List[Dict[str, str]]] = {}
        for tab, items in (grouped or {}).items():
            rows: List[Dict[str, str]] = []
            for d in (items or []):
                if isinstance(d, dict):
                    rows.append({
                        "Type": str(d.get("Type", "") or ""),
                        "Name": str(d.get("Name", "") or ""),
                        "Tag": str(d.get("Tag", "") or ""),
                        "Description": str(d.get("Description", "") or ""),
                    })
                else:
                    # DTO-like object with attributes
                    rows.append({
                        "Type": str(getattr(d, "type", "") or ""),
                        "Name": str(getattr(d, "name", "") or ""),
                        "Tag": str(getattr(d, "tag", "") or ""),
                        "Description": str(getattr(d, "description", "") or ""),
                    })
            out[str(tab)] = rows
        # Ensure all expected categories exist (even if empty)
        for key in ("Finishes", "Hardware", "Sinks", "Appliances", "Uncategorized"):
            out.setdefault(key, [])
        return out

    def save_callouts(self, project_id: int, rows_or_grouped: Dict[str, List[Dict[str, str]]] | List[Dict[str, str]]) -> Result:
        """Replace callouts for the project.

        Accepts either:
          - a grouped mapping category -> list[rows], or
          - a flat list of rows (which will be grouped by the "Type" key)
        """
        # Group if a flat list is provided
        try:
            if isinstance(rows_or_grouped, list):
                grouped: Dict[str, List[Dict[str, str]]] = {}
                for r in rows_or_grouped:
                    t = str((r or {}).get("Type", "") or "")
                    grouped.setdefault(t, []).append(r or {})
            else:
                grouped = rows_or_grouped or {}
            # Map from Type value to DataManager group keys
            # UI/VM use friendly Type labels identical to dm.get_callouts_for_project keys
            normalized: Dict[str, List[Dict[str, str]]] = {
                "Finishes": list(grouped.get("Finishes", []) or []),
                "Hardware": list(grouped.get("Hardware", []) or []),
                "Sinks": list(grouped.get("Sinks", []) or []),
                "Appliances": list(grouped.get("Appliances", []) or []),
                "Uncategorized": list(grouped.get("Uncategorized", []) or []),
            }
            # Delegate to DataManager
            self._dm.replace_callouts_for_project(project_id, normalized)
            return Result.ok_value(None)
        except Exception as e:
            return Result.fail(str(e))

    # --- Location tables ---
    def load_locations_and_tables(self, project_id: int) -> Dict[str, List[Dict[str, str]]]:
        """Return mapping of location_name -> list of rows with keys: Type, Tag, Description."""
        try:
            mapping = self._dm.get_location_tables_for_project(project_id) or {}
        except Exception:
            return {}
        out: Dict[str, List[Dict[str, str]]] = {}
        for name, rows in (mapping or {}).items():
            norm_rows: List[Dict[str, str]] = []
            for r in (rows or []):
                if isinstance(r, dict):
                    norm_rows.append({
                        "Type": str(r.get("Type", "") or ""),
                        "Tag": str(r.get("Tag", "") or ""),
                        "Description": str(r.get("Description", "") or ""),
                    })
                else:
                    norm_rows.append({
                        "Type": str(getattr(r, "type", "") or ""),
                        "Tag": str(getattr(r, "tag", "") or ""),
                        "Description": str(getattr(r, "description", "") or ""),
                    })
            out[str(name or "")] = norm_rows
        return out

    def save_location_tables(self, project_id: int, mapping: Dict[str, List[Dict[str, str]]] | None) -> Result:
        """Replace location-table callouts for the project.

        Mapping is location_name -> list of rows with keys: Type, Tag, Description.
        """
        try:
            ok = self._dm.replace_location_tables_for_project(project_id, mapping or {})
            # DataManager returns bool; treat False as failure with generic message
            if ok is False:
                return Result.fail("replace_location_tables_for_project returned False")
            return Result.ok_value(None)
        except Exception as e:
            return Result.fail(str(e))
