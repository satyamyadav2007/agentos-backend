from typing import Dict, Any, List
from integrations.zendesk.extractors.tickets import ZendeskTicketExtractor
from integrations.zendesk.normalizer import ZendeskNormalizer

class ZendeskSyncService:
    """Orchestrates extraction and normalization for Zendesk."""
    
    def __init__(self, client):
        self.client = client
        self.ticket_extractor = ZendeskTicketExtractor(client)
        # self.org_extractor = ZendeskOrgExtractor(client) -> To be added
        
    async def run_full_sync(self) -> List[Dict[str, Any]]:
        print(f"\n🚀 [Zendesk Sync] Starting sync for subdomain: {self.client.subdomain}")
        
        all_universal_events = []
        
        # 1. Fetch Tickets
        tickets_models = await self.ticket_extractor.fetch_recent_tickets()
        
        # 2. Normalize to Universal Format
        for ticket in tickets_models:
            # TODO: Fetch real org name using organization_id in the future
            org_name = f"Org_{ticket.organization_id}" if ticket.organization_id else "Individual"
            
            normalized = ZendeskNormalizer.normalize_ticket(ticket, org_name)
            all_universal_events.append(normalized)
                
        print(f"🧠 [AgentOS Brain] Normalized {len(all_universal_events)} tickets from Zendesk!")
        return all_universal_events