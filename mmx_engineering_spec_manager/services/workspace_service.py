from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    # Prefer the shared Result used across services
    from .project_bootstrap_service import Result  # type: ignore
except Exception:  # pragma: no cover - fallback tiny Result for isolation
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


@dataclass
class WorkspaceNode:
    """Lightweight, UI-agnostic tree node DTO for the Workspace hierarchy.

    type: one of {"project","location","wall","product"}
    label: human-readable text (e.g., project number/name, location name)
    children: nested nodes
    """
    id: Any
    type: str
    label: str
    children: List["WorkspaceNode"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "children": [c.to_dict() for c in (self.children or [])],
        }


class WorkspaceService:
    """Service for Workspace domain use-cases.

    Responsibilities (initial scaffolding for Phase 3, Step 1):
    - Provide a UI-agnostic API to load a project "tree" suitable for presentation.
    - Provide a placeholder API to persist workspace changes (to be implemented in later steps).

    This service intentionally avoids importing any UI toolkit. It wraps DataManager
    reads/writes and exposes simple dict-based DTOs.
    """

    def __init__(self, data_manager: Any) -> None:
        self._dm = data_manager

    def load_project_tree(self, project_id: int) -> Dict[str, Any]:
        """Load a hierarchical representation of a project's workspace elements.

        Returns a dict representing the root node with nested children. The shape is:
        {
            "id": <project_id>,
            "type": "project",
            "label": "<number> - <name>",
            "children": [
                {"id": <location_id>, "type": "location", "label": <name>, "children": [
                    {"id": <wall_id>, "type": "wall", "label": <wall label>, "children": [
                        {"id": <product_id>, "type": "product", "label": <name>, "children": []}, ...
                    ]}, ...
                ]}, ...
            ]
        }

        Notes:
        - This is a best-effort mapping from available ORM objects; fields may be missing
          depending on the dataset. The service is defensive and produces an empty tree on
          failures.
        """
        try:
            project = None
            try:
                project = self._dm.get_full_project_from_project_db(int(project_id))
            except Exception:
                project = None
            if project is None:
                root = WorkspaceNode(id=project_id, type="project", label=f"Project {project_id}", children=[])
                return root.to_dict()

            # Project label
            number = getattr(project, "number", None) or ""
            name = getattr(project, "name", None) or ""
            proj_label = (f"{number} - {name}").strip(" -") or (name or number or f"Project {project_id}")
            root = WorkspaceNode(id=getattr(project, "id", project_id), type="project", label=proj_label, children=[])

            # Locations (if present)
            locations = list(getattr(project, "locations", []) or [])
            loc_nodes: List[WorkspaceNode] = []
            for loc in locations:
                loc_id = getattr(loc, "id", None)
                loc_name = getattr(loc, "name", None) or ""
                loc_node = WorkspaceNode(id=loc_id if loc_id is not None else f"loc-{loc_name}", type="location", label=str(loc_name), children=[])
                # Walls under this location, if relationship exists
                walls = []
                try:
                    walls = list(getattr(loc, "walls", []) or [])
                except Exception:
                    # Some schemas may relate walls via project only; fall back below
                    walls = []
                for w in walls:
                    wid = getattr(w, "id", None)
                    wlabel = self._format_wall_label(w)
                    wall_node = WorkspaceNode(id=wid if wid is not None else f"wall-{wlabel}", type="wall", label=wlabel, children=[])
                    # Products under wall
                    for p in list(getattr(w, "products", []) or []):
                        pid = getattr(p, "id", None)
                        pname = getattr(p, "name", None) or getattr(p, "material", None) or "Product"
                        wall_node.children.append(WorkspaceNode(id=pid if pid is not None else f"prod-{pname}", type="product", label=str(pname), children=[]))
                    loc_node.children.append(wall_node)
                loc_nodes.append(loc_node)

            # If no walls discovered under locations, try project-level walls
            if not any(n.children for n in loc_nodes):
                for w in list(getattr(project, "walls", []) or []):
                    wid = getattr(w, "id", None)
                    wlabel = self._format_wall_label(w)
                    wall_node = WorkspaceNode(id=wid if wid is not None else f"wall-{wlabel}", type="wall", label=wlabel, children=[])
                    for p in list(getattr(w, "products", []) or []):
                        pid = getattr(p, "id", None)
                        pname = getattr(p, "name", None) or getattr(p, "material", None) or "Product"
                        wall_node.children.append(WorkspaceNode(id=pid if pid is not None else f"prod-{pname}", type="product", label=str(pname), children=[]))
                    # Attach to a synthetic location bucket
                    loc_label = getattr(getattr(w, "location", None), "name", None) or ""
                    bucket_label = loc_label or ""
                    bucket_id = f"loc-{bucket_label or 'unknown'}"
                    # Find/create bucket
                    bucket = next((n for n in loc_nodes if n.label == bucket_label), None)
                    if bucket is None:
                        bucket = WorkspaceNode(id=bucket_id, type="location", label=bucket_label, children=[])
                        loc_nodes.append(bucket)
                    bucket.children.append(wall_node)

            root.children = loc_nodes
            return root.to_dict()
        except Exception:
            # Defensive default
            return WorkspaceNode(id=project_id, type="project", label=f"Project {project_id}", children=[]).to_dict()

    def save_changes(self, changes: Dict[str, Any] | List[Dict[str, Any]] | None) -> Result:
        """Persist workspace changes.

        Initial scaffolding returns success without applying changes. In later steps,
        this will delegate to DataManager/Repositories to upsert walls, products,
        and geometry changes captured by the ViewModel.
        """
        try:
            # Placeholder no-op for Phase 3, Step 1
            _ = changes  # satisfy linters
            return Result.ok_value(None)
        except Exception as e:
            return Result.fail(str(e))

    @staticmethod
    def _format_wall_label(w: Any) -> str:
        """Create a human-friendly wall label from available fields."""
        try:
            nm = getattr(w, "link_id", None) or getattr(w, "id", None)
            width = getattr(w, "width", None)
            height = getattr(w, "height", None)
            if width and height:
                return f"Wall {nm} ({width}x{height})"
            if width:
                return f"Wall {nm} ({width})"
            return f"Wall {nm}"
        except Exception:
            return "Wall"