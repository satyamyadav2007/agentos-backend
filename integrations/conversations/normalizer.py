from typing import Dict, Any
from .models.call import ConversationCallModel

class ConversationNormalizer:
    
    @staticmethod
    def normalize_call(call: ConversationCallModel) -> Dict[str, Any]:
        """Converts ANY conversation (Gong/Fireflies/Otter) into an AgentOS UniversalEvent."""
        
        # High severity if it's a critical deal or churn risk
        severity = "Critical" if call.is_revenue_critical else "Medium"

        return {
            "source": "conversations",
            "provider": call.provider,
            "entity_type": "sales_call",
            "repository": "Revenue_Intelligence", 
            "title": call.title,
            "description": f"Transcript Snippet: {call.transcript_text[:1000]}",
            "author": call.provider,
            "severity": severity,
            "timestamp": call.start_time.isoformat(),
            "metadata": {
                "call_id": call.id,
                "deal_id": call.deal_id,
                "duration": call.duration_minutes,
                "participants": [s.name for s in call.speakers]
            },
            # Linked to Salesforce Opportunity and Jira Epics by Neo4j
            "linked_entities": [call.deal_id] if call.deal_id else []
        }