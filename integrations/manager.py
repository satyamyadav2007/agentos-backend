import os
from dotenv import load_dotenv
from .slack import SlackIntegration
from .crm import CRMIntegration
from .jira_tool import JiraIntegration

# Load variables from .env file securely
load_dotenv()

class IntegrationManager:
    def __init__(self):
        self.slack = SlackIntegration(webhook_url=os.getenv("SLACK_WEBHOOK_URL"))
        self.crm = CRMIntegration()
        self.jira = JiraIntegration(
            domain=os.getenv("JIRA_DOMAIN"),
            email=os.getenv("JIRA_EMAIL"),
            api_token=os.getenv("JIRA_API_TOKEN")
        )

    
    def get_integration(self, name: str):
        name = name.lower()
        if name == "slack":
            return self.slack
        elif name == "crm":          
            return self.crm
        elif name == "jira":         # <-- YEH 2 NAYI LINES ADD KARO
            return self.jira
        else:
            raise ValueError(f"Enterprise Integration '{name}' is not supported yet.")

integration_manager = IntegrationManager()