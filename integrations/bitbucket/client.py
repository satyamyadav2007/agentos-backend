import httpx
import base64
from typing import Dict, Any, Optional

class BitbucketClient:
    """Centralized HTTP Client for Bitbucket API v2.0."""
    
    def __init__(self, token: str, username: Optional[str] = None):
        self.token = token
        self.username = username
        self.base_url = "https://api.bitbucket.org/2.0"
        self.timeout = httpx.Timeout(20.0)
        
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # ⚡ Bitbucket supports both Basic Auth (Username + App Password) and Bearer (OAuth)
        if self.username:
            auth_string = f"{self.username}:{self.token}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            self.headers["Authorization"] = f"Basic {encoded_auth}"
        else:
            self.headers["Authorization"] = f"Bearer {self.token}"

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()