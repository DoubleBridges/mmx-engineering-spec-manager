import requests


class InnergyImporter:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.innergy.com"

    def get_job_details(self):
        url = f"{self.base_url}/jobs/12345"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(url, headers=headers)
        return response