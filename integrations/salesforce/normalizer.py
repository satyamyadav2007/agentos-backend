from typing import Dict, Any
from .models.account import SalesforceAccountModel
from .models.opportunity import SalesforceOpportunityModel

class SalesforceNormalizer:
    
    @staticmethod
    def normalize_account(account: SalesforceAccountModel) -> Dict[str, Any]:
        """Converts Salesforce Account into AgentOS UniversalEvent."""
        
        # Base severity on tier/revenue (AgentOS specific logic)
        severity = "Critical" if account.is_enterprise else "Medium"

        return {
            "source": "salesforce",
            "entity_type": "account",
            "repository": "CRM_Revenue", # Conceptual grouping
            "title": f"Account: {account.name}",
            "description": f"Industry: {account.industry} | Tier: {account.customer_tier}",
            "author": "Salesforce_System",
            "severity": severity,
            "timestamp": account.last_modified_date.isoformat(),
            "revenue_risk": account.annual_revenue, # Crucial for Revenue Agent
            "metadata": {
                "salesforce_id": account.id,
                "type": account.type,
                "is_enterprise": account.is_enterprise,
                "health_score": account.health_score
            },
            "linked_entities": [] # Neo4j will connect this to Zendesk tickets & GitHub PRs
        }