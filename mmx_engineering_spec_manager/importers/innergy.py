import os
import requests
from dotenv import load_dotenv

from mmx_engineering_spec_manager.utilities.settings import get_settings
from mmx_engineering_spec_manager.utilities.logging_config import get_logger

load_dotenv()


class InnergyImporter:
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.innergy_api_key
        self.base_url = settings.innergy_base_url
        self._logger = get_logger(__name__)

    def _headers(self):
        # Keep legacy behavior for tests: always include Authorization header even if key is None
        return {"Authorization": f"Bearer {self.api_key}"}

    def get_job_details(self, job_id):
        url = f"{self.base_url}/api/projects/{job_id}"
        response = requests.get(url, headers=self._headers())
        if response.status_code == 200:
            return response.json()
        self._logger.warning("Innergy get_job_details non-200: %s", response.status_code)
        return None

    def get_projects(self):
        url = f"{self.base_url}/api/projects"
        response = requests.get(url, headers=self._headers())
        if response.status_code == 200:
            filtered_projects = []
            for item in response.json().get("Items", []):
                project_data = {
                    "Id": item.get("Id"),
                    "Number": item.get("Number"),
                    "Name": item.get("Name", ""),
                    "Address": item.get("Address", "")
                }
                filtered_projects.append(project_data)
            return filtered_projects
        self._logger.warning("Innergy get_projects non-200: %s", response.status_code)
        return None

    def get_products(self, job_id):
        url = f"{self.base_url}/api/projects/{job_id}/budgetProducts"
        response = requests.get(url, headers=self._headers())
        if response.status_code == 200:
            filtered_products = []
            for item in response.json().get("Items", []):
                custom_fields = []
                if "CustomFields" in item:
                    for cf in item["CustomFields"]:
                        custom_fields.append({"Name": cf.get("Name"), "Value": cf.get("Value")})

                product_data = {
                    "Name": item.get("Name"),
                    "QuantCount": item.get("QuantCount"),
                    "Description": item.get("Description"),
                    "CustomFields": custom_fields
                }
                filtered_products.append(product_data)
            return filtered_products
        self._logger.warning("Innergy get_products non-200: %s", response.status_code)
        return None