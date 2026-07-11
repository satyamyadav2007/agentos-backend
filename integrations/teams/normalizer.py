from typing import Dict, Any
from .models.message import TeamsMessageModel

class TeamsNormalizer:
    
    @staticmethod
    def normalize_message(message: TeamsMessageModel) -> Dict[str, Any]:
        """Converts a Microsoft Teams message into an AgentOS UniversalEvent."""
        
        # Escalate priority if it looks like an incident or blocker
        severity = "Critical" if message.is_escalation else "Medium"

        return {
            "source": "teams",
            "entity_type": "channel_message",
            "repository": f"Team_{message.team_id}", # Maps to the workspace/team context
            "title": f"Teams Discussion by {message.author.display_name}",
            "description": message.content[:1500], # Keep within AI context limits
            "author": message.author.email or message.author.display_name,
            "severity": severity,
            "timestamp": message.created_datetime.isoformat(),
            "metadata": {
                "message_id": message.id,
                "channel_id": message.channel_id,
                "has_attachments": message.has_attachments
            },
            # Graph connections for Neo4j (Module 20)
            "linked_entities": [] 
        }