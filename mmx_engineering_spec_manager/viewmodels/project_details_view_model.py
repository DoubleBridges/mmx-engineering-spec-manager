from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

try:  # pragma: no cover - import resilience
    from mmx_engineering_spec_manager.services import ProjectBootstrapService
    from mmx_engineering_spec_manager.services import ProjectsService
    from mmx_engineering_spec_manager.services import ProductsService
    from mmx_engineering_spec_manager.services import Result
except Exception:  # pragma: no cover
    ProjectBootstrapService = Any  # type: ignore
    ProjectsService = Any  # type: ignore
    ProductsService = Any  # type: ignore
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


class Event:
    def __init__(self) -> None:
        self._subs: List[Callable[..., None]] = []
    def subscribe(self, cb: Callable[..., None]) -> None:
        if cb not in self._subs:
            self._subs.append(cb)
    def unsubscribe(self, cb: Callable[..., None]) -> None:
        if cb in self._subs:
            self._subs.remove(cb)
    def emit(self, *args: Any, **kwargs: Any) -> None:
        for cb in list(self._subs):
            try:
                cb(*args, **kwargs)
            except Exception:
                pass


@dataclass
class ProjectDetailsViewState:
    active_project_id: Optional[int] = None
    project: Any | None = None  # domain model or ORM-like object
    staged_products: List[Dict[str, Any]] = field(default_factory=list)
    is_loading: bool = False
    is_saving: bool = False
    error: Optional[str] = None
    status: str = ""


class ProjectDetailsViewModel:
    """ViewModel for Project Details screen.

    Responsibilities:
    - Ensure per-project DB exists and load enriched project, preferring DB data.
    - Load products from Innergy only when needed and stage changes before saving.
    - Save product changes to the per-project DB via service and refresh state.
    """

    def __init__(
        self,
        project_bootstrap_service: ProjectBootstrapService | None = None,
        projects_service: ProjectsService | None = None,
        products_service: ProductsService | None = None,
        data_manager: Any | None = None,  # transitional fallback
    ) -> None:
        self._bootstrap = project_bootstrap_service or (ProjectBootstrapService(data_manager) if data_manager is not None else None)
        self._projects = projects_service or (ProjectsService(data_manager) if data_manager is not None else None)
        self._products = products_service or (ProductsService(data_manager) if data_manager is not None else None)
        self.view_state = ProjectDetailsViewState()
        # Events
        self.project_loaded = Event()
        self.products_loaded = Event()
        self.notification = Event()

    # ---- Commands ----
    def set_active_project(self, project: Any) -> None:
        self.view_state.active_project_id = getattr(project, "id", None)
        # Prefer to keep the original object until enriched load completes
        self.view_state.project = project
        self.view_state.error = None
        self.view_state.status = ""

    def load_details(self) -> Any | None:
        """Ensure DB, skip unnecessary ingestion, and load enriched project into state."""
        pid = self.view_state.active_project_id
        proj = self.view_state.project
        if not pid or proj is None:
            return None
        self.view_state.is_loading = True
        try:
            # Ensure DB exists (non-fatal on failure)
            try:
                if self._bootstrap is not None:
                    _ = self._bootstrap.ensure_project_db(proj)
            except Exception:  # pragma: no cover
                pass
            # Attempt to load directly from DB first
            enriched: Any | None = None
            try:
                if self._bootstrap is not None:
                    res = self._bootstrap.load_enriched_project(proj)
                    if getattr(res, "ok", False):
                        enriched = getattr(res, "value", None)
                elif self._projects is not None:
                    res = self._projects.load_enriched_project(proj)
                    if getattr(res, "ok", False):
                        enriched = getattr(res, "value", None)
            except Exception:
                enriched = None
            if enriched is None:
                enriched = proj
            # If enriched equals original and we have bootstrap service, consider ingestion on first open
            try:
                # Decide via bootstrap (it checks DB existence and API key)
                if self._bootstrap is not None:
                    res_ing = self._bootstrap.ingest_project_details_if_needed(proj, None)
                    if not getattr(res_ing, "ok", False):
                        # Surfacing as warning; do not block
                        self._notify(f"Failed to load project details from Innergy: {getattr(res_ing, 'error', 'unknown error')}", level="warning")
                    # Reload enriched regardless
                    res2 = self._bootstrap.load_enriched_project(proj)
                    if getattr(res2, "ok", False) and getattr(res2, "value", None) is not None:
                        enriched = getattr(res2, "value", None)
            except Exception:  # pragma: no cover
                pass
            self.view_state.project = enriched
            self.project_loaded.emit(enriched)
            return enriched
        except Exception as e:  # pragma: no cover
            self._set_error(str(e))
            return None
        finally:
            self.view_state.is_loading = False

    def load_products_from_innergy_if_needed(self) -> List[Dict[str, Any]]:
        """Fetch products from Innergy, compare with DB, and stage changes if different.

        If there are no differences, emit an informational notification.
        """
        pid = self.view_state.active_project_id
        proj = self.view_state.project
        if not pid or proj is None or self._products is None:
            return []
        number = getattr(proj, "number", None)
        if not number:
            return []
        try:
            fetched = self._products.fetch_products_from_innergy(number) or []
        except Exception:
            fetched = []
        try:
            current_db = self._products.get_products_from_db(int(pid)) or []
        except Exception:
            current_db = []
        if self._normalize_products_for_compare(fetched) == self._normalize_products_for_compare(current_db):
            self._notify("No changes were discovered.")
            # Clear staged products
            self.view_state.staged_products = []
            self.products_loaded.emit([])
            return []
        # Stage products and notify view
        staged = list(fetched or [])
        self.view_state.staged_products = staged
        self.products_loaded.emit(staged)
        return staged

    def stage_products(self, products: List[Dict[str, Any]]) -> None:
        self.view_state.staged_products = list(products or [])
        self.products_loaded.emit(self.view_state.staged_products)

    def save_products_changes(self) -> bool:
        pid = self.view_state.active_project_id
        if not pid or self._products is None:
            return False
        prods = list(self.view_state.staged_products or [])
        if not prods:
            return False
        try:
            res = self._products.replace_products_for_project(int(pid), prods)
            if getattr(res, "ok", False):
                # Clear staged changes and reload enriched project for display
                self.view_state.staged_products = []
                try:
                    if self._projects is not None:
                        res2 = self._projects.load_enriched_project(self.view_state.project)
                        if getattr(res2, "ok", False) and getattr(res2, "value", None) is not None:
                            self.view_state.project = getattr(res2, "value", None)
                            self.project_loaded.emit(self.view_state.project)
                except Exception:
                    pass
                self._notify("Products saved")
                return True
            # Failure
            self._set_error(getattr(res, "error", "Failed to save products"))
            return False
        except Exception as e:  # pragma: no cover
            self._set_error(str(e))
            return False

    # ---- Helpers ----
    def _set_error(self, message: str) -> None:
        self.view_state.error = message
        self.notification.emit({"level": "error", "message": message})

    def _notify(self, message: str, level: str = "info") -> None:
        self.notification.emit({"level": level, "message": message})

    def _normalize_products_for_compare(self, products_list: List[Dict[str, Any]] | List[Any]) -> List[Any]:
        """Return a sorted, normalized list of tuples for equality compare including extended attributes.
        Accepts dicts or objects with attributes like the DataManager returns.
        """
        norm = []
        for d in (products_list or []):
            if isinstance(d, dict):
                name = d.get("name") or ""
                qty = d.get("quantity")
                desc = d.get("description") or ""
                cfs = d.get("custom_fields") or []
                loc = d.get("location") or ""
                width = d.get("width")
                height = d.get("height")
                depth = d.get("depth")
                xo = d.get("x_origin")
                yo = d.get("y_origin")
                zo = d.get("z_origin")
                item_no = d.get("item_number") or ""
                comment = d.get("comment") or ""
                angle = d.get("angle")
                link_sg = d.get("link_id_specification_group")
                link_loc = d.get("link_id_location")
                link_wall = d.get("link_id_wall")
                file_name = d.get("file_name") or ""
                picture_name = d.get("picture_name") or ""
            else:
                name = getattr(d, "name", "")
                qty = getattr(d, "quantity", None)
                desc = getattr(d, "description", "")
                cfs = getattr(d, "custom_fields", []) or []
                loc = getattr(d, "location", "") if hasattr(d, "location") else ""
                width = getattr(d, "width", None)
                height = getattr(d, "height", None)
                depth = getattr(d, "depth", None)
                xo = getattr(d, "x_origin", None)
                yo = getattr(d, "y_origin", None)
                zo = getattr(d, "z_origin", None)
                item_no = getattr(d, "item_number", "")
                comment = getattr(d, "comment", "")
                angle = getattr(d, "angle", None)
                link_sg = getattr(d, "link_id_specification_group", None)
                link_loc = getattr(d, "link_id_location", None)
                link_wall = getattr(d, "link_id_wall", None)
                file_name = getattr(d, "file_name", "")
                picture_name = getattr(d, "picture_name", "")
            cf_pairs = []
            for cf in cfs:
                if isinstance(cf, dict):
                    cf_pairs.append((cf.get("name") or "", cf.get("value")))
                else:
                    cf_pairs.append((getattr(cf, "name", ""), getattr(cf, "value", None)))
            cf_pairs.sort()
            norm.append((name, qty, desc, loc, width, height, depth, xo, yo, zo, item_no, comment, angle, link_sg, link_loc, link_wall, file_name, picture_name, tuple(cf_pairs)))
        norm.sort()
        return norm
