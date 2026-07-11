import httpx
from typing import Dict, Any, Optional

class IntercomClient:
    """Centralized HTTP Client for Intercom API."""
    
    def __init__(self, access_token: str, api_version: str = "2.10"):
        self.base_url = "https://api.intercom.io"
        self.timeout = httpx.Timeout(20.0)
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Intercom-Version": api_version
        }

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()