from pathlib import Path

from mmx_engineering_spec_manager.utilities import callout_import as co


def test_parse_json_callouts_with_d_section_format():
    # Use the provided example JSON which uses the {"d": [...]} structure with headers
    root = Path(__file__).resolve().parents[2]
    json_path = root / "example_data" / "innergy" / "json" / "Material Legend JSON 09-02-2025 2_01_04 PM.json"

    dtos = co.parse_json_callouts(str(json_path))

    # Basic assertions
    assert isinstance(dtos, list)
    assert len(dtos) > 0
    # Ensure all entries are CalloutDTO-like
    for d in dtos:
        assert hasattr(d, "name") and hasattr(d, "tag") and hasattr(d, "description") and hasattr(d, "type")

    # Group and ensure multiple categories are present
    grouped = co.group_callouts(dtos)
    # Expect at least one Finish based on the fixture data (PL1 etc.)
    assert len(grouped["Finishes"]) >= 1
    # The example JSON also has Hardware, Sinks, and Appliances sections
    assert len(grouped["Hardware"]) >= 1
    assert len(grouped["Sinks"]) >= 1
    assert len(grouped["Appliances"]) >= 1
