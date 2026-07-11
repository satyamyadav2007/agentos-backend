from typing import Dict, Any, Type
from .base import BaseConnector

# 🚀 All 23 Enterprise Connectors Imported
from .github.connector import GitHubConnector
from .jira.connector import JiraConnector
from .slack.connector import SlackConnector 
from .zendesk.connector import ZendeskConnector
from .salesforce.connector import SalesforceConnector
from .hubspot.connector import HubSpotConnector
from .intercom.connector import IntercomConnector
from .discord.connector import DiscordConnector
from .reddit.connector import RedditConnector
from .analytics.connector import AnalyticsConnector
from .crashes.connector import CrashesConnector
from .email.connector import EmailConnector
from .zoom.connector import ZoomConnector
from .bitbucket.connector import BitbucketConnector
from .linear.connector import LinearConnector
from .freshdesk.connector import FreshdeskConnector
from .twitter.connector import TwitterConnector
from .community.connector import CommunityConnector
from .ga4.connector import GA4Connector
from .datadog.connector import DatadogConnector
from .google_meet.connector import GoogleMeetConnector
from .reviews.connector import ReviewsConnector
from .knowledge.connector import KnowledgeConnector

class IntegrationManager:
    def __init__(self):
        # ⚡ Complete AgentOS Central Registry
        self._registry: Dict[str, Type[BaseConnector]] = {
            "github": GitHubConnector,
            "jira": JiraConnector,
            "slack": SlackConnector,
            "zendesk": ZendeskConnector,
            "salesforce": SalesforceConnector,
            "hubspot": HubSpotConnector,
            "intercom": IntercomConnector,
            "discord": DiscordConnector,
            "reddit": RedditConnector,
            "analytics": AnalyticsConnector,
            "crashes": CrashesConnector,
            "email": EmailConnector,
            "zoom": ZoomConnector,
            "bitbucket": BitbucketConnector,
            "linear": LinearConnector,
            "freshdesk": FreshdeskConnector,  
            "twitter": TwitterConnector,
            "community": CommunityConnector,
            "ga4": GA4Connector,
            "datadog": DatadogConnector,
            "google_meet": GoogleMeetConnector,
            "reviews": ReviewsConnector,
            "knowledge": KnowledgeConnector  
        }
        
    async def connect_integration(self, integration_name: str, workspace_id: str, org_id: str, auth_payload: Dict[str, Any]):
        if integration_name not in self._registry:
            raise ValueError(f"Integration '{integration_name}' is not supported yet.")
        
        connector_class = self._registry[integration_name]
        connector_instance = connector_class(workspace_id=workspace_id, org_id=org_id)
        
        connection_status = await connector_instance.connect(auth_payload)
        return connection_status

integration_manager = IntegrationManager()