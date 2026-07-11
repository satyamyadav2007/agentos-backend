import httpx
from typing import Dict, Any, Optional

class GA4Client:
    """Client for Google Analytics Data API v1beta."""
    
    def __init__(self, property_id: str, access_token: str):
        self.property_id = property_id
        self.access_token = access_token
        self.base_url = "https://analyticsdata.googleapis.com/v1beta"
        self.timeout = httpx.Timeout(30.0)
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    async def post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/properties/{self.property_id}:{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()