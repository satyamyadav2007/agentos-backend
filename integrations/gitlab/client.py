import httpx
from typing import Dict, Any, Optional

class GitLabClient:
    """Centralized HTTP Client for GitLab REST API v4."""
    
    def __init__(self, token: str, host: str = "https://gitlab.com"):
        self.token = token
        # Strip trailing slash and append API v4 path
        self.base_url = f"{host.rstrip('/')}/api/v4"
        self.timeout = httpx.Timeout(20.0)
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            # GitLab returns lists directly for many endpoints, so we handle both dict and list
            data = response.json()
            return {"data": data} if isinstance(data, list) else data