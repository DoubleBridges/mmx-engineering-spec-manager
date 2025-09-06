import os
import importlib

from mmx_engineering_spec_manager.utilities import settings as settings_module
from mmx_engineering_spec_manager.utilities.persistence import get_database_url


def _reset_settings_singleton():
    # Reset the module-level singleton for deterministic tests
    settings_module._settings_singleton = None  # type: ignore[attr-defined]


def test_settings_env_overrides(monkeypatch, tmp_path):
    monkeypatch.setenv("INNERGY_API_KEY", "TESTKEY")
    monkeypatch.setenv("INNERGY_BASE_URL", "https://example.com")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("MICROVELLUM_XML_TEMPLATE_PATH", str(tmp_path / "mv.xml"))
    monkeypatch.setenv("XLSX_TEMPLATE_PATH", str(tmp_path / "tmpl.xlsx"))

    _reset_settings_singleton()
    s = settings_module.get_settings()

    assert s.innergy_api_key == "TESTKEY"
    assert s.innergy_base_url == "https://example.com"
    assert s.database_url == "sqlite:///:memory:"
    assert s.microvellum_xml_template_path.endswith("mv.xml")
    assert s.xlsx_template_path.endswith("tmpl.xlsx")
    assert isinstance(s.app_data_dir, str) and s.app_data_dir != ""


def test_settings_defaults_consistent_with_persistence(monkeypatch):
    # Remove env vars to force defaults
    for key in [
        "INNERGY_API_KEY",
        "INNERGY_BASE_URL",
        "DATABASE_URL",
        "MICROVELLUM_XML_TEMPLATE_PATH",
        "XLSX_TEMPLATE_PATH",
    ]:
        monkeypatch.delenv(key, raising=False)

    _reset_settings_singleton()
    s = settings_module.get_settings()

    assert s.innergy_base_url == "https://api.innergy.com"
    # database_url should equal the persistence helper's resolution
    assert s.database_url == get_database_url()
    # Optional paths default to None
    assert s.microvellum_xml_template_path is None
    assert s.xlsx_template_path is None
