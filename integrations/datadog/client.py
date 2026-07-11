import httpx
from typing import Dict, Any, Optional

class DatadogClient:
    """Centralized HTTP Client for Datadog API."""
    
    def __init__(self, api_key: str, app_key: str, site: str = "datadoghq.com"):
        self.api_key = api_key
        self.app_key = app_key
        # Datadog has different regions (e.g., datadoghq.eu, us3.datadoghq.com)
        self.base_url = f"https://api.{site}/api/v1"
        self.timeout = httpx.Timeout(20.0)
        
        self.headers = {
            "DD-API-KEY": self.api_key,
            "DD-APPLICATION-KEY": self.app_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()