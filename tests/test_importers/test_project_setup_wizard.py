import pytest
from mmx_engineering_spec_manager.importers.project_setup_wizard import ProjectSetupWizardImporter


def test_project_setup_wizard_importer_returns_clean_data():
    """
    Test that the ProjectSetupWizardImporter returns a clean, filtered dictionary.
    """
    form_data = {
        "job_number": "101",
        "name": "New Project",
        "job_description": "A complete project example.",
    }

    expected_data = {
        "job_number": "101",
        "name": "New Project",
        "job_description": "A complete project example.",
    }

    importer = ProjectSetupWizardImporter()
    project_data = importer.get_project_data(form_data)

    assert project_data == expected_data