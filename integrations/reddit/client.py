import httpx
from typing import Dict, Any, Optional

class RedditClient:
    """Centralized HTTP Client for Reddit OAuth API."""
    
    def __init__(self, access_token: str):
        self.base_url = "https://oauth.reddit.com"
        self.timeout = httpx.Timeout(20.0)
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "AgentOS Intelligence Engine/1.0.0 (by /u/satyam_founder)"
        }

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()