import pytest
from mmx_engineering_spec_manager.models.microvellum_model import ProjectModel
from mmx_engineering_spec_manager.models.location_model import LocationModel
from mmx_engineering_spec_manager.models.prompt_model import PromptModel
from mmx_engineering_spec_manager.models.wall_model import WallModel
from mmx_engineering_spec_manager.models.product_model import ProductModel

def test_project_model_creation():
    """
    Test that the ProjectModel can be created with basic properties.
    """
    # Create an instance of the ProjectModel
    project_data = {
        "Name": "Test Project",
        "JobNumber": "98765"
    }
    project = ProjectModel(project_data)

    # Assert that the properties were set correctly
    assert project.name == "Test Project"
    assert project.job_number == "98765"
    assert project.category is None

def test_project_model_all_properties():
    """
    Test that all ProjectModel properties can be set and are accessible.
    """
    project_data = {
        "Name": "Full Project Test",
        "JobDescription": "A complete project example.",
        "JobNumber": "MV123",
        "Category": "Estimates",
        "JobAddress": "123 Main St.",
        "JobPhone": "555-123-4567",
        "JobFax": "555-987-6543",
        "JobEmail": "test@example.com"
    }

    project = ProjectModel(project_data)

    assert project.name == "Full Project Test"
    assert project.job_description == "A complete project example."
    assert project.job_number == "MV123"
    assert project.category == "Estimates"
    assert project.job_address == "123 Main St."
    assert project.job_phone == "555-123-4567"
    assert project.job_fax == "555-987-6543"
    assert project.job_email == "test@example.com"

def test_project_model_empty_collections():
    """
    Test that the ProjectModel can be created with empty collections.
    """
    project_data = {}
    project = ProjectModel(project_data)

    assert project.locations == []
    assert project.walls == []
    assert project.products == []

def test_project_model_with_locations():
    """
    Test that the ProjectModel can be created with a list of LocationModels.
    """
    project_data = {
        "Locations": [
            {"Name": "Kitchen"},
            {"Name": "Bathroom"}
        ]
    }
    project = ProjectModel(project_data)

    assert len(project.locations) == 2
    assert isinstance(project.locations[0], LocationModel)
    assert project.locations[0].name == "Kitchen"
    assert project.locations[1].name == "Bathroom"

def test_project_model_with_walls():
    """
    Test that the ProjectModel can be created with a list of WallModels.
    """
    project_data = {
        "Walls": [
            {
                "LinkID": "BPWALL.Wall.001",
                "LinkIDLocation": "Phase One",
                "Width": 120,
                "Height": 108.0,
                "Depth": 6.0,
                "XOrigin": -2.69925,
                "YOrigin": 344.76264,
                "ZOrigin": 0.0,
                "Angle": 0
            },
            {
                "LinkID": "BPWALL.Wall.002",
                "LinkIDLocation": "Phase One",
                "Width": 132.45931982369,
                "Height": 108.0,
                "Depth": 6.0,
                "XOrigin": 117.30075,
                "YOrigin": 344.76264,
                "ZOrigin": 0.0,
                "Angle": 320.09654468120192
            }
        ]
    }
    project = ProjectModel(project_data)

    assert len(project.walls) == 2
    assert isinstance(project.walls[0], WallModel)
    assert project.walls[0].link_id == "BPWALL.Wall.001"
    assert project.walls[1].link_id == "BPWALL.Wall.002"
    assert project.walls[1].width == 132.45931982369

def test_project_model_with_products():
    """
    Test that the ProjectModel can be created with a list of ProductModels.
    """
    project_data = {
        "Products": [
            {
                "Name": "1 Door Base",
                "Quantity": 1,
                "Width": 18,
                "Height": 34.5,
                "Depth": 23.125,
                "ItemNumber": "1.01",
                "Comment": "Test comment1|Test Comment2|Test Comment3",
                "Angle": 0,
                "XOrigin": 48.30075,
                "YOrigin": 344.76264,
                "ZOrigin": 0,
                "LinkIDSpecificationGroup": "Veneer",
                "LinkIDLocation": "Phase One",
                "LinkIDWall": "BPWALL.Wall.001",
                "Prompts": [
                    {
                        "Name": "Fixed_Shelf_Qty",
                        "Value": "=2+2"
                    },
                    {
                        "Name": "Shelf_Qtys",
                        "Value": "=4+4"
                    }
                ]
            }
        ]
    }
    project = ProjectModel(project_data)

    assert len(project.products) == 1
    assert isinstance(project.products[0], ProductModel)
    assert project.products[0].name == "1 Door Base"
    assert len(project.products[0].prompts) == 2
    assert isinstance(project.products[0].prompts[0], PromptModel)
    assert project.products[0].prompts[0].name == "Fixed_Shelf_Qty"
    assert project.products[0].prompts[0].value == "=2+2"