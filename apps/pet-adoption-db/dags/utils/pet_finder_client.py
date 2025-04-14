import requests
import os

PF_CLIENT_ID = os.getenv("PF_CLIENT_ID")
PF_CLIENT_SECRET = os.getenv("PF_CLIENT_SECRET")

class PetFinderClient:
    """A client for interacting with the PetFinder API."""

    def __init__(self):
        self.base_url = "https://api.petfinder.com/v2"
        self.token = None
        self.authenticate()

    def authenticate(self):
        """Authenticate with the PetFinder API and retrieve an access token."""
        auth_url = f"{self.base_url}/oauth2/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": PF_CLIENT_ID,
            "client_secret": PF_CLIENT_SECRET,
        }
        response = requests.post(auth_url, data=payload)
        if response.status_code == 200:
            self.token = response.json().get("access_token")
        else:
            raise Exception(f"Authentication failed: {response.status_code} - {response.text}")

    def get_headers(self):
        """Return headers for API requests."""
        return {"Authorization": f"Bearer {self.token}"}

    def fetch_organization_by_id(self, organization_id):
        """Fetch organization details by ID."""
        url = f"{self.base_url}/organizations/{organization_id}"
        response = requests.get(url, headers=self.get_headers())

        if response.status_code == 401:  # Token expired
            self.authenticate()
            response = requests.get(url, headers=self.get_headers())

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch organization: {response.status_code} - {response.text}")
