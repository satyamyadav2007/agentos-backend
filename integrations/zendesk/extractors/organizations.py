from typing import List
from integrations.zendesk.models.organization import ZendeskOrganizationModel

class ZendeskOrgExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_organizations(self) -> List[ZendeskOrganizationModel]:
        print(f"🏢 [Zendesk Extractor] Scanning organizations...")
        try:
            raw_data = await self.client.get("organizations")
            orgs = [ZendeskOrganizationModel(**item) for item in raw_data.get("organizations", [])]
            print(f"   ✅ Extracted {len(orgs)} organizations.")
            return orgs
        except Exception as e:
            print(f"🚨 [Zendesk Extractor] Failed to fetch organizations: {e}")
            return []