import httpx
from typing import Dict, Any, Optional

class TwitterClient:
    """Centralized HTTP Client for Twitter/X API v2."""
    
    def __init__(self, bearer_token: str):
        self.bearer_token = bearer_token
        self.base_url = "https://api.twitter.com/2"
        self.timeout = httpx.Timeout(20.0)
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
