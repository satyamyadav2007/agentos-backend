import httpx
import base64
from typing import Dict, Any, Optional

class FreshdeskClient:
    """Centralized HTTP Client for Freshdesk API v2."""
    
    def __init__(self, api_key: str, domain: str):
        self.api_key = api_key
        # Ensure clean domain format (e.g., yourcompany.freshdesk.com)
        clean_domain = domain.replace("https://", "").replace("http://", "").rstrip('/')
        self.base_url = f"https://{clean_domain}/api/v2"
        self.timeout = httpx.Timeout(20.0)
        
        # Freshdesk uses Basic Auth with the API key as username and 'X' as password
        auth_string = f"{self.api_key}:X"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        self.headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json"
        }

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            # Freshdesk often returns a list for index endpoints
            data = response.json()
            return {"data": data} if isinstance(data, list) else data