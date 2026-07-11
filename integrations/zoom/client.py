import httpx
from typing import Dict, Any, Optional

class ZoomClient:
    """Centralized HTTP Client for Zoom API v2."""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.zoom.us/v2"
        self.timeout = httpx.Timeout(30.0)
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
            
    async def download_transcript(self, download_url: str) -> str:
        """Downloads the VTT/TXT transcript file from Zoom Cloud."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(download_url, headers=self.headers)
            response.raise_for_status()
            return response.text # Raw transcript text