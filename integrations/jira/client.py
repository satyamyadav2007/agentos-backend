import httpx
import json
from typing import Dict, Any, Optional, Union

class JiraClient:
    """
    Enterprise HTTP Client for Jira REST + Agile APIs.
    Prints every request & response for debugging.
    """

    def __init__(self, access_token: str, cloud_id: str):
        self.access_token = access_token
        self.cloud_id = cloud_id
        self.base_url = f"https://api.atlassian.com/ex/jira/{cloud_id}"
        self.timeout = httpx.Timeout(60.0)

    @property
    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], list]:

        endpoint = endpoint.lstrip("/")
        url = f"{self.base_url}/{endpoint}"

        print("\n===================================================")
        print("🚀 JIRA GET REQUEST")
        print("URL:", url)

        if params:
            print("PARAMS:")
            print(json.dumps(params, indent=2))

        print("TOKEN:", self.access_token[:40] + "...")
        print("===================================================")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    headers=self._headers,
                    params=params
                )

            print("\n================ RESPONSE =================")
            print("STATUS:", response.status_code)
            print(response.text[:4000])
            print("===========================================\n")

            if response.status_code == 429:
                print("⚠️ Jira Rate Limited")
                return {}

            if response.status_code >= 400:
                return {}

            return response.json()

        except Exception as e:
            print("🚨 CLIENT ERROR:", e)
            return {}

    async def post(
        self,
        endpoint: str,
        json_data: Dict[str, Any]
    ) -> Union[Dict[str, Any], list]:

        endpoint = endpoint.lstrip("/")
        url = f"{self.base_url}/{endpoint}"

        print("\n===================================================")
        print("🚀 JIRA POST REQUEST")
        print("URL:", url)
        print("BODY:")
        print(json.dumps(json_data, indent=2))
        print("===================================================")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    headers=self._headers,
                    json=json_data
                )

            print("\n================ RESPONSE =================")
            print("STATUS:", response.status_code)
            print(response.text[:4000])
            print("===========================================\n")

            if response.status_code == 429:
                print("⚠️ Jira Rate Limited")
                return {}

            if response.status_code >= 400:
                return {}

            return response.json()

        except Exception as e:
            print("🚨 CLIENT ERROR:", e)
            return {}