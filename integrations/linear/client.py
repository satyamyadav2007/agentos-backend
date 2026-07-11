import httpx
from typing import Dict, Any, Optional

class LinearClient:
    """Centralized HTTP Client for Linear GraphQL API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.linear.app/graphql"
        self.timeout = httpx.Timeout(20.0)
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }

    async def execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
            
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            if "errors" in data:
                raise Exception(f"Linear GraphQL Error: {data['errors']}")
                
            return data.get("data", {})