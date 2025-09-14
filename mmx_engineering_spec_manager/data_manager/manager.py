import os
from pathlib import Path

from PySide6.QtCore import QStandardPaths
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mmx_engineering_spec_manager.db_models.appliance_callout import \
    ApplianceCallout
from mmx_engineering_spec_manager.db_models.custom_field import CustomField
from mmx_engineering_spec_manager.db_models.database_config import Base
from mmx_engineering_spec_manager.db_models.finish_callout import FinishCallout
from mmx_engineering_spec_manager.db_models.global_prompts import GlobalPrompts
from mmx_engineering_spec_manager.db_models.hardware_callout import HardwareCallout
from mmx_engineering_spec_manager.db_models.location import Location
from mmx_engineering_spec_manager.db_models.product import Product
from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.db_models.prompt import Prompt
from mmx_engineering_spec_manager.db_models.sink_callout import SinkCallout
from mmx_engineering_spec_manager.db_models.specification_group import SpecificationGroup
from mmx_engineering_spec_manager.db_models.wall import Wall
from mmx_engineering_spec_manager.db_models.wizard_prompts import WizardPrompts
from mmx_engineering_spec_manager.db_models.location_table_callout import LocationTableCallout
from mmx_engineering_spec_manager.importers.innergy import InnergyImporter
from mmx_engineering_spec_manager.mappers.innergy_mapper import map_project_payload_to_dto, map_products_payload_to_dtos
from mmx_engineering_spec_manager.utilities.persistence import create_engine_and_sessionmaker, project_sqlite_db_path, create_engine_and_sessionmaker_for_sqlite_path
from mmx_engineering_spec_manager.utilities import callout_import
from mmx_engineering_spec_manager.utilities.settings import get_settings
from mmx_engineering_spec_manager.utilities.logging_config import get_logger


class DataManager:
    def __init__(self):
        # Initialize DB engine/session using centralized persistence config (supports SQLite/Postgres)
        engine, Session = create_engine_and_sessionmaker()
        # Ensure schema exists
        Base.metadata.create_all(engine)
        # Run lightweight SQLite migration to add any missing product columns (safe no-op otherwise)
        try:
            from mmx_engineering_spec_manager.utilities.migrations import (
                migrate_sqlite_products_add_missing_columns,
                migrate_sqlite_walls_add_missing_columns,
                migrate_sqlite_global_prompts_add_missing_columns,
                migrate_sqlite_wizard_prompts_add_missing_columns,
            )
            migrate_sqlite_products_add_missing_columns(engine)
            migrate_sqlite_walls_add_missing_columns(engine)
            migrate_sqlite_global_prompts_add_missing_columns(engine)
            migrate_sqlite_wizard_prompts_add_missing_columns(engine)
        except Exception:  # pragma: no cover
            pass
        self.session = Session()
        # Note: per-project databases are created on demand via prepare_project_db()
        self._logger = get_logger(__name__)

    def save_project(self, raw_data, session=None):
        self.create_or_update_project(raw_data, session)

    def save_project_with_collections(self, raw_data, session=None):
        db_session = session if session is not None else self.session
        project = Project(
            number=raw_data.get("number"),
            name=raw_data.get("name"),
            job_description=raw_data.get("job_description")
        )

        # Add locations to the project
        if "locations" in raw_data:
            for location_data in raw_data["locations"]:
                location = Location(
                    name=location_data.get("name"),
                    project=project
                )
                project.locations.append(location)

        # Add products to the project
        if "products" in raw_data:
            for product_data in raw_data["products"]:
                product = Product(
                    name=product_data.get("name"),
                    quantity=product_data.get("quantity"),
                    project=project
                )
                project.products.append(product)

        # Add walls to the project
        if "walls" in raw_data:
            for wall_data in raw_data["walls"]:
                wall = Wall(
                    link_id=wall_data.get("link_id"),
                    width=wall_data.get("width"),
                    project=project
                )
                project.walls.append(wall)

        # Add custom fields to the project
        if "custom_fields" in raw_data:
            for cf_data in raw_data["custom_fields"]:
                custom_field = CustomField(
                    name=cf_data.get("name"),
                    value=cf_data.get("value"),
                    project=project
                )
                project.custom_fields.append(custom_field)

        # Add global prompts to the project
        if "global_prompts" in raw_data:
            for gp_data in raw_data["global_prompts"]:
                global_prompts = GlobalPrompts(
                    name=gp_data.get("name"),
                    project=project
                )
                project.global_prompts.append(global_prompts)

        # Add wizard prompts to the project
        if "wizard_prompts" in raw_data:
            for wp_data in raw_data["wizard_prompts"]:
                wizard_prompts = WizardPrompts(
                    name=wp_data.get("name"),
                    project=project
                )
                project.wizard_prompts.append(wizard_prompts)

        db_session.add(project)
        db_session.commit()

    def get_all_projects(self, session=None):
        db_session = session if session is not None else self.session
        return db_session.query(Project).all()

    def sync_projects_from_innergy(self, session=None, progress=None):
        """
        Imports projects from Innergy API and saves them to the database.
        Raises RuntimeError on configuration or HTTP errors; callers should handle and surface to UI.
        Returns:
            int: number of imported/updated projects
        """
        logger = get_logger(__name__)
        db_session = session if session is not None else self.session
        settings = get_settings()
        if progress:
            try:
                progress(5)
            except Exception:
                pass
        if not settings.innergy_base_url or not settings.innergy_api_key:
            logger.warning(
                "Innergy API key or base URL missing; proceeding (tests may mock importer). UI should validate settings before invoking sync."
            )
        importer = InnergyImporter()
        logger.info("Starting Innergy projects sync from %s", settings.innergy_base_url)
        try:
            projects_data = importer.get_projects()
            imported = 0
            total = len(projects_data) if projects_data else 0
            if progress:
                try:
                    progress(10)
                except Exception:
                    pass
            if projects_data:
                for idx, project_data in enumerate(projects_data, start=1):
                    # Adapt the Innergy data to the format expected by our database models
                    # Normalize address and description safely (avoid dicts in text fields)
                    addr = project_data.get("Address")
                    if isinstance(addr, dict):
                        address_str = addr.get("Address1") or addr.get("address1") or addr.get("Address") or ""  # pragma: no cover
                    else:
                        address_str = str(addr or "")
                    # Prefer explicit JobDescription; fall back to address string for backward-compat and to avoid dicts
                    job_desc = project_data.get("JobDescription") or address_str
                    # Keep formatted_data minimal to satisfy existing expectations/tests
                    formatted_data = {
                        "number": project_data.get("Number"),
                        "name": project_data.get("Name"),
                        "job_description": job_desc,
                    }
                    self.create_or_update_project(formatted_data, db_session)
                    imported += 1
                    if progress and total > 0:
                        try:
                            base = 10
                            span = 85
                            pct = base + int(span * (idx / total))
                            progress(min(99, pct))
                        except Exception:
                            pass
                db_session.commit()
            if progress:
                try:
                    progress(100)
                except Exception:
                    pass
            logger.info("Innergy projects sync finished. Imported/updated: %d", imported)
            return imported
        except Exception as e:
            logger.exception("Innergy projects sync failed: %s", e)
            raise

    def get_project_by_id(self, project_id, session=None):
        db_session = session if session is not None else self.session
        return db_session.query(Project).get(project_id)

    def prepare_project_db(self, project) -> str:
        """Ensure the per-project SQLite DB exists and has the schema. Returns the DB path.

        It also ensures the Project row exists inside the per-project DB so FKs can resolve.
        """
        try:
            db_path = project_sqlite_db_path(project)
            engine, Session = create_engine_and_sessionmaker_for_sqlite_path(db_path)
            # Create schema
            Base.metadata.create_all(engine)
            # Attempt light migrations where applicable
            try:
                from mmx_engineering_spec_manager.utilities.migrations import (
                    migrate_sqlite_products_add_missing_columns,
                    migrate_sqlite_walls_add_missing_columns,
                    migrate_sqlite_global_prompts_add_missing_columns,
                    migrate_sqlite_wizard_prompts_add_missing_columns,
                )
                migrate_sqlite_products_add_missing_columns(engine)
                migrate_sqlite_walls_add_missing_columns(engine)
                migrate_sqlite_global_prompts_add_missing_columns(engine)
                migrate_sqlite_wizard_prompts_add_missing_columns(engine)
            except Exception:
                pass
            # Ensure project row exists in this DB
            sess = Session()
            try:
                pid = getattr(project, "id", None)
                # Try to lookup by id else by number
                obj = None
                if pid is not None:
                    obj = sess.query(Project).get(pid)
                if obj is None:
                    number = getattr(project, "number", None)
                    if number is not None:
                        obj = sess.query(Project).filter_by(number=number).first()
                if obj is None:
                    # Create minimal project row
                    obj = Project(
                        id=pid if isinstance(pid, int) else None,
                        number=getattr(project, "number", None),
                        name=getattr(project, "name", None),
                        job_description=getattr(project, "job_description", None),
                    )
                    sess.add(obj)
                    sess.commit()
            finally:
                sess.close()
            return db_path
        except Exception as e:  # pragma: no cover
            try:
                self._logger.warning("prepare_project_db failed: %s", e)
            except Exception:
                pass
            # Return a path anyway for debugging
            return project_sqlite_db_path(project)

    def create_or_update_project(self, raw_data, session=None):
        db_session = session if session is not None else self.session
        project = db_session.query(Project).filter_by(number=raw_data.get("number")).first()
        if project:
            project.name = raw_data.get("name")
            project.job_description = raw_data.get("job_description")
            if hasattr(project, "job_address"):
                project.job_address = raw_data.get("job_address")
        else:
            project = Project(
                number=raw_data.get("number"),
                name=raw_data.get("name"),
                job_description=raw_data.get("job_description"),
                job_address=raw_data.get("job_address")
            )
            db_session.add(project)
        db_session.commit()
        return project

    def get_callouts_for_project(self, project_id: int, session=None):
        """
        Load grouped callouts for a project from its per-project SQLite database.
        Returns a dict with keys: "Finishes", "Hardware", "Sinks", "Appliances", "Uncategorized".
        Each value is a list of dict rows: {"Type","Name","Tag","Description"}.
        """
        # Prefer provided session
        if session is not None:
            db_session = session
            engine2 = None
        else:
            # Open per-project DB similar to replace_callouts_for_project
            try:
                p = None
                try:
                    p = self.session.query(Project).get(project_id)
                except Exception:
                    p = None
                if p is None:
                    class _Tmp:
                        pass
                    p = _Tmp()
                    setattr(p, 'id', project_id)
                db_path = self.prepare_project_db(p)
                engine2, Session2 = create_engine_and_sessionmaker_for_sqlite_path(db_path)
                db_session = Session2()
            except Exception:
                db_session = self.session
                engine2 = None
        try:
            groups = {
                "Finishes": [],
                "Hardware": [],
                "Sinks": [],
                "Appliances": [],
                "Uncategorized": [],
            }
            # Query each table and map to UI rows
            def fetch_many(model_cls, type_label, key_name):
                items = db_session.query(model_cls).filter_by(project_id=project_id).all()
                out = []
                for obj in items:
                    try:
                        name = getattr(obj, 'material', None)
                        tag = getattr(obj, 'tag', None)
                        desc = getattr(obj, 'description', None)
                        out.append({
                            "Type": type_label,
                            "Name": name or "",
                            "Tag": tag or "",
                            "Description": desc or "",
                        })
                    except Exception:
                        continue
                groups[key_name] = out

            fetch_many(FinishCallout, callout_import.TYPE_FINISH, "Finishes")
            fetch_many(HardwareCallout, callout_import.TYPE_HARDWARE, "Hardware")
            fetch_many(SinkCallout, callout_import.TYPE_SINK, "Sinks")
            fetch_many(ApplianceCallout, callout_import.TYPE_APPLIANCE, "Appliances")
            return groups
        finally:
            try:
                if 'Session2' in locals() and db_session is not (session if session is not None else self.session):
                    db_session.close()
            except Exception:
                pass

    def replace_callouts_for_project(self, project_id: int, grouped: dict, session=None):
        """
        Replace all callouts for a project with the provided grouped callouts.
        `grouped` is a dict with keys: "Finishes", "Hardware", "Sinks", "Appliances", "Uncategorized".
        Values are lists of DTOs having attributes: name/material, tag, description.
        Uncategorized items are ignored unless assigned a concrete type by the UI before saving.
        
        This method persists into the selected project's own SQLite database file.
        """
        # Prefer an explicitly provided session (tests rely on this behavior)
        if session is not None:
            db_session = session
            engine2 = None
        else:
            # Resolve target project's per-project DB and open a short-lived session there.
            try:
                # Fetch project from global DB to derive filename and ensure minimal metadata
                p = None
                try:
                    p = self.session.query(Project).get(project_id)
                except Exception:
                    p = None
                if p is None:
                    # Fallback object with only id if global lookup failed
                    class _Tmp:
                        pass
                    p = _Tmp()
                    setattr(p, 'id', project_id)
                # Ensure DB exists and schema ready
                db_path = self.prepare_project_db(p)
                engine2, Session2 = create_engine_and_sessionmaker_for_sqlite_path(db_path)
                db_session = Session2()
            except Exception:
                # Fallback to global session if anything fails
                db_session = self.session
                engine2 = None
        try:
            # Clear existing in the project DB
            db_session.query(FinishCallout).filter_by(project_id=project_id).delete(synchronize_session=False)
            db_session.query(HardwareCallout).filter_by(project_id=project_id).delete(synchronize_session=False)
            db_session.query(SinkCallout).filter_by(project_id=project_id).delete(synchronize_session=False)
            db_session.query(ApplianceCallout).filter_by(project_id=project_id).delete(synchronize_session=False)

            # Helper to add
            def add_many(model_cls, items):
                for d in items or []:
                    # Support either DTOs or dicts
                    name = getattr(d, 'name', None) or (d.get('name') if isinstance(d, dict) else None) or getattr(d, 'Name', None) or (d.get('Name') if isinstance(d, dict) else None)
                    tag = getattr(d, 'tag', None) or (d.get('tag') if isinstance(d, dict) else None) or getattr(d, 'Tag', None) or (d.get('Tag') if isinstance(d, dict) else None)
                    desc = getattr(d, 'description', None) or (d.get('description') if isinstance(d, dict) else None) or getattr(d, 'Description', None) or (d.get('Description') if isinstance(d, dict) else None)
                    if not name or not tag:
                        continue
                    obj = model_cls(project_id=project_id)
                    # Map to CalloutMixin fields (material, tag, description)
                    setattr(obj, 'material', str(name))
                    setattr(obj, 'tag', str(tag))
                    setattr(obj, 'description', str(desc) if desc is not None else None)
                    db_session.add(obj)

            add_many(FinishCallout, grouped.get("Finishes"))
            add_many(HardwareCallout, grouped.get("Hardware"))
            add_many(SinkCallout, grouped.get("Sinks"))
            add_many(ApplianceCallout, grouped.get("Appliances"))
            # Uncategorized are not persisted until categorized
            db_session.commit()
        finally:
            try:
                # Close only if we created a separate session
                if 'Session2' in locals() and db_session is not (session if session is not None else self.session):
                    db_session.close()
            except Exception:
                pass
    def ingest_project_details_to_project_db(self, project_number: str) -> bool:
        """
        Fetch a project's details from Innergy by ID (we use the project number as ID),
        map to DTOs, and persist the data into that project's specific SQLite DB.
        Returns True on success, False otherwise. Network/parse errors are swallowed with a warning.
        """
        try:
            settings = get_settings()
        except Exception:
            settings = None
        # Avoid unexpected network during tests/dev when API key is not configured
        if not settings or not getattr(settings, "innergy_api_key", None):
            try:
                self._logger.info("Skipping Innergy ingest: API key not configured.")
            except Exception:
                pass
            return False
        try:
            importer = InnergyImporter()
            project_payload = importer.get_job_details(project_number) or {}
            products_payload = importer.get_products(project_number) or []
        except Exception as e:  # pragma: no cover
            try:
                self._logger.warning("Innergy fetch byId failed: %s", e)
            except Exception:
                pass
            return False
        if not project_payload:
            return False
        # Map payloads to our DTOs
        try:
            dto = map_project_payload_to_dto(project_payload, products_payload)
        except Exception as e:  # pragma: no cover
            try:
                self._logger.warning("Mapping project payload failed: %s", e)
            except Exception:
                pass
            return False
        # Ensure a global Project exists (used to derive per-project DB path and id)
        project = self.create_or_update_project({
            "number": dto.number,
            "name": dto.name,
            "job_description": dto.job_description,
            "job_address": dto.job_address,
        })
        # Prepare/open the per-project DB and persist collections there
        db_path = self.prepare_project_db(project)
        try:
            engine2, Session2 = create_engine_and_sessionmaker_for_sqlite_path(db_path)
            sess2 = Session2()
        except Exception as e:  # pragma: no cover
            try:
                self._logger.warning("Failed to open per-project DB: %s", e)
            except Exception:
                pass
            return False
        try:
            pid = getattr(project, "id", None)
            if pid is None:
                return False
            # Upsert/refresh the Project row in the per-project DB
            pr = sess2.query(Project).get(pid)
            if pr is None:
                pr = Project(
                    id=pid,
                    number=dto.number,
                    name=dto.name,
                    job_description=dto.job_description,
                )
                if hasattr(pr, "job_address"):
                    setattr(pr, "job_address", dto.job_address)
                sess2.add(pr)
                sess2.flush()
            else:
                pr.number = dto.number
                pr.name = dto.name
                pr.job_description = dto.job_description
                if hasattr(pr, "job_address"):
                    setattr(pr, "job_address", dto.job_address)
            # Clear existing child rows for this project
            prod_ids = [row[0] for row in sess2.query(Product.id).filter_by(project_id=pid).all()]
            if prod_ids:
                sess2.query(CustomField).filter(CustomField.product_id.in_(prod_ids)).delete(synchronize_session=False)
            sess2.query(CustomField).filter_by(project_id=pid).delete(synchronize_session=False)
            sess2.query(Product).filter_by(project_id=pid).delete(synchronize_session=False)
            sess2.query(Location).filter_by(project_id=pid).delete(synchronize_session=False)
            # Insert locations
            name_to_loc_id: dict[str, int] = {}
            for loc_dto in dto.locations or []:
                name = getattr(loc_dto, "name", None) or ""
                if not name:
                    continue
                loc = Location(name=name, project_id=pid)
                sess2.add(loc)
                sess2.flush()
                try:
                    name_to_loc_id[name] = loc.id  # type: ignore[attr-defined]
                except Exception:
                    pass
            # Insert products and their custom fields
            for p_dto in dto.products or []:
                prod = Product(
                    name=getattr(p_dto, "name", ""),
                    quantity=getattr(p_dto, "quantity", None),
                    project_id=pid,
                )
                # If in future ProductDTO carries a location, we could map it here using name_to_loc_id
                sess2.add(prod)
                sess2.flush()
                for cf in getattr(p_dto, "custom_fields", []) or []:
                    sess2.add(CustomField(name=getattr(cf, "name", ""), value=getattr(cf, "value", None), product_id=prod.id))
            # Project-level custom fields
            for cf in getattr(dto, "custom_fields", []) or []:
                sess2.add(CustomField(name=getattr(cf, "name", ""), value=getattr(cf, "value", None), project_id=pid))
            sess2.commit()
            return True
        except Exception as e:  # pragma: no cover
            try:
                sess2.rollback()
            except Exception:
                pass
            try:
                self._logger.warning("Persisting project details to per-project DB failed: %s", e)
            except Exception:
                pass
            return False
        finally:
            try:
                sess2.close()
            except Exception:
                pass

    def get_full_project_from_project_db(self, project_id: int):
        """
        Return the Project ORM object (with relationships loaded) from the project's specific DB.
        Returns None if not found or on error.
        """
        # Build a minimal object to derive DB path
        class _Tmp:
            pass
        tmp = _Tmp()
        setattr(tmp, "id", project_id)
        try:
            db_path = self.prepare_project_db(tmp)
            engine2, Session2 = create_engine_and_sessionmaker_for_sqlite_path(db_path)
            sess2 = Session2()
        except Exception as e:  # pragma: no cover
            try:
                self._logger.warning("Open per-project DB for read failed: %s", e)
            except Exception:
                pass
            return None
        try:
            pr = sess2.query(Project).get(project_id)
            if pr is None:
                return None
            # Force-load common relationships for display
            try:
                _ = list(getattr(pr, "locations", []) or [])
                _ = list(getattr(pr, "products", []) or [])
                _ = list(getattr(pr, "custom_fields", []) or [])
                _ = list(getattr(pr, "walls", []) or [])
                _ = list(getattr(pr, "specification_groups", []) or [])
                _ = list(getattr(pr, "global_prompts", []) or [])
                _ = list(getattr(pr, "wizard_prompts", []) or [])
            except Exception:
                pass
            # Detach so it can be used after session closes
            try:
                sess2.expunge(pr)
            except Exception:
                pass
            return pr
        finally:
            try:
                sess2.close()
            except Exception:
                pass

    def fetch_products_from_innergy(self, project_number: str):
        """Fetch budget products for a project number from Innergy and map to simple dicts.
        Returns a list of dicts with keys like: name, quantity, description, custom_fields, location,
        and extended attributes from ProductModel (width, height, depth, item_number, comment, angle,
        x_origin, y_origin, z_origin, link_id_specification_group, link_id_location, link_id_wall,
        file_name, picture_name). Returns [] if API key not configured or on error.
        """
        try:
            settings = get_settings()
        except Exception:
            settings = None
        if not settings or not getattr(settings, "innergy_api_key", None):
            try:
                self._logger.info("Skipping Innergy products fetch: API key not configured.")
            except Exception:
                pass
            return []
        try:
            importer = InnergyImporter()
            # Fetch filtered products for essential fields and DTO mapping
            products_payload = importer.get_products(project_number) or []
            # Also fetch raw payload to extract location and extended attributes
            raw_payload = None
            try:
                raw_payload = importer.get_products_raw(project_number)
            except Exception:
                raw_payload = None
            raw_items = []
            if isinstance(raw_payload, dict) and isinstance(raw_payload.get("Items"), list):
                raw_items = raw_payload.get("Items")
            elif isinstance(raw_payload, list):
                raw_items = raw_payload
            pdtos = map_products_payload_to_dtos(products_payload)
            out = []
            # Attempt to align locations and extended attributes from raw payload with mapped DTOs by index
            for idx, p in enumerate(pdtos):
                cfs = []
                for cf in getattr(p, "custom_fields", []) or []:
                    cfs.append({"name": getattr(cf, "name", ""), "value": getattr(cf, "value", None)})
                # Defaults
                location = None
                width = height = depth = None
                x_origin = y_origin = z_origin = None
                item_number = comment = angle = None
                link_sg = link_loc = link_wall = None
                file_name = picture_name = None
                try:
                    src = raw_items[idx] if isinstance(raw_items, list) and idx < len(raw_items) else (
                        products_payload[idx] if isinstance(products_payload, list) and idx < len(products_payload) else None
                    )
                    if isinstance(src, dict):
                        # Location can be str or dict
                        loc_val = src.get("Location") or src.get("location") or src.get("LocationName") or src.get("locationName")
                        if isinstance(loc_val, dict):
                            location = loc_val.get("Name") or loc_val.get("name") or loc_val.get("Title") or loc_val.get("title")
                        elif isinstance(loc_val, str):
                            location = loc_val
                        # Extended numeric/string attributes
                        width = src.get("Width")
                        height = src.get("Height")
                        depth = src.get("Depth")
                        x_origin = src.get("XOrigin")
                        y_origin = src.get("YOrigin")
                        z_origin = src.get("ZOrigin")
                        item_number = src.get("ItemNumber")
                        comment = src.get("Comment")
                        angle = src.get("Angle")
                        link_sg = src.get("LinkIDSpecificationGroup")
                        link_loc = src.get("LinkIDLocation")
                        link_wall = src.get("LinkIDWall")
                        file_name = src.get("FileName")
                        picture_name = src.get("PictureName")
                except Exception:
                    pass
                out.append({
                    "name": getattr(p, "name", ""),
                    "quantity": getattr(p, "quantity", None),
                    "description": getattr(p, "description", ""),
                    "custom_fields": cfs,
                    "location": location,
                    # Extended attributes (snake_case)
                    "width": width,
                    "height": height,
                    "depth": depth,
                    "x_origin": x_origin,
                    "y_origin": y_origin,
                    "z_origin": z_origin,
                    "item_number": item_number,
                    "comment": comment,
                    "angle": angle,
                    "link_id_specification_group": link_sg,
                    "link_id_location": link_loc,
                    "link_id_wall": link_wall,
                    "file_name": file_name,
                    "picture_name": picture_name,
                })
            return out
        except Exception as e:  # pragma: no cover
            try:
                self._logger.warning("Fetching products from Innergy failed: %s", e)
            except Exception:
                pass
            return []

    def get_products_for_project_from_project_db(self, project_id: int):
        """Load products (and their custom fields) from the project's specific DB as a list of dicts,
        including location and extended attributes in ProductModel.
        """
        # Open per-project DB session
        try:
            tmp = type("_Tmp", (), {})()
            setattr(tmp, "id", project_id)
            db_path = self.prepare_project_db(tmp)
            engine2, Session2 = create_engine_and_sessionmaker_for_sqlite_path(db_path)
            sess2 = Session2()
        except Exception as e:  # pragma: no cover
            try:
                self._logger.warning("Open per-project DB for products failed: %s", e)
            except Exception:
                pass
            return []
        try:
            prods = sess2.query(Product).filter_by(project_id=project_id).all()
            out = []
            for p in prods:
                try:
                    # Collect custom fields
                    cfs = []
                    extras_map = {}
                    for cf in getattr(p, "custom_fields", []) or []:
                        name = getattr(cf, "name", "")
                        val = getattr(cf, "value", None)
                        cfs.append({"name": name, "value": val})
                        # Capture known extra attributes persisted as CFs
                        if name in {"ItemNumber", "Comment", "Angle", "FileName", "PictureName"}:
                            extras_map[name] = val
                    # Location name if linked
                    loc_name = None
                    try:
                        loc = getattr(p, 'location', None)
                        if loc is not None:
                            loc_name = getattr(loc, 'name', None)
                    except Exception:
                        loc_name = None
                    out.append({
                        "name": getattr(p, "name", ""),
                        "quantity": getattr(p, "quantity", None),
                        "description": getattr(p, "description", ""),
                        "custom_fields": cfs,
                        "location": loc_name,
                        # Extended columns
                        "width": getattr(p, "width", None),
                        "height": getattr(p, "height", None),
                        "depth": getattr(p, "depth", None),
                        "x_origin": getattr(p, "x_origin_from_right", None),
                        "y_origin": getattr(p, "y_origin_from_face", None),
                        "z_origin": getattr(p, "z_origin_from_bottom", None),
                        "link_id_specification_group": getattr(p, "specification_group_id", None),
                        "link_id_wall": getattr(p, "wall_id", None),
                        # Extras from custom fields
                        "item_number": extras_map.get("ItemNumber"),
                        "comment": extras_map.get("Comment"),
                        "angle": extras_map.get("Angle"),
                        "file_name": extras_map.get("FileName"),
                        "picture_name": extras_map.get("PictureName"),
                    })
                except Exception:
                    continue
            return out
        finally:
            try:
                sess2.close()
            except Exception:
                pass

    def replace_products_for_project(self, project_id: int, products: list[dict] | list):
        """Replace all products for a project in its per-project DB with provided products list.
        Each product can be a dict or DTO with attributes name, quantity, description, custom_fields,
        location, and extended attributes from ProductModel. Also upserts Location rows and links products.
        """
        # Open per-project DB session
        try:
            tmp = type("_Tmp", (), {})()
            setattr(tmp, "id", project_id)
            db_path = self.prepare_project_db(tmp)
            engine2, Session2 = create_engine_and_sessionmaker_for_sqlite_path(db_path)
            sess2 = Session2()
        except Exception as e:  # pragma: no cover
            try:
                self._logger.warning("Open per-project DB for replace products failed: %s", e)
            except Exception:
                pass
            return False
        try:
            # Delete existing products and their CFs
            prod_ids = [row[0] for row in sess2.query(Product.id).filter_by(project_id=project_id).all()]
            if prod_ids:
                sess2.query(CustomField).filter(CustomField.product_id.in_(prod_ids)).delete(synchronize_session=False)
            sess2.query(Product).filter_by(project_id=project_id).delete(synchronize_session=False)
            # Preload locations mapping by name
            existing_locs = sess2.query(Location).filter_by(project_id=project_id).all()
            name_to_loc = { (getattr(l, 'name', '') or '').strip(): l for l in existing_locs }
            # Insert new products
            for d in (products or []):
                is_dict = isinstance(d, dict)
                name = getattr(d, 'name', None) if not is_dict else d.get('name')
                qty = getattr(d, 'quantity', None) if not is_dict else d.get('quantity')
                desc = getattr(d, 'description', None) if not is_dict else d.get('description')
                width = getattr(d, 'width', None) if not is_dict else d.get('width')
                height = getattr(d, 'height', None) if not is_dict else d.get('height')
                depth = getattr(d, 'depth', None) if not is_dict else d.get('depth')
                x_origin = getattr(d, 'x_origin', None) if not is_dict else d.get('x_origin')
                y_origin = getattr(d, 'y_origin', None) if not is_dict else d.get('y_origin')
                z_origin = getattr(d, 'z_origin', None) if not is_dict else d.get('z_origin')
                link_sg = getattr(d, 'link_id_specification_group', None) if not is_dict else d.get('link_id_specification_group')
                link_wall = getattr(d, 'link_id_wall', None) if not is_dict else d.get('link_id_wall')
                # Create Product row
                prod = Product(name=name or "", quantity=qty, project_id=project_id)
                # Map columns present on model
                if hasattr(prod, 'description'):
                    setattr(prod, 'description', desc or "")
                if hasattr(prod, 'width'):
                    setattr(prod, 'width', width)
                if hasattr(prod, 'height'):
                    setattr(prod, 'height', height)
                if hasattr(prod, 'depth'):
                    setattr(prod, 'depth', depth)
                if hasattr(prod, 'x_origin_from_right'):
                    setattr(prod, 'x_origin_from_right', x_origin)
                if hasattr(prod, 'y_origin_from_face'):
                    setattr(prod, 'y_origin_from_face', y_origin)
                if hasattr(prod, 'z_origin_from_bottom'):
                    setattr(prod, 'z_origin_from_bottom', z_origin)
                if hasattr(prod, 'specification_group_id'):
                    try:
                        setattr(prod, 'specification_group_id', int(link_sg) if link_sg is not None else None)
                    except Exception:
                        pass
                if hasattr(prod, 'wall_id'):
                    try:
                        setattr(prod, 'wall_id', int(link_wall) if link_wall is not None else None)
                    except Exception:
                        pass
                # Resolve/Upsert location by name if provided
                loc_name = None
                if is_dict:
                    loc_name = d.get('location')
                else:
                    loc_name = getattr(d, 'location', None)
                if isinstance(loc_name, str) and loc_name.strip():
                    key = loc_name.strip()
                    loc_obj = name_to_loc.get(key)
                    if loc_obj is None:
                        loc_obj = Location(name=key, project_id=project_id)
                        sess2.add(loc_obj)
                        sess2.flush()
                        name_to_loc[key] = loc_obj
                    try:
                        prod.location_id = loc_obj.id
                    except Exception:
                        pass
                # Persist product
                sess2.add(prod)
                sess2.flush()
                # Custom fields (existing custom fields from payload)
                cfs = getattr(d, 'custom_fields', None)
                if is_dict:
                    cfs = d.get('custom_fields')
                for cf in (cfs or []):
                    cf_name = getattr(cf, 'name', None) if not isinstance(cf, dict) else cf.get('name')
                    cf_val = getattr(cf, 'value', None) if not isinstance(cf, dict) else cf.get('value')
                    sess2.add(CustomField(name=cf_name or "", value=cf_val, product_id=prod.id))
                # Persist extra attributes without dedicated columns as product custom fields
                extras = {}
                if is_dict:
                    extras = {
                        'ItemNumber': d.get('item_number'),
                        'Comment': d.get('comment'),
                        'Angle': d.get('angle'),
                        'FileName': d.get('file_name'),
                        'PictureName': d.get('picture_name'),
                    }
                else:
                    extras = {
                        'ItemNumber': getattr(d, 'item_number', None),
                        'Comment': getattr(d, 'comment', None),
                        'Angle': getattr(d, 'angle', None),
                        'FileName': getattr(d, 'file_name', None),
                        'PictureName': getattr(d, 'picture_name', None),
                    }
                for k, v in extras.items():
                    if v is not None and v != "":
                        sess2.add(CustomField(name=k, value=v, product_id=prod.id))
            sess2.commit()
            return True
        except Exception as e:  # pragma: no cover
            try:
                sess2.rollback()
            except Exception:
                pass
            try:
                self._logger.warning("replace_products_for_project failed: %s", e)
            except Exception:
                pass
            return False
        finally:
            try:
                sess2.close()
            except Exception:
                pass


    def get_location_tables_for_project(self, project_id: int, session=None) -> dict:
        """
        Load location table callouts for a project from its per-project SQLite DB.
        Returns a mapping: { location_name: [ {"Type","Tag","Description"}, ... ] }
        Unknown or missing location names are grouped under "" (empty string).
        """
        # Prefer provided session
        if session is not None:
            db_session = session
        else:
            # Open per-project DB
            try:
                tmp = type("_Tmp", (), {})()
                setattr(tmp, "id", project_id)
                db_path = self.prepare_project_db(tmp)
                engine2, Session2 = create_engine_and_sessionmaker_for_sqlite_path(db_path)
                db_session = Session2()
            except Exception:
                db_session = self.session
        try:
            rows = db_session.query(LocationTableCallout).filter_by(project_id=project_id).all()
            out: dict[str, list[dict]] = {}
            for obj in rows or []:
                try:
                    loc_name = None
                    try:
                        loc = getattr(obj, "location", None)
                        if loc is not None:
                            loc_name = getattr(loc, "name", None)
                    except Exception:
                        loc_name = None
                    key = (loc_name or "").strip()
                    out.setdefault(key, []).append({
                        "Type": getattr(obj, "type", "") or "",
                        "Tag": getattr(obj, "tag", "") or "",
                        "Description": getattr(obj, "description", "") or "",
                    })
                except Exception:
                    continue
            return out
        finally:
            try:
                if 'Session2' in locals() and db_session is not (session if session is not None else self.session):
                    db_session.close()
            except Exception:
                pass

    def replace_location_tables_for_project(self, project_id: int, data: dict | None, session=None) -> bool:
        """
        Replace all location table callouts for a project in its per-project DB.
        `data` must be a mapping of location_name -> list of dicts with keys Type, Tag, Description.
        Locations are upserted by name when needed.
        """
        if data is None:
            data = {}
        # Prefer provided session
        created_session = False
        if session is not None:
            db_session = session
        else:
            try:
                tmp = type("_Tmp", (), {})()
                setattr(tmp, "id", project_id)
                db_path = self.prepare_project_db(tmp)
                engine2, Session2 = create_engine_and_sessionmaker_for_sqlite_path(db_path)
                db_session = Session2()
                created_session = True
            except Exception:
                db_session = self.session
        try:
            # Preload locations by name
            locs = db_session.query(Location).filter_by(project_id=project_id).all()
            name_to_loc = { (getattr(l, 'name', '') or '').strip(): l for l in locs }
            # Clear existing rows
            db_session.query(LocationTableCallout).filter_by(project_id=project_id).delete(synchronize_session=False)
            # Insert new ones
            for loc_name, rows in (data or {}).items():
                if loc_name is None:
                    loc_key = ""
                else:
                    loc_key = str(loc_name).strip()
                loc_obj = name_to_loc.get(loc_key)
                if loc_obj is None:
                    # Create missing location row
                    loc_obj = Location(name=loc_key, project_id=project_id)
                    db_session.add(loc_obj)
                    db_session.flush()
                    name_to_loc[loc_key] = loc_obj
                for r in rows or []:
                    try:
                        t = (r.get("Type") if isinstance(r, dict) else getattr(r, 'type', None)) or ""
                        tag = (r.get("Tag") if isinstance(r, dict) else getattr(r, 'tag', None)) or ""
                        desc = (r.get("Description") if isinstance(r, dict) else getattr(r, 'description', None))
                        obj = LocationTableCallout(project_id=project_id, location_id=getattr(loc_obj, 'id', None))
                        # Map fields
                        setattr(obj, 'type', str(t) if t is not None else "")
                        setattr(obj, 'tag', str(tag) if tag is not None else "")
                        setattr(obj, 'description', str(desc) if desc is not None else None)
                        # Optional material from dict
                        try:
                            mat = r.get("Name") if isinstance(r, dict) else getattr(r, 'name', None)
                            if mat is not None:
                                setattr(obj, 'material', str(mat))
                        except Exception:
                            pass
                        db_session.add(obj)
                    except Exception:
                        continue
            db_session.commit()
            return True
        except Exception as e:  # pragma: no cover
            try:
                db_session.rollback()
            except Exception:
                pass
            try:
                self._logger.warning("replace_location_tables_for_project failed: %s", e)
            except Exception:
                pass
            return False
        finally:
            try:
                if created_session:
                    db_session.close()
            except Exception:
                pass
