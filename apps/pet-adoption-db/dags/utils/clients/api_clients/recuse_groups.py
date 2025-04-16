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
        url = f"{self.base_url}/orgs/{organization_id}"

        print(f"Fetching organization with ID: {organization_id}")
        print(f"Using URL: {url}")

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json().get("data", [])[0]
        else:
            raise Exception(f"Failed to fetch organization: {response.status_code} - {response.text}")

    def fetch_breed_by_id(self, breed_id):
        """Fetch breed details by ID."""
        url = f"{self.base_url}/animals/breeds/{breed_id}"

        print(f"Fetching breed with ID: {breed_id}")
        print(f"Using URL: {url}")

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()["data"][0]
        else:
            raise Exception(f"Failed to fetch breed: {response.status_code} - {response.text}")
