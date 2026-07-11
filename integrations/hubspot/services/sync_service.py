from typing import Dict, Any, List
from integrations.hubspot.extractors.deals import HubSpotDealExtractor
from integrations.hubspot.normalizer import HubSpotNormalizer

class HubSpotSyncService:
    """Orchestrates extraction and normalization for HubSpot Growth Data."""
    
    def __init__(self, client):
        self.client = client
        self.deal_extractor = HubSpotDealExtractor(client)
        # self.contact_extractor = HubSpotContactExtractor(client) -> To be added
        
    async def run_full_sync(self) -> List[Dict[str, Any]]:
        print("\n🚀 [HubSpot Sync] Starting Growth & Pipeline Sync...")
        
        all_universal_events = []
        
        # 1. Fetch Deals
        deals_models = await self.deal_extractor.fetch_open_deals()
        
        # 2. Normalize to Universal Format
        for deal in deals_models:
            normalized = HubSpotNormalizer.normalize_deal(deal)
            all_universal_events.append(normalized)
            
        print(f"🧠 [AgentOS Brain] Normalized {len(all_universal_events)} growth entities from HubSpot!")
        return all_universal_events