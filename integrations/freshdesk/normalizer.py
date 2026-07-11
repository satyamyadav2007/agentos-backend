from typing import Dict, Any
from .models.ticket import FreshdeskTicketModel

class FreshdeskNormalizer:
    
    @staticmethod
    def normalize_ticket(ticket: FreshdeskTicketModel) -> Dict[str, Any]:
        """Converts a Freshdesk Ticket into an AgentOS UniversalEvent."""
        
        return {
            "source": "freshdesk",
            "entity_type": "ticket",
            "repository": "Customer_Support", 
            "title": f"Ticket #{ticket.id}: {ticket.subject}",
            "description": ticket.description_text[:1500], # Keep within AI context limits
            "author": f"Requester_{ticket.requester_id}",
            "severity": ticket.severity_label,
            "timestamp": ticket.updated_at.isoformat(),
            "metadata": {
                "ticket_id": ticket.id,
                "status_code": ticket.status,
                "tags": ticket.tags
            },
            # Graph Connections (e.g., to GitHub issues or Jira epics)
            "linked_entities": [] 
        }