from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, Any, Iterable

from sqlalchemy.orm import sessionmaker

from mmx_engineering_spec_manager.importers.innergy_adapter import InnergyProjectImporterAdapter
from mmx_engineering_spec_manager.importers.contracts import ProjectImporter
from mmx_engineering_spec_manager.mappers.innergy_mapper import map_project_payload_to_dto
from mmx_engineering_spec_manager.dtos.ingest_dto import IngestProjectDTO
from mmx_engineering_spec_manager.repositories.unit_of_work import SqlAlchemyUnitOfWork
from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.db_models.location import Location
from mmx_engineering_spec_manager.db_models.product import Product
from mmx_engineering_spec_manager.db_models.custom_field import CustomField
from mmx_engineering_spec_manager.utilities.persistence import create_engine_and_sessionmaker


@dataclass
class IngestResult:
    project: Project
    ingest_dto: IngestProjectDTO


class IngestInnergyProjectService:
    """
    Application-layer service that ingests a full project from Innergy using the adapter/importer,
    maps it to DTOs, and persists via Unit of Work.
    """

    def __init__(
        self,
        session_factory: sessionmaker,
        importer: Optional[ProjectImporter] = None,
    ) -> None:
        self._session_factory = session_factory
        self._importer = importer or InnergyProjectImporterAdapter()

    def ingest(self, job_id: Any) -> IngestResult:
        # Fetch payloads via importer
        project_payload = self._importer.fetch_project(job_id)
        products_payload: Optional[Iterable[dict]] = self._importer.fetch_products(job_id) or []

        # Map to DTOs
        dto = map_project_payload_to_dto(project_payload, products_payload)
        ingest_dto = IngestProjectDTO(
            project=dto,
            source="innergy",
            raw_project_payload=project_payload,
            raw_products_payload=list(products_payload) if products_payload is not None else None,
        )

        # Persist via UoW
        uow = SqlAlchemyUnitOfWork(self._session_factory)
        with uow as tx:
            # Upsert project by number
            existing = tx.projects.get_by_number(dto.number)
            if existing:
                existing.name = dto.name
                existing.job_description = dto.job_description
                # If model has job_address, set it
                if hasattr(existing, "job_address"):
                    setattr(existing, "job_address", dto.job_address)
                project = existing
            else:
                project = Project(
                    number=dto.number,
                    name=dto.name,
                    job_description=dto.job_description,
                    **({"job_address": dto.job_address} if hasattr(Project, "job_address") else {})
                )
                tx.projects.add(project)
                # Flush to get id for relationships (if session supports)
                tx.session.flush()

            # Locations
            if dto.locations:
                # For simplicity, append locations not already present by name
                existing_names = {getattr(l, "name", None) for l in getattr(project, "locations", [])}
                for loc_dto in dto.locations:
                    if loc_dto.name and loc_dto.name not in existing_names:
                        loc = Location(name=loc_dto.name, project=project)
                        tx.session.add(loc)

            # Products
            if dto.products:
                for p_dto in dto.products:
                    prod = Product(
                        name=p_dto.name,
                        quantity=p_dto.quantity,
                        project=project,
                    )
                    tx.session.add(prod)
                    # Custom fields for product
                    for cf in (p_dto.custom_fields or []):
                        tx.session.add(CustomField(name=cf.name, value=cf.value, product=prod))

            # Commit
            tx.commit()

            # Ensure 'project' is attached and returned
            return IngestResult(project=project, ingest_dto=ingest_dto)


def build_default_ingest_service() -> IngestInnergyProjectService:
    """Helper to construct a default service with the app's engine and sessionmaker."""
    _, Session = create_engine_and_sessionmaker()
    return IngestInnergyProjectService(session_factory=Session)
