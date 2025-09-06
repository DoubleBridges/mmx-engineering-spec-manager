from pathlib import Path
import pytest
from PySide6.QtWidgets import QTabWidget

from mmx_engineering_spec_manager.views.main_window import MainWindow
from mmx_engineering_spec_manager.views.attributes.attributes_tab import AttributesTab


def test_main_window_has_attributes_tab(qtbot):
    mw = MainWindow()
    qtbot.addWidget(mw)

    tab_widget = mw.findChild(QTabWidget)
    assert tab_widget is not None

    labels = [tab_widget.tabText(i) for i in range(tab_widget.count())]
    assert "Projects" in labels
    assert "Attributes" in labels
    assert "Workspace" in labels
    # Ensure Attributes comes between Projects and Workspace
    p_idx = labels.index("Projects")
    a_idx = labels.index("Attributes")
    w_idx = labels.index("Workspace")
    assert p_idx < a_idx < w_idx


def test_attributes_tab_loads_csv_and_json(qtbot):
    tab = AttributesTab()
    qtbot.addWidget(tab)

    root = Path(__file__).resolve().parents[2]
    csv_path = root / "example_data" / "innergy" / "csv" / "NMMC CSV.csv"
    json_path = root / "example_data" / "innergy" / "json" / "Material Legend JSON 09-02-2025 2_01_04 PM.json"

    # Load CSV
    tab.load_from_path(str(csv_path))
    rows = tab.current_rows()
    assert isinstance(rows, list)
    assert len(rows) >= 1
    model = tab.table.model()
    assert model is not None and model.rowCount() >= 1

    # Load JSON
    tab.load_from_path(str(json_path))
    rows2 = tab.current_rows()
    assert isinstance(rows2, list)
    assert len(rows2) >= 1
    model2 = tab.table.model()
    assert model2 is not None and model2.rowCount() >= 1
