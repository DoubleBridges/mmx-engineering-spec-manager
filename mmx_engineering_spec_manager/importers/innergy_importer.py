import requests
from dotenv import load_dotenv
import os

load_dotenv()


class InnergyImporter:
    def __init__(self):
        self.api_key = os.getenv("INNERGY_API_KEY")
        self.base_url = "https://api.innergy.com"

    def get_job_details(self, job_id):
        url = f"{self.base_url}/jobs/{job_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        return None