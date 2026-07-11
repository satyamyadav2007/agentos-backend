from typing import Dict, Any, List
from integrations.salesforce.extractors.accounts import SalesforceAccountExtractor
from integrations.salesforce.normalizer import SalesforceNormalizer

class SalesforceSyncService:
    """Orchestrates extraction and normalization for Salesforce Revenue Data."""
    
    def __init__(self, client):
        self.client = client
        self.account_extractor = SalesforceAccountExtractor(client)
        # self.opp_extractor = SalesforceOpportunityExtractor(client) -> Coming soon
        
    async def run_full_sync(self) -> List[Dict[str, Any]]:
        print(f"\n🚀 [Salesforce Sync] Starting Revenue Data Sync for instance: {self.client.instance_url}")
        
        all_universal_events = []
        
        # 1. Fetch High-Value Accounts
        accounts_models = await self.account_extractor.fetch_key_accounts()
        
        # 2. Normalize to Universal Format
        for account in accounts_models:
            normalized = SalesforceNormalizer.normalize_account(account)
            all_universal_events.append(normalized)
            
        print(f"🧠 [AgentOS Brain] Normalized {len(all_universal_events)} revenue entities from Salesforce!")
        return all_universal_events