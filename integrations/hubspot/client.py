import httpx
from typing import Dict, Any, Optional

class HubSpotClient:
    """Centralized HTTP Client for HubSpot CRM API v3."""
    
    def __init__(self, access_token: str):
        self.base_url = "https://api.hubapi.com/crm/v3"
        self.timeout = httpx.Timeout(20.0)
        self.access_token = access_token

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self._headers, params=params)
            response.raise_for_status()
            return response.json()