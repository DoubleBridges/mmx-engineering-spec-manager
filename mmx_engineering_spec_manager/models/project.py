from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, List, Dict, Optional


@dataclass
class ProjectModel:
    """Pure domain Project model mirroring db_models.project.Project at a high level.

    Keeps only fields commonly used by Views/VMs and provides from_orm/to_dict helpers.
    Collections (locations/walls/products) are represented as simple dicts to avoid
    coupling to ORM classes.
    """
    id: Optional[int] = None
    number: str | None = None
    name: str | None = None
    job_description: str | None = None
    job_address: str | None = None  # optional; present in some schemas
    locations: List[Dict[str, Any]] = field(default_factory=list)
    walls: List[Dict[str, Any]] = field(default_factory=list)
    products: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_orm(cls, obj: Any) -> "ProjectModel":
        if obj is None:
            return cls()
        # Basic fields
        pid = getattr(obj, "id", None)
        number = getattr(obj, "number", None)
        name = getattr(obj, "name", None)
        job_description = getattr(obj, "job_description", None)
        job_address = getattr(obj, "job_address", None) if hasattr(obj, "job_address") else None
        # Shallow copy of related collections when present
        def to_dict_safe(o: Any) -> Dict[str, Any]:
            try:
                d = {}
                for k in ("id", "name", "material", "tag", "description", "width", "height", "depth",
                          "x_origin", "y_origin", "z_origin", "quantity", "item_number"):
                    if hasattr(o, k):
                        d[k] = getattr(o, k)
                return d
            except Exception:
                return {}
        locs = []
        try:
            for l in list(getattr(obj, "locations", []) or []):
                locs.append({k: getattr(l, k, None) for k in ("id", "name")})
        except Exception:
            locs = []
        walls = []
        try:
            for w in list(getattr(obj, "walls", []) or []):
                walls.append({k: getattr(w, k, None) for k in ("id", "link_id", "width", "height", "thicknesses")})
        except Exception:
            walls = []
        prods = []
        try:
            for p in list(getattr(obj, "products", []) or []):
                prods.append(to_dict_safe(p))
        except Exception:
            prods = []
        return cls(id=pid, number=number, name=name, job_description=job_description, job_address=job_address,
                   locations=locs, walls=walls, products=prods)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
