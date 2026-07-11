from typing import Dict, Any
from .models.ticket import ZendeskTicketModel

class ZendeskNormalizer:
    
    @staticmethod
    def normalize_ticket(ticket: ZendeskTicketModel, org_name: str = "Unknown Org") -> Dict[str, Any]:
        """Converts a Zendesk Ticket into the AgentOS UniversalEvent format."""
        
        # Map Zendesk priority to AgentOS severity
        severity_map = {"urgent": "Critical", "high": "High", "normal": "Medium", "low": "Low"}
        severity = severity_map.get(ticket.priority, "Medium")

        return {
            "source": "zendesk",
            "entity_type": "ticket",
            "repository": "Customer_Support", # Conceptual bucket
            "title": ticket.subject,
            "description": ticket.description,
            "author": f"User_{ticket.requester_id}", # Can be enriched with users.py later
            "severity": severity,
            "timestamp": ticket.created_at.isoformat(),
            "customer": org_name,
            "revenue_risk": f"${ticket.calculated_arr_risk}", # Will be updated by Revenue Agent
            "metadata": {
                "ticket_id": ticket.id,
                "status": ticket.status,
                "tags": ticket.tags,
                "type": ticket.type
            },
            "linked_entities": []
        }