import requests
import os

RC_API_KEY = os.getenv("RC_API_KEY")

class RescueGroupsClient:
    """A client for interacting with the Rescue Groups API."""

    def __init__(self):
        self.base_url = "https://api.rescuegroups.org/v5/public"
        self.api_key = RC_API_KEY
        self.headers = {
            "Authorization": f"{self.api_key}"
        }

    def fetch_organization_by_id(self, organization_id):
        """Fetch organization details by ID."""
        url = f"{self.base_url}/organizations/{organization_id}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch organization: {response.status_code} - {response.text}")
