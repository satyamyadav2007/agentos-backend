import httpx
from typing import Dict, Any, Optional, Union

class JiraClient:
    """
    Enterprise HTTP Client for all Atlassian/Jira API calls.
    Gracefully handles REST (v3) and Agile (v1.0) APIs without crashing.
    """
    def __init__(self, access_token: str, cloud_id: str):
        self.access_token = access_token
        self.cloud_id = cloud_id
        self.base_url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}"
        self.timeout = httpx.Timeout(30.0) 

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], list]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        print(f"🔗 [Client Debug] Exact URL Executed: {url}")
        
        # ⚡ OPTIONAL BUT HELPFUL: Print params so you know exactly what JQL is sent
        if params:
            print(f"🔍 [Client Debug] Query Params: {params}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self._headers, params=params)
                
                if response.status_code == 429:
                    print(f"⚠️ [Jira Client] Rate limit exceeded for {endpoint}! Bypassing...")
                    return {} 
                
                # ⚡ FIX: Catch ALL 400+ errors and print EXACTLY what Atlassian is complaining about
                if response.status_code >= 400:
                    print(f"⚠️ [Jira Client] Resource unavailable ({response.status_code}) for {endpoint}")
                    print(f"🚨 [Jira Response Body]: {response.text}")
                    return {} 

                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            print(f"🚨 [Jira Client] Network Error on GET {url}: {str(e)}")
            return {}

    async def post(self, endpoint: str, json_data: Dict[str, Any]) -> Union[Dict[str, Any], list]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        print(f"🔗 [Client Debug] Exact URL Executed: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=self._headers, json=json_data)
                
                if response.status_code == 429:
                    print(f"⚠️ [Jira Client] Rate limit exceeded for {endpoint}! Bypassing...")
                    return {}

                # ⚡ FIX: Catch ALL 400+ errors and print EXACTLY what Atlassian is complaining about
                if response.status_code >= 400:
                    print(f"⚠️ [Jira Client] POST Failed ({response.status_code}): {endpoint}")
                    print(f"🚨 [Jira Response Body]: {response.text}")
                    return {}

                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            print(f"🚨 [Jira Client] Network Error on POST {url}: {str(e)}")
            return {}