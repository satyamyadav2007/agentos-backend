import httpx
import base64
from typing import Dict, Any, Optional

class ZendeskClient:
    """Centralized HTTP Client for Zendesk API."""
    
    def __init__(self, subdomain: str, access_token: str, is_oauth: bool = True):
        self.subdomain = subdomain
        self.base_url = f"https://{subdomain}.zendesk.com/api/v2"
        self.timeout = httpx.Timeout(20.0)
        
        # Zendesk supports both OAuth and API Token (Email/Token)
        if is_oauth:
            self.auth_header = f"Bearer {access_token}"
        else:
            # Fallback for Enterprise API Tokens: base64(email/token:api_token)
            self.auth_header = f"Basic {access_token}"

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": self.auth_header,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self._headers, params=params)
            response.raise_for_status()
            return response.json()