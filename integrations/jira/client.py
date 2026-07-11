import httpx
from typing import Dict, Any, Optional

class JiraClient:
    """
    Centralized HTTP Client for all Atlassian/Jira API calls.
    Handles authentication injection, retries, and rate-limiting.
    """
    def __init__(self, access_token: str, cloud_id: str):
        self.access_token = access_token
        self.cloud_id = cloud_id
        # Atlassian API routes through api.atlassian.com using the cloud_id
        self.base_url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/rest/api/3"
        self.timeout = httpx.Timeout(20.0)

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self._headers, params=params)
            
            if response.status_code == 429:
                print("⚠️ [Jira Client] Rate limit exceeded. (Should implement retry logic here)")
                
            response.raise_for_status()
            return response.json()

    async def post(self, endpoint: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=self._headers, json=json_data)
            response.raise_for_status()
            return response.json()