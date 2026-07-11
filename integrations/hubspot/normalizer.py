from typing import Dict, Any
from .models.deal import HubSpotDealModel

class HubSpotNormalizer:
    
    @staticmethod
    def normalize_deal(deal: HubSpotDealModel) -> Dict[str, Any]:
        """Converts HubSpot Deal into AgentOS UniversalEvent."""
        
        # High value deals get higher severity for immediate attention
        severity = "High" if deal.amount and deal.amount > 50000 else "Medium"

        return {
            "source": "hubspot",
            "entity_type": "deal",
            "repository": "Marketing_Sales_Pipeline", 
            "title": deal.dealname,
            "description": f"Stage: {deal.dealstage} | Pipeline: {deal.pipeline}",
            "author": deal.hubspot_owner_id or "Unassigned",
            "severity": severity,
            "timestamp": deal.createdate.isoformat(),
            "revenue_risk": deal.amount, # Feed this to Revenue Agent
            "metadata": {
                "hubspot_id": deal.id,
                "lifecycle_stage": deal.dealstage,
                "close_date": deal.closedate.isoformat() if deal.closedate else None
            },
            "linked_entities": [] # Ready to connect to Zendesk & GitHub in Neo4j
        }