from typing import Dict, Any
from .models.conversation import IntercomConversationModel

class IntercomNormalizer:
    
    @staticmethod
    def normalize_conversation(conversation: IntercomConversationModel) -> Dict[str, Any]:
        """Converts Intercom Conversation into AgentOS UniversalEvent."""
        
        import re
        # Clean HTML tags from the snippet for the AI
        clean_text = re.sub('<[^<]+?>', '', conversation.snippet)

        return {
            "source": "intercom",
            "entity_type": "conversation",
            "repository": "Proactive_Customer_Chat", 
            "title": f"Chat from Contact {conversation.primary_contact_id}",
            "description": clean_text,
            "author": conversation.primary_contact_id,
            "severity": "Medium", # Will be updated by Theme Agent based on intent (Bug vs Feature)
            "timestamp": conversation.created_at.isoformat(),
            "metadata": {
                "intercom_id": conversation.id,
                "state": conversation.state,
                "read": conversation.read
            },
            "linked_entities": [] # Ready to connect to Zendesk & GitHub in Neo4j
        }