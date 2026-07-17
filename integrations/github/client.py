import httpx
from typing import Dict, Any, Optional, Union, List

class GitHubClient:
    """Centralized HTTP Client for GitHub REST & GraphQL API."""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.github.com"
        # ⚡ Timeout thoda bada rakha hai taaki heavy enterprise sync me fail na ho
        self.timeout = httpx.Timeout(30.0)

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], List[Any]]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self._headers, params=params)
                
                # 1. ⚡ GRACEFUL RATE LIMIT HANDLING
                if response.status_code == 403 and "rate limit" in response.text.lower():
                    print(f"⚠️ [GitHub Client] Rate limit exceeded for {endpoint}! Bypassing to save pipeline.")
                    return [] 
                    
                # 2. ⚡ GRACEFUL EMPTY REPO / NOT FOUND HANDLING (Fixes the crash)
                if response.status_code in [404, 409]:
                    print(f"⚠️ [GitHub Client] Resource not found or empty (404/409): {endpoint}")
                    # Extractors loops (for x in data) expect lists, so returning [] prevents TypeError
                    return [] 

                # Standard error raiser for other 500s
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            print(f"🚨 [GitHub Client] HTTP Error {e.response.status_code} for {url}: {e.response.text}")
            return [] # Failsafe return
            
        except Exception as e:
            print(f"🚨 [GitHub Client] Network Error connecting to {url}: {str(e)}")
            return [] # Failsafe return
            
    async def post(self, endpoint: str, json_data: dict = None) -> dict:
        import httpx
        url = endpoint if endpoint.startswith("http") else f"{self.base_url}/{endpoint}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, json=json_data)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"🚨 [GitHub Client] POST Error: {e}")
            return {}        