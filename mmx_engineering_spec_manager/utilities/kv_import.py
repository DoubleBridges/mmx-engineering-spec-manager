from __future__ import annotations
from typing import List, Dict, Any
import csv
import json
from pathlib import Path


def _ensure_list_of_dicts(obj: Any) -> List[Dict[str, Any]]:
    """
    Normalize arbitrary JSON-like content into a list of dict rows for tabular display.
    Cases handled:
    - list of dicts: return as-is
    - dict of dicts: return values as rows, using keys as an added column 'key'
    - dict of scalars: convert to rows with columns: key, value
    - scalar or other: return single-row list with {'value': str(obj)}
    """
    if isinstance(obj, list):
        # If list of dicts, good; else wrap values
        if obj and all(isinstance(it, dict) for it in obj):
            return obj  # type: ignore[return-value]
        return [{"value": item} for item in obj]
    if isinstance(obj, dict):
        # If values are dicts, add a 'key' column for original map key
        if obj and all(isinstance(v, dict) for v in obj.values()):
            rows: List[Dict[str, Any]] = []
            for k, v in obj.items():
                row = {"key": k}
                row.update(v)
                rows.append(row)
            return rows
        # Otherwise treat as key/value map
        return [{"key": k, "value": v} for k, v in obj.items()]
    # Fallback scalar
    return [{"value": obj}]


def read_csv(path: str | Path) -> List[Dict[str, Any]]:
    p = Path(path)
    with p.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def read_json(path: str | Path) -> List[Dict[str, Any]]:
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Try to salvage by wrapping the raw text
        return [{"value": text}]
    return _ensure_list_of_dicts(data)


def read_any(path: str | Path) -> List[Dict[str, Any]]:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix in (".csv", ".tsv"):
        return read_csv(p)
    if suffix in (".json", ".jsn"):
        return read_json(p)
    # Unknown: try JSON first then CSV
    try:
        return read_json(p)
    except Exception:
        return read_csv(p)
