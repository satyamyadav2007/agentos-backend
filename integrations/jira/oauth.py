import os
import httpx
from typing import Tuple


class JiraAuthManager:
    """Handles Atlassian OAuth 2.0 (3LO) authentication."""

    def __init__(self):
        self.client_id = os.getenv("JIRA_CLIENT_ID")
        self.client_secret = os.getenv("JIRA_CLIENT_SECRET")
        self.callback_url = os.getenv("JIRA_CALLBACK_URL")

    async def exchange_code_for_token(self, auth_code: str) -> str:
        """Exchange Authorization Code for Access Token"""

        print("\n================= TOKEN EXCHANGE =================")
        print("Client ID:", self.client_id)
        print("Redirect URI:", self.callback_url)
        print("Auth Code (first 25 chars):", auth_code[:25] if auth_code else "None")

        payload = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": auth_code,
            "redirect_uri": self.callback_url,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://auth.atlassian.com/oauth/token",
                json=payload,
            )

        print("Status Code:", response.status_code)
        print("Response Body:")
        print(response.text)
        print("=================================================\n")

        if response.status_code != 200:
            raise Exception(f"OAuth Token Exchange Failed: {response.text}")

        token_data = response.json()

        print("Scopes Returned:")
        print(token_data.get("scope"))
        print("=================================================\n")

        return token_data["access_token"]

    async def get_accessible_resources(self, access_token: str):
        """Returns Jira Cloud IDs"""

        print("\n============= ACCESSIBLE RESOURCES =============")
        print("Token (first 40 chars):", access_token[:40])

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://api.atlassian.com/oauth/token/accessible-resources",
                headers=headers,
            )

        print("Status Code:", response.status_code)
        print("Response:")
        print(response.text)
        print("===============================================\n")

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    async def authenticate(self, auth_code: str) -> Tuple[str, str, str]:

        print("🔐 Starting Jira Authentication...")

        token = await self.exchange_code_for_token(auth_code)

        resources = await self.get_accessible_resources(token)

        if not resources:
            raise Exception("No Jira resources found.")

        resource = resources[0]

        cloud_id = resource["id"]
        site_url = resource["url"]

        print("Cloud ID:", cloud_id)
        print("Site URL:", site_url)
        print("Scopes:")
        print(resource.get("scopes"))

        return token, cloud_id, site_url