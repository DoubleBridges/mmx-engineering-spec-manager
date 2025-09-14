from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeView
from PySide6.QtCore import Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem


class ProjectsDetailView(QWidget):
    save_button_clicked_signal = Signal(object)
    load_products_clicked_signal = Signal()
    save_products_changes_clicked_signal = Signal()

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Action buttons
        self.load_products_button = QPushButton("Load Products From Innergy")
        self.layout.addWidget(self.load_products_button)

        # Tree view to display project and its collections
        self.tree_view = QTreeView()
        self.layout.addWidget(self.tree_view)

        # Existing save button for top-level project properties (kept for tests)
        self.save_button = QPushButton("Save")
        self.layout.addWidget(self.save_button)

        # New save changes button for products loaded from Innergy
        self.save_changes_button = QPushButton("Save Changes")
        self.save_changes_button.setEnabled(False)
        self.layout.addWidget(self.save_changes_button)

        # Connect the button clicks to our custom signals/slots
        self.save_button.clicked.connect(self.on_save_button_clicked)
        self.load_products_button.clicked.connect(self.load_products_clicked_signal.emit)
        self.save_changes_button.clicked.connect(self.save_products_changes_clicked_signal.emit)

        self.current_project = None
        self._pending_products = None  # used by controller to reflect non-persisted state

    def _as_str(self, value):
        try:
            return "" if value is None else str(value)
        except Exception:
            return ""

    def _item(self, text: str, value: str | None = None) -> QStandardItem:
        it = QStandardItem(text)
        if value is not None:
            # add sibling value item handled by caller
            pass
        return it

    def _add_kv_child(self, parent: QStandardItem, key: str, value: str):
        k_item = QStandardItem(key)
        v_item = QStandardItem(self._as_str(value))
        parent.appendRow([k_item, v_item])

    def _find_child_by_text(self, parent_item: QStandardItem, text: str) -> QStandardItem | None:
        for r in range(parent_item.rowCount()):
            child = parent_item.child(r, 0)
            if child and child.text() == text:
                return child
        return None

    def display_project(self, project):
        # Build a hierarchical model
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Item", "Value"])

        # Root: Project label
        proj_label = f"{self._as_str(getattr(project, 'number', ''))} - {self._as_str(getattr(project, 'name', ''))}"
        root = QStandardItem("Project")
        root_val = QStandardItem(proj_label)
        model.appendRow([root, root_val])

        # Details group (auto-expanded)
        details = QStandardItem("Details")
        details_val = QStandardItem("")
        root.appendRow([details, details_val])
        # Include known scalar properties
        self._add_kv_child(details, "ID", self._as_str(getattr(project, 'id', '')))
        self._add_kv_child(details, "Number", self._as_str(getattr(project, 'number', '')))
        self._add_kv_child(details, "Name", self._as_str(getattr(project, 'name', '')))
        self._add_kv_child(details, "Job Description", self._as_str(getattr(project, 'job_description', '')))
        self._add_kv_child(details, "Job Address", self._as_str(getattr(project, 'job_address', '')))

        # Callouts parent
        callouts_parent = QStandardItem("Callouts")
        callouts_parent_val = QStandardItem("")
        root.appendRow([callouts_parent, callouts_parent_val])

        # Helper to add a callout subgroup under Callouts
        def add_callout_group(items, title: str):
            grp = QStandardItem(title)
            grp_val = QStandardItem("")
            callouts_parent.appendRow([grp, grp_val])
            for co in items or []:
                try:
                    tag = getattr(co, 'tag', '') or ''
                    mat = getattr(co, 'material', '') or ''
                    desc = getattr(co, 'description', '') or ''
                    label = (f"{tag} - {mat}" if tag or mat else self._as_str(co))
                except Exception:
                    label, desc = self._as_str(co), ''
                grp.appendRow([QStandardItem(self._as_str(label)), QStandardItem(self._as_str(desc))])

        # Resolve callout collections and add subgroups (present even if empty)
        try:
            add_callout_group(getattr(project, 'finish_callouts', []) or [], 'Finish Callouts')
        except Exception:
            add_callout_group([], 'Finish Callouts')
        try:
            add_callout_group(getattr(project, 'hardware_callouts', []) or [], 'Hardware Callouts')
        except Exception:
            add_callout_group([], 'Hardware Callouts')
        try:
            add_callout_group(getattr(project, 'sink_callouts', []) or [], 'Sink Callouts')
        except Exception:
            add_callout_group([], 'Sink Callouts')
        try:
            add_callout_group(getattr(project, 'appliance_callouts', []) or [], 'Appliance Callouts')
        except Exception:
            add_callout_group([], 'Appliance Callouts')

        # Locations group (present even if empty)
        locs = QStandardItem("Locations")
        locs_val = QStandardItem("")
        root.appendRow([locs, locs_val])
        # If ORM relationships exist, place products under their locations as before
        try:
            locations = getattr(project, 'locations', []) or []
            products = getattr(project, 'products', []) or []
        except Exception:
            locations, products = [], []
        if locations or products:
            # Build mapping by location id when possible
            by_loc_id: dict[object, list] = {}
            for prod in products:
                try:
                    lid = getattr(prod, 'location_id', None)
                    if lid is None and getattr(prod, 'location', None) is not None:
                        lid = getattr(getattr(prod, 'location'), 'id', None)
                except Exception:
                    lid = None
                by_loc_id.setdefault(lid, []).append(prod)
            for loc in locations:
                # Determine location display and id
                try:
                    loc_name = getattr(loc, 'name', None) or self._as_str(loc)
                    loc_id = getattr(loc, 'id', None)
                except Exception:
                    loc_name = self._as_str(loc)
                    loc_id = None
                l_item = QStandardItem(self._as_str(loc_name))
                l_val = QStandardItem("")
                locs.appendRow([l_item, l_val])
                # Products under this location
                prods_here = by_loc_id.get(loc_id, [])
                if prods_here:
                    for p in prods_here:
                        try:
                            pname = getattr(p, 'name', None) or self._as_str(p)
                            qty = getattr(p, 'quantity', None)
                            p_item = QStandardItem(self._as_str(pname))
                            p_val = QStandardItem(f"Qty: {qty}" if qty is not None else "")
                        except Exception:
                            p_item = QStandardItem(self._as_str(p))
                            p_val = QStandardItem("")
                        l_item.appendRow([p_item, p_val])
                        # Add product properties (from ORM columns)
                        desc = self._as_str(getattr(p, 'description', ''))
                        if desc:
                            self._add_kv_child(p_item, "Description", desc)
                        # Dimensions
                        try:
                            if getattr(p, 'width', None) is not None:
                                self._add_kv_child(p_item, "Width", self._as_str(getattr(p, 'width', None)))
                            if getattr(p, 'height', None) is not None:
                                self._add_kv_child(p_item, "Height", self._as_str(getattr(p, 'height', None)))
                            if getattr(p, 'depth', None) is not None:
                                self._add_kv_child(p_item, "Depth", self._as_str(getattr(p, 'depth', None)))
                        except Exception:
                            pass
                        # Origins
                        try:
                            if getattr(p, 'x_origin_from_right', None) is not None:
                                self._add_kv_child(p_item, "X Origin", self._as_str(getattr(p, 'x_origin_from_right', None)))
                            if getattr(p, 'y_origin_from_face', None) is not None:
                                self._add_kv_child(p_item, "Y Origin", self._as_str(getattr(p, 'y_origin_from_face', None)))
                            if getattr(p, 'z_origin_from_bottom', None) is not None:
                                self._add_kv_child(p_item, "Z Origin", self._as_str(getattr(p, 'z_origin_from_bottom', None)))
                        except Exception:
                            pass
                        # Link IDs if present
                        try:
                            if getattr(p, 'specification_group_id', None) is not None:
                                self._add_kv_child(p_item, "LinkIDSpecificationGroup", self._as_str(getattr(p, 'specification_group_id', None)))
                            if getattr(p, 'wall_id', None) is not None:
                                self._add_kv_child(p_item, "LinkIDWall", self._as_str(getattr(p, 'wall_id', None)))
                        except Exception:
                            pass
                        # Product-level custom fields (includes ItemNumber/Comment/etc.)
                        try:
                            for cf in getattr(p, 'custom_fields', []) or []:
                                self._add_kv_child(p_item, self._as_str(getattr(cf, 'name', '')), self._as_str(getattr(cf, 'value', '')))
                        except Exception:
                            pass
            # Unassigned products
            unassigned = by_loc_id.get(None, [])
            if unassigned:
                ua_group = QStandardItem("Unassigned Products")
                ua_group_val = QStandardItem("")
                locs.appendRow([ua_group, ua_group_val])
                for p in unassigned:
                    pname = self._as_str(getattr(p, 'name', p))
                    qty = getattr(p, 'quantity', None)
                    ua_item = QStandardItem(pname)
                    ua_val = QStandardItem(f"Qty: {qty}" if qty is not None else "")
                    ua_group.appendRow([ua_item, ua_val])
                    # Add same properties for unassigned
                    desc = self._as_str(getattr(p, 'description', ''))
                    if desc:
                        self._add_kv_child(ua_item, "Description", desc)
                    try:
                        if getattr(p, 'width', None) is not None:
                            self._add_kv_child(ua_item, "Width", self._as_str(getattr(p, 'width', None)))
                        if getattr(p, 'height', None) is not None:
                            self._add_kv_child(ua_item, "Height", self._as_str(getattr(p, 'height', None)))
                        if getattr(p, 'depth', None) is not None:
                            self._add_kv_child(ua_item, "Depth", self._as_str(getattr(p, 'depth', None)))
                    except Exception:
                        pass
                    try:
                        if getattr(p, 'x_origin_from_right', None) is not None:
                            self._add_kv_child(ua_item, "X Origin", self._as_str(getattr(p, 'x_origin_from_right', None)))
                        if getattr(p, 'y_origin_from_face', None) is not None:
                            self._add_kv_child(ua_item, "Y Origin", self._as_str(getattr(p, 'y_origin_from_face', None)))
                        if getattr(p, 'z_origin_from_bottom', None) is not None:
                            self._add_kv_child(ua_item, "Z Origin", self._as_str(getattr(p, 'z_origin_from_bottom', None)))
                    except Exception:
                        pass
                    try:
                        if getattr(p, 'specification_group_id', None) is not None:
                            self._add_kv_child(ua_item, "LinkIDSpecificationGroup", self._as_str(getattr(p, 'specification_group_id', None)))
                        if getattr(p, 'wall_id', None) is not None:
                            self._add_kv_child(ua_item, "LinkIDWall", self._as_str(getattr(p, 'wall_id', None)))
                    except Exception:
                        pass
                    try:
                        for cf in getattr(p, 'custom_fields', []) or []:
                            self._add_kv_child(ua_item, self._as_str(getattr(cf, 'name', '')), self._as_str(getattr(cf, 'value', '')))
                    except Exception:
                        pass

        self.tree_view.setModel(model)
        # Expand the Details group by default
        try:
            details_index = model.index(0, 0).child(0, 0)  # root -> Details
            if details_index.isValid():
                self.tree_view.expand(model.index(0, 0))  # expand root
                self.tree_view.expand(details_index)
        except Exception:
            pass

        self.current_project = project

    def update_products_from_dicts(self, products: list[dict] | list):
        """Update (not replace) the Locations subtree using provided product dicts.
        Each dict may include keys: name, quantity, description, custom_fields (list of {name,value}), location,
        and extended attributes per ProductModel (width, height, depth, x_origin, y_origin, z_origin,
        item_number, comment, angle, link_id_specification_group, link_id_location, link_id_wall,
        file_name, picture_name).
        """
        model = self.tree_view.model()
        if not isinstance(model, QStandardItemModel):
            return
        root = model.item(0, 0)
        if root is None:
            return
        # Ensure Locations group exists
        locs = self._find_child_by_text(root, "Locations")
        if locs is None:
            locs = QStandardItem("Locations")
            locs_val = QStandardItem("")
            root.appendRow([locs, locs_val])
        # Clear existing rows under Locations
        while locs.rowCount() > 0:
            locs.removeRow(0)
        # Group by 'location' field
        by_loc_name: dict[str | None, list[dict]] = {}
        for d in (products or []):
            if not isinstance(d, dict):
                continue
            key = d.get("location")
            by_loc_name.setdefault(key, []).append(d)
        # Build location nodes (sorted by name, None last)
        def sort_key(k):
            return ("~" if k is None else str(k).lower())
        for loc_name in sorted(by_loc_name.keys(), key=sort_key):
            l_item = QStandardItem(self._as_str(loc_name) if loc_name is not None else "Unassigned")
            l_val = QStandardItem("")
            locs.appendRow([l_item, l_val])
            for p in by_loc_name[loc_name]:
                p_item = QStandardItem(self._as_str(p.get("name")))
                p_val = QStandardItem(f"Qty: {self._as_str(p.get('quantity'))}" if p.get("quantity") is not None else "")
                l_item.appendRow([p_item, p_val])
                # Add product properties as children
                self._add_kv_child(p_item, "Name", self._as_str(p.get("name")))
                if p.get("quantity") is not None:
                    self._add_kv_child(p_item, "Quantity", self._as_str(p.get("quantity")))
                if p.get("description"):
                    self._add_kv_child(p_item, "Description", self._as_str(p.get("description")))
                # Extended attributes (if present)
                for key, label in (
                    ("width", "Width"),
                    ("height", "Height"),
                    ("depth", "Depth"),
                    ("x_origin", "X Origin"),
                    ("y_origin", "Y Origin"),
                    ("z_origin", "Z Origin"),
                    ("item_number", "Item Number"),
                    ("comment", "Comment"),
                    ("angle", "Angle"),
                    ("link_id_specification_group", "LinkIDSpecificationGroup"),
                    ("link_id_location", "LinkIDLocation"),
                    ("link_id_wall", "LinkIDWall"),
                    ("file_name", "File Name"),
                    ("picture_name", "Picture Name"),
                ):
                    if p.get(key) is not None and p.get(key) != "":
                        self._add_kv_child(p_item, label, self._as_str(p.get(key)))
                # Custom fields
                for cf in (p.get("custom_fields") or []):
                    if isinstance(cf, dict):
                        self._add_kv_child(p_item, self._as_str(cf.get("name")), self._as_str(cf.get("value")))
        # Optionally expand Locations
        try:
            root_index = model.index(0, 0)
            locs_index = None
            for r in range(root.rowCount()):
                if root.child(r, 0) is locs:
                    locs_index = root_index.child(r, 0)
                    break
            if locs_index is not None:
                self.tree_view.expand(locs_index)
        except Exception:
            pass

    def on_save_button_clicked(self):
        updated_data = self.get_data()
        self.save_button_clicked_signal.emit(updated_data)

    def get_data(self):
        # With tree view, return current project's top-level properties
        if self.current_project is None:
            return {"number": "", "name": "", "job_description": ""}
        return {
            "number": self._as_str(getattr(self.current_project, 'number', '')),
            "name": self._as_str(getattr(self.current_project, 'name', '')),
            "job_description": self._as_str(getattr(self.current_project, 'job_description', '')),
        }

    # Helper to allow controller to toggle the Save Changes button state
    def set_save_products_changes_enabled(self, enabled: bool):
        try:
            self.save_changes_button.setEnabled(bool(enabled))
        except Exception:
            pass