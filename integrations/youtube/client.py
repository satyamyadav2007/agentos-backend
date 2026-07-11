import httpx
from typing import Dict, Any, Optional

class YouTubeClient:
    """Centralized HTTP Client for YouTube Data API v3."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.timeout = httpx.Timeout(20.0)

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        if params is None:
            params = {}
        params["key"] = self.api_key  # Append API Key to every request
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()