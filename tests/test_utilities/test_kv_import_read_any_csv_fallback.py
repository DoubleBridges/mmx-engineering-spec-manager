from pathlib import Path
from mmx_engineering_spec_manager.utilities import kv_import


def test_read_any_unknown_suffix_forces_csv_when_json_raises(monkeypatch, tmp_path: Path):
    # Prepare a CSV-like file with unknown suffix
    p = tmp_path / "rows.bin"
    p.write_text('a,b\n1,2\n', encoding='utf-8')

    # Force read_json to raise a generic Exception so read_any goes to CSV branch
    monkeypatch.setattr(kv_import, 'read_json', lambda path: (_ for _ in ()).throw(RuntimeError('boom')))

    rows = kv_import.read_any(p)
    assert rows and rows[0]['a'] == '1' and rows[0]['b'] == '2'
