from typing import List
from integrations.hubspot.models.deal import HubSpotDealModel

class HubSpotDealExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_open_deals(self) -> List[HubSpotDealModel]:
        print("🤝 [HubSpot Extractor] Fetching open deals from pipeline...")
        try:
            # We explicitly request the properties we need
            params = {
                "properties": "dealname,amount,dealstage,pipeline,closedate,createdate,hubspot_owner_id",
                "limit": 100
            }
            raw_data = await self.client.get("objects/deals", params=params)
            results = raw_data.get("results", [])
            
            deals = [HubSpotDealModel.from_hubspot_response(item) for item in results]
            print(f"   ✅ Extracted {len(deals)} Pipeline Deals.")
            return deals
        except Exception as e:
            print(f"🚨 [HubSpot Extractor] Failed to fetch deals: {e}")
            return []