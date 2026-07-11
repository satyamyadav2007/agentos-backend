import httpx
from typing import Dict, Any, Optional

class TeamsGraphClient:
    """Centralized HTTP Client for Microsoft Graph API (Teams)."""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.timeout = httpx.Timeout(20.0)
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()