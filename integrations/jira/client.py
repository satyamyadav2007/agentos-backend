import httpx
from typing import Dict, Any, Optional, Union


class JiraClient:
    """
    Enterprise HTTP Client for all Atlassian/Jira API calls.
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

    async def test_myself(self):
        """
        Debug endpoint.
        """
        return await self.get("rest/api/3/myself")

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], list]:

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        print("\n========================================")
        print("🚀 JIRA GET REQUEST")
        print("URL:", url)

        if params:
            print("PARAMS:", params)

        print("========================================")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    headers=self._headers,
                    params=params
                )

            print("\n============== RESPONSE ==============")
            print("STATUS:", response.status_code)
            print(response.text)
            print("======================================\n")

            if response.status_code == 429:
                print("⚠️ Rate Limit")
                return {}

            if response.status_code >= 400:
                return {}

            return response.json()

        except Exception as e:
            print("🚨 GET ERROR:", e)
            return {}

    async def post(
        self,
        endpoint: str,
        json_data: Dict[str, Any]
    ) -> Union[Dict[str, Any], list]:

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        print("\n========================================")
        print("🚀 JIRA POST REQUEST")
        print("URL:", url)
        print("BODY:", json_data)
        print("========================================")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    headers=self._headers,
                    json=json_data
                )

            print("\n============== RESPONSE ==============")
            print("STATUS:", response.status_code)
            print(response.text)
            print("======================================\n")

            if response.status_code == 429:
                print("⚠️ Rate Limit")
                return {}

            if response.status_code >= 400:
                return {}

            return response.json()

        except Exception as e:
            print("🚨 POST ERROR:", e)
            return {}