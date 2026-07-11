import httpx
from typing import Dict, Any, Optional

class SalesforceClient:
    """Centralized HTTP Client for Salesforce REST API & SOQL."""
    
    def __init__(self, instance_url: str, access_token: str, api_version: str = "v58.0"):
        self.instance_url = instance_url
        self.base_url = f"{instance_url.rstrip('/')}/services/data/{api_version}"
        self.timeout = httpx.Timeout(30.0)
        self.access_token = access_token

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def query(self, soql: str) -> Dict[str, Any]:
        """Executes a SOQL query to fetch targeted data."""
        url = f"{self.base_url}/query/"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self._headers, params={"q": soql})
            response.raise_for_status()
            return response.json()

    async def get(self, endpoint: str) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self._headers)
            response.raise_for_status()
            return response.json()