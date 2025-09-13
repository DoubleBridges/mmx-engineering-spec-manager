import pytest
from unittest.mock import mock_open, patch
from mmx_engineering_spec_manager.importers.callout_importer import CalloutImporter
import json

def test_callout_importer_parses_json_correctly(mocker):
    """
    Test that the CalloutImporter can parse the JSON data and return a clean list with correct types.
    """
    mock_json_data = {
        "DO_NOT_EDIT": True,
        "d": [
            ["SPECIFICATIONS", "", "", "David Kane", "8/14/2025"],
            ["FINISHES", "", "", "David Kane", "8/14/2025"],
            ["PLAM", "PL1", "NEVAMAR VA 7002 COOL CHIC", "David Kane", "8/14/2025"],
            ["PLAM", "PL2", "WILSONART 15515-31 NILE VELVET TRACELESS, 0.5 MIL PVC EB, WHITE MCP INTERIOR", "David Kane", "8/14/2025"],
            ["HARDWARE", "", "", "David Kane", "8/14/2025"],
            ["PULL", "CP1", "MOCKETT D254A 94", "David Kane", "8/14/2025"],
            ["LOCKS", "HW11", "GOKEYLESS 7850S-CHROME, KEYLESS CAM", "David Kane", "8/14/2025"],
            ["SINKS", "", "", "David Kane", "8/14/2025"],
            ["SINK", "SK1", "TBD, ARCH/GC PLEASE SPECIFY, 14 24", "David Kane", "8/14/2025"],
            ["APPLIANCES", "", "", "David Kane", "8/14/2025"],
            ["MICROWAVE", "AP1", "TBD, ARCH/GC PLEASE SPECIFY, 19", "David Kane", "8/14/2025"],
        ]
    }

    expected_callouts = [
        {"material": "PLAM", "tag": "PL1", "description": "NEVAMAR VA 7002 COOL CHIC", "type": "FINISHES"},
        {"material": "PLAM", "tag": "PL2", "description": "WILSONART 15515-31 NILE VELVET TRACELESS, 0.5 MIL PVC EB, WHITE MCP INTERIOR", "type": "FINISHES"},
        {"material": "PULL", "tag": "CP1", "description": "MOCKETT D254A 94", "type": "HARDWARE"},
        {"material": "LOCKS", "tag": "HW11", "description": "GOKEYLESS 7850S-CHROME, KEYLESS CAM", "type": "HARDWARE"},
        {"material": "SINK", "tag": "SK1", "description": "TBD, ARCH/GC PLEASE SPECIFY, 14 24", "type": "SINKS"},
        {"material": "MICROWAVE", "tag": "AP1", "description": "TBD, ARCH/GC PLEASE SPECIFY, 19", "type": "APPLIANCES"},
    ]

    # Use mocker to simulate reading a file
    mocker.patch('builtins.open', new=mock_open(read_data=json.dumps(mock_json_data)))
    mocker.patch('json.load', return_value=mock_json_data)

    importer = CalloutImporter()
    callouts = importer.parse_json_file("dummy_path.json")
    print(callouts)

    assert callouts == expected_callouts