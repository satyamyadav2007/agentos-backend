from typing import Dict, Any
from .models.event import AnalyticsEventModel

class AnalyticsNormalizer:
    
    @staticmethod
    def normalize_event(event: AnalyticsEventModel) -> Dict[str, Any]:
        """Converts ANY analytics event (Mixpanel/Amplitude/PostHog) into an AgentOS UniversalEvent."""
        
        # Flag critical behaviors for the Theme/Action Agents
        severity = "High" if event.is_dropoff_signal else "Low"

        return {
            "source": "analytics",
            "provider": event.provider, # Tagging where it came from
            "entity_type": "user_behavior",
            "repository": "Product_Analytics", 
            "title": f"User Action: {event.event_name}",
            "description": f"User {event.user_id} triggered {event.event_name} on {event.current_url or 'App'}",
            "author": event.user_id,
            "severity": severity,
            "timestamp": event.timestamp.isoformat(),
            "metadata": {
                "event_id": event.id,
                "session_id": event.session_id,
                "properties": event.properties
            },
            "linked_entities": [] # Neo4j will connect this user_id to Zendesk and GitHub!
        }