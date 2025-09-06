import os
from unittest.mock import Mock
import requests

from mmx_engineering_spec_manager.importers.innergy import InnergyImporter
from mmx_engineering_spec_manager.utilities import settings as settings_module


def test_innergy_base_url_normalization_www_and_api(monkeypatch):
    # www -> app
    monkeypatch.setenv('INNERGY_BASE_URL', 'https://www.innergy.com/')
    settings_module._settings_singleton = None
    imp1 = InnergyImporter()
    assert imp1.base_url == 'https://app.innergy.com'

    # api -> app
    monkeypatch.setenv('INNERGY_BASE_URL', 'https://api.innergy.com/')
    settings_module._settings_singleton = None
    imp2 = InnergyImporter()
    assert imp2.base_url == 'https://app.innergy.com'


def test_get_projects_raw_returns_status_and_text(monkeypatch):
    # Ensure a deterministic base URL
    monkeypatch.setenv('INNERGY_BASE_URL', 'https://app.innergy.com')
    settings_module._settings_singleton = None

    mock_resp = Mock()
    mock_resp.status_code = 202
    mock_resp.text = '{"ok": true}'
    monkeypatch.setattr(requests, 'get', lambda url, headers=None: mock_resp)

    imp = InnergyImporter()
    raw = imp.get_projects_raw()
    assert raw['status_code'] == 202
    assert 'ok' in raw['text']
