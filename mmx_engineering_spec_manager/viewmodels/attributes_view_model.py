from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List, Callable

# Utilities and constants (kept outside of Views per MVVM guidelines)
try:  # pragma: no cover - import resilience for tests
    from mmx_engineering_spec_manager.utilities import callout_import, kv_import
except Exception:  # pragma: no cover
    callout_import, kv_import = None, None  # type: ignore

try:  # pragma: no cover - import resilience
    from mmx_engineering_spec_manager.data_manager.manager import DataManager
except Exception:  # pragma: no cover
    DataManager = Any  # type: ignore


class Event:
    def __init__(self) -> None:
        self._subs: List[Callable[..., None]] = []

    def subscribe(self, cb: Callable[..., None]) -> None:
        if cb not in self._subs:
            self._subs.append(cb)

    def emit(self, *args: Any, **kwargs: Any) -> None:
        for cb in list(self._subs):
            try:
                cb(*args, **kwargs)
            except Exception:
                pass


@dataclass
class AttributesViewState:
    active_project_id: Optional[int] = None
    grouped_callouts: Dict[str, List[Dict[str, str]]] = field(default_factory=dict)
    error: Optional[str] = None
    status: str = ""


class AttributesViewModel:
    """Holds Attributes domain state and orchestrates I/O and parsing.

    No UI framework types, returns plain dict/list payloads.
    """

    def __init__(self, data_manager: DataManager | None = None) -> None:
        self.view_state = AttributesViewState()
        self._dm = data_manager
        # Events for the View to subscribe to (optional in transitional phase)
        self.callouts_loaded = Event()
        self.notification = Event()

    def set_active_project(self, project: Any) -> None:
        self.view_state.active_project_id = getattr(project, "id", None)

    # ---- Commands ----
    def load_callouts_for_active_project(self) -> Dict[str, List[Dict[str, str]]]:
        pid = self.view_state.active_project_id
        if not pid or not self._dm:
            return {}
        try:
            grouped = self._dm.get_callouts_for_project(pid) or {}
            # Normalize to list[dict[str,str]]
            norm: Dict[str, List[Dict[str, str]]] = {}
            for tab, items in (grouped.items() if isinstance(grouped, dict) else []):
                rows: List[Dict[str, str]] = []
                for d in items or []:
                    if isinstance(d, dict):
                        rows.append({
                            "Type": str(d.get("Type", "")),
                            "Name": str(d.get("Name", "")),
                            "Tag": str(d.get("Tag", "")),
                            "Description": str(d.get("Description", "")),
                        })
                norm[str(tab)] = rows
            self.view_state.grouped_callouts = norm
            self.callouts_loaded.emit(norm)
            return norm
        except Exception as e:  # pragma: no cover
            self._set_error(str(e))
            return {}

    def parse_callouts_from_path(self, file_type: str, path: str) -> Dict[str, List[Dict[str, str]]]:
        grouped: Dict[str, List[Dict[str, str]]] = {}
        try:
            if callout_import is not None:
                dtos = callout_import.read_callouts(file_type, path)
                if dtos:
                    grouped_dto = callout_import.group_callouts(dtos)
                    for tab, items in grouped_dto.items():
                        rows = [
                            {"Type": getattr(d, "type", ""), "Name": getattr(d, "name", ""),
                             "Tag": getattr(d, "tag", ""), "Description": getattr(d, "description", "")}
                            for d in (items or [])
                        ]
                        grouped[str(tab)] = rows
                    self.view_state.grouped_callouts = grouped
                    self.callouts_loaded.emit(grouped)
                    return grouped
            # Fallback generic read (for legacy generic table use)
            if kv_import is not None:
                rows_any = kv_import.read_any(path)
                # Expose under a special key if needed by callers
                grouped["Generic"] = list(rows_any) if isinstance(rows_any, list) else []
        except Exception as e:  # pragma: no cover
            self._set_error(str(e))
        return grouped

    def save_callouts_for_active_project(self, rows: List[Dict[str, str]]) -> bool:
        pid = self.view_state.active_project_id
        if not pid or not self._dm:
            return False
        # Map rows to DTOs via callout_import utilities, skipping incomplete rows
        try:
            dtos = []
            TYPE_UNC = getattr(callout_import, "TYPE_UNCATEGORIZED", "Uncategorized") if callout_import else "Uncategorized"
            for r in rows:
                t = (r.get("Type") or "").strip() or TYPE_UNC
                name = (r.get("Name") or "").strip()
                tag = (r.get("Tag") or "").strip()
                desc = (r.get("Description") or "").strip()
                if not name or not tag or not desc:
                    continue
                dto = callout_import._mk_dto(name, tag, desc) if callout_import else {"type": t, "name": name, "tag": tag, "description": desc}
                # Preserve explicit user-assigned Type in Uncategorized by overriding categorization
                try:
                    if callout_import and t and getattr(dto, "type", None) != t:
                        dto.type = t  # type: ignore[attr-defined]
                except Exception:
                    pass
                dtos.append(dto)
            grouped = callout_import.group_callouts(dtos) if callout_import else {}
            self._dm.replace_callouts_for_project(pid, grouped)
            return True
        except Exception as e:  # pragma: no cover
            self._set_error(str(e))
            return False

    # ---- Helpers ----
    def _set_error(self, message: str) -> None:
        self.view_state.error = message
        self.notification.emit({"level": "error", "message": message})
