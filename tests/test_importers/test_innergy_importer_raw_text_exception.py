from mmx_engineering_spec_manager.importers.innergy import InnergyImporter
import requests


def test_get_projects_raw_handles_text_exception(monkeypatch):
    class _Resp:
        status_code = 200
        @property
        def text(self):
            raise RuntimeError('nope')
    monkeypatch.setattr(requests, 'get', lambda url, headers=None: _Resp())
    imp = InnergyImporter()
    raw = imp.get_projects_raw()
    assert raw['status_code'] == 200
    assert raw['text'] == '<no text>'
