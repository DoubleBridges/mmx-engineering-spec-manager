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
        # Normalize base URL to the API host for predictable behavior in tests and runtime
        try:
            if isinstance(self.base_url, str):
                bu = self.base_url.rstrip("/")
                # Force API subdomain for consistency
                if "innergy.com" in bu:
                    if "://www." in bu:
                        bu = bu.replace("://www.", "://app.", 1)
                    elif "://api." in bu:
                        bu = bu.replace("://api.", "://app.", 1)
                self.base_url = bu
        except Exception:  # pragma: no cover
            pass
        self._logger = get_logger(__name__)

    def _headers(self):
        """Return headers expected by Innergy API (per Postman screenshot).
        Uses custom API-KEY header rather than Authorization.
        """
        return {
            "API-KEY": str(self.api_key) if self.api_key is not None else "",
            "Accept": "*/*",
            "Connection": "keep-alive",
        }

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
            payload = response.json()
            # Place a breakpoint here to inspect 'payload' and payload.get("Items")
            items = payload.get("Items", [])
            for item in items:
                # Include only projects with active status (case-insensitive). Status may be a string or a dict with Name.
                status_val = item.get("Status")
                is_active = False
                if isinstance(status_val, str):
                    is_active = status_val.strip().lower() == "open"
                elif isinstance(status_val, dict):
                    name = status_val.get("Name") or status_val.get("name")
                    if isinstance(name, str):
                        is_active = name.strip().lower() == "active"
                if not is_active:
                    continue
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

    def get_projects_raw(self):
        """Return raw HTTP response content and status from projects endpoint for debugging/log display."""
        url = f"{self.base_url}/api/projects"
        response = requests.get(url, headers=self._headers())
        try:
            text = response.text
        except Exception:
            text = "<no text>"
        return {"status_code": getattr(response, "status_code", None), "text": text}

    def get_products(self, job_id):
        url = f"{self.base_url}/api/projects/{job_id}/budgetProducts"
        response = requests.get(url, headers=self._headers())
        if response.status_code == 200:
            filtered_products = []
            for item in response.json().get("Items", []):
                # Only return the minimal set required by consumers/tests
                custom_fields = []
                for cf in item.get("CustomFields", []) or []:
                    custom_fields.append({"Name": cf.get("Name"), "Value": cf.get("Value")})
                product_data = {
                    "Name": item.get("Name"),
                    "QuantCount": item.get("QuantCount"),
                    "Description": item.get("Description"),
                    "CustomFields": custom_fields,
                }
                filtered_products.append(product_data)
            return filtered_products
        self._logger.warning("Innergy get_products non-200: %s", response.status_code)
        return None

    def get_products_raw(self, job_id):
        """Return the full JSON payload from the budgetProducts endpoint for a job.
        This preserves fields like Location, dimensions, origins, link IDs, etc.,
        for callers that need extended attributes.
        """
        url = f"{self.base_url}/api/projects/{job_id}/budgetProducts"
        response = requests.get(url, headers=self._headers())
        if response.status_code == 200:
            try:
                return response.json()
            except Exception:
                return None
        self._logger.warning("Innergy get_products_raw non-200: %s", response.status_code)
        return None