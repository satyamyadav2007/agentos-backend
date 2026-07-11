from typing import Dict, Any
import requests
from requests.auth import HTTPBasicAuth
from .base import BaseConnector


class JiraIntegration(BaseConnector):

    def __init__(
        self,
        domain: str = "mock_domain",
        email: str = "mock_email",
        api_token: str = "mock_token",
        workspace_id: str = "default_workspace",
        org_id: str = "default_org",
    ):
        super().__init__(workspace_id, org_id)

        self.domain = domain
        self.email = email
        self.api_token = api_token

        self.api_url = (
            f"https://{self.domain}.atlassian.net/rest/api/2/issue"
        )

    # ===================================================
    # BaseConnector Required Methods
    # ===================================================

    async def connect(
        self,
        auth_payload: Dict[str, Any],
    ) -> Dict[str, Any]:

        print("[Jira] Connected")

        return {
            "status": "connected"
        }

    async def sync(self) -> Dict[str, Any]:

        print("[Jira] Sync started")

        return {
            "status": "success",
            "items": []
        }

    async def webhook(
        self,
        payload: Dict[str, Any],
    ) -> bool:

        print("[Jira] Webhook received")

        return True

    async def disconnect(self) -> bool:

        print("[Jira] Disconnected")

        return True

    async def normalize(
        self,
        raw_data: Any,
    ) -> Any:

        return raw_data

    # ===================================================
    # Existing Methods
    # ===================================================

    def fetch_data(self, **kwargs):
        return []

    def send_action(
        self,
        prd_content: str,
        project_key: str = "KAN",
        issue_summary: str = "Auto-PRD: Fix Required",
    ):

        print(f"[Jira] Exporting AI PRD...")

        if self.api_token == "mock_token":

            print(f"[MOCK]\n{issue_summary}")

            return {
                "status": "success",
                "ticket": "MOCK-123",
            }

        payload = {
            "fields": {
                "project": {
                    "key": project_key
                },
                "summary": issue_summary,
                "description": prd_content,
                "issuetype": {
                    "name": "Task"
                }
            }
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        auth = HTTPBasicAuth(
            self.email,
            self.api_token,
        )

        response = requests.post(
            self.api_url,
            json=payload,
            headers=headers,
            auth=auth,
        )

        if response.status_code == 201:

            return {
                "status": "success",
                "ticket": response.json()["key"],
            }

        return {
            "status": "error",
            "message": response.text,
        }