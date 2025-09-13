from __future__ import annotations
from dataclasses import asdict
from typing import Iterable, List, Tuple
import csv
import json
from pathlib import Path

from mmx_engineering_spec_manager.dtos.callout_dto import CalloutDTO


TYPE_UNCATEGORIZED = "Uncategorized"
TYPE_FINISH = "Finish"
TYPE_HARDWARE = "Hardware"
TYPE_SINK = "Sink"
TYPE_APPLIANCE = "Appliance"

# Map tag two-letter prefixes to category
_PREFIX_TO_TYPE = {
    "PL": TYPE_FINISH,
    "PT": TYPE_FINISH,
    "PG": TYPE_FINISH,
    "WD": TYPE_FINISH,
    "ST": TYPE_FINISH,
    "SS": TYPE_FINISH,
    "HW": TYPE_HARDWARE,
    "BK": TYPE_HARDWARE,
    "SK": TYPE_SINK,
    "AP": TYPE_APPLIANCE,
}


def categorize_by_tag(tag: str) -> str:
    t = (tag or "").strip().upper()
    if len(t) >= 2:
        pref = t[:2]
        return _PREFIX_TO_TYPE.get(pref, TYPE_UNCATEGORIZED)
    return TYPE_UNCATEGORIZED


def _mk_dto(name: str, tag: str, description: str) -> CalloutDTO:
    ctype = categorize_by_tag(tag)
    return CalloutDTO(
        type=ctype,
        name=name.strip(),
        tag=tag.strip(),
        description=description.strip(),
    )


def parse_csv_callouts(path: str | Path) -> List[CalloutDTO]:
    p = Path(path)
    rows: List[CalloutDTO] = []
    with p.open(newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for idx, cols in enumerate(reader):
            if not cols:
                continue
            # Stick to first 3 cols: A,B,C
            a = (cols[0] if len(cols) > 0 else "").strip()
            b = (cols[1] if len(cols) > 1 else "").strip()
            c = (cols[2] if len(cols) > 2 else "").strip()
            # Skip header-like row if detected
            if idx == 0 and {a.lower(), b.lower(), c.lower()} <= {"name", "tag", "description"}:
                continue
            # Skip if any of first 3 cells empty
            if not a or not b or not c:
                continue
            rows.append(_mk_dto(a, b, c))
    return rows


def parse_json_callouts(path: str | Path) -> List[CalloutDTO]:
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    data = json.loads(text)
    if not isinstance(data, list):
        return []
    result: List[CalloutDTO] = []
    for item in data:
        if not isinstance(item, list) or len(item) < 3:
            continue
        a = (item[0] or "").strip() if isinstance(item[0], str) else str(item[0]).strip()
        b = (item[1] or "").strip() if isinstance(item[1], str) else str(item[1]).strip()
        c = (item[2] or "").strip() if isinstance(item[2], str) else str(item[2]).strip()
        if not a or not b or not c:
            continue
        result.append(_mk_dto(a, b, c))
    return result


def group_callouts(dtos: Iterable[CalloutDTO]) -> dict:
    groups = {
        "Finishes": [],
        "Hardware": [],
        "Sinks": [],
        "Appliances": [],
        "Uncategorized": [],
    }
    for dto in dtos:
        t = dto.type
        if t == TYPE_FINISH:
            groups["Finishes"].append(dto)
        elif t == TYPE_HARDWARE:
            groups["Hardware"].append(dto)
        elif t == TYPE_SINK:
            groups["Sinks"].append(dto)
        elif t == TYPE_APPLIANCE:
            groups["Appliances"].append(dto)
        else:
            groups["Uncategorized"].append(dto)
    return groups


def read_callouts(file_type: str, path: str | Path) -> List[CalloutDTO]:
    ft = (file_type or "").strip().lower()
    if ft == "csv":
        return parse_csv_callouts(path)
    if ft == "json":
        return parse_json_callouts(path)
    # Unknown type
    return []
