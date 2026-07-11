import httpx
from typing import Dict, Any, Optional

class CommunityClient:
    """Centralized HTTP Client for Community Forums (e.g., Discourse)."""
    
    def __init__(self, api_key: str, domain: str):
        self.api_key = api_key
        # Ensure clean domain format
        clean_domain = domain.replace("https://", "").replace("http://", "").rstrip('/')
        self.base_url = f"https://{clean_domain}"
        self.timeout = httpx.Timeout(20.0)
        
        self.headers = {
            "Api-Key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()