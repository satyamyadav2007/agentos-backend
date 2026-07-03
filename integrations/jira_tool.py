import requests
from requests.auth import HTTPBasicAuth
from .base import BaseIntegration

class JiraIntegration(BaseIntegration):
    def __init__(self, domain: str = "mock_domain", email: str = "mock_email", api_token: str = "mock_token"):
        self.domain = domain
        self.email = email
        self.api_token = api_token
        # Jira REST API URL for creating issues
        self.api_url = f"https://{self.domain}.atlassian.net/rest/api/2/issue"

    def fetch_data(self, **kwargs):
        pass

    def send_action(self, prd_content: str, project_key: str = "KAN", issue_summary: str = "Auto-PRD: Fix Required"):
        print(f"[Jira] Exporting AI PRD to Jira Project: {project_key}...")
        
        # 🚨 MOCK MODE: Agar API token nahi hai, toh terminal me print karke success return karo
        if not self.api_token or self.api_token == "mock_token":
            print(f"🤖 [Jira Mock Success]: \nTitle: {issue_summary}\nDescription: {prd_content[:50]}...\n-------------------------")
            return {"status": "success", "ticket": "MOCK-123"}
            
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": issue_summary,
                "description": prd_content,
                "issuetype": {"name": "Task"} # Enterprise level par usually 'Task' ya 'Bug' use hota hai
            }
        }
        
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        auth = HTTPBasicAuth(self.email, self.api_token)
        
        try:
            response = requests.post(self.api_url, json=payload, headers=headers, auth=auth)
            if response.status_code == 201:
                ticket_key = response.json().get('key')
                print(f"[Jira] Success! Ticket created: {ticket_key}")
                return {"status": "success", "ticket": ticket_key}
            else:
                print(f"[Jira Error] Failed: {response.text}")
                return {"status": "error", "message": response.text}
        except Exception as e:
            print(f"[Jira Exception] {e}")
            return {"status": "error", "message": str(e)}