import os
import httpx
from typing import Dict, Any, Tuple

class JiraAuthManager:
    """Handles Atlassian 3LO (OAuth 2.0) flow and Cloud ID discovery."""
    
    def __init__(self):
        self.client_id = os.getenv("JIRA_CLIENT_ID")
        self.client_secret = os.getenv("JIRA_CLIENT_SECRET")
        self.callback_url = os.getenv("JIRA_CALLBACK_URL")

    async def exchange_code_for_token(self, auth_code: str) -> str:
        """Exchanges the authorization code for an Access Token."""
        url = "https://auth.atlassian.com/oauth/token"
        payload = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": auth_code,
            "redirect_uri": self.callback_url
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                raise Exception(f"Jira OAuth Token Exchange Failed: {response.text}")
                
            return response.json()["access_token"]

    async def get_accessible_resources(self, access_token: str) -> list:
        """
        Fetches the Cloud IDs (Workspaces) the user granted access to.
        Atlassian requires this Cloud ID to make API calls.
        """
        url = "https://api.atlassian.com/oauth/token/accessible-resources"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                raise Exception("Failed to fetch Jira accessible resources.")
                
            return response.json()

    async def authenticate(self, auth_code: str) -> Tuple[str, str, str]:
        """Runs the full auth flow and returns (token, cloud_id, site_url)."""
        print("🔐 [Jira Auth] Starting token exchange...")
        
        token = await self.exchange_code_for_token(auth_code)
        resources = await self.get_accessible_resources(token)
        
        if not resources:
            raise Exception("No Jira workspaces found for this token.")
            
        # ⚡ FIX: Filter explicitly for Jira resource instead of blindly taking index 0
        jira_resource = next((r for r in resources if "jira" in r.get("scopes", []) or r.get("avatarUrl")), None)
        
        if not jira_resource:
            # Fallback in case specific markers aren't present
            jira_resource = resources[0]
            
        cloud_id = jira_resource["id"]
        site_url = jira_resource["url"]
        site_name = jira_resource.get("name", site_url)
        
        print(f"✅ [Jira Auth] Cloud ID verified: {cloud_id} for site: {site_name}")
        
        return token, cloud_id, site_url