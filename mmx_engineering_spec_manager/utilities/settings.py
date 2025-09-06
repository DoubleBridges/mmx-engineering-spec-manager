from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from PySide6.QtCore import QStandardPaths

from .persistence import default_sqlite_db_path, get_database_url

# Load .env if present
load_dotenv()


def _app_data_dir() -> str:
    data_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    return data_dir


@dataclass(frozen=True)
class Settings:
    # Innergy / Importer settings
    innergy_api_key: Optional[str]
    innergy_base_url: str

    # Database settings
    database_url: str

    # Exporter settings (optional for MVP)
    microvellum_xml_template_path: Optional[str] = None
    xlsx_template_path: Optional[str] = None

    # General app paths
    app_data_dir: str = ""


_settings_singleton: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings_singleton
    if _settings_singleton is not None:
        return _settings_singleton

    app_data = _app_data_dir()

    # Resolve values from environment with sensible defaults
    innergy_api_key = os.getenv("INNERGY_API_KEY")
    innergy_base_url = os.getenv("INNERGY_BASE_URL", "https://app.innergy.com").rstrip("/")

    # Use the persistence helper for DB URL resolution (keeps compatibility)
    database_url = os.getenv("DATABASE_URL") or get_database_url()

    microvellum_xml_template_path = os.getenv("MICROVELLUM_XML_TEMPLATE_PATH")
    xlsx_template_path = os.getenv("XLSX_TEMPLATE_PATH")

    _settings_singleton = Settings(
        innergy_api_key=innergy_api_key,
        innergy_base_url=innergy_base_url,
        database_url=database_url,
        microvellum_xml_template_path=microvellum_xml_template_path,
        xlsx_template_path=xlsx_template_path,
        app_data_dir=app_data,
    )
    return _settings_singleton
