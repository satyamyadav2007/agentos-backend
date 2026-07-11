import httpx
from typing import Dict, Any, Optional

class GitHubClient:
    """Centralized HTTP Client for GitHub REST & GraphQL API."""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.github.com"
        self.timeout = httpx.Timeout(20.0)

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self._headers, params=params)
            
            # Simple Rate Limit handling (Can be moved to utils/rate_limit.py later)
            if response.status_code == 403 and "rate limit" in response.text.lower():
                print("⚠️ [GitHub Client] Rate limit exceeded!")
                
            response.raise_for_status()
            return response.json()