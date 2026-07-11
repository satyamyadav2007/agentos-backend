import httpx
from typing import Dict, Any, Optional

class SlackClient:
    """Centralized HTTP Client for Slack Web API."""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://slack.com/api"
        self.timeout = httpx.Timeout(20.0)

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
            data = response.json()
            if not data.get("ok"):
                print(f"⚠️ [Slack API Error]: {data.get('error')}")
            return data

    async def post(self, endpoint: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=self._headers, json=json_data)
            response.raise_for_status()
            return response.json()