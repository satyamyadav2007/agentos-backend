from typing import List
from integrations.zendesk.models.ticket import ZendeskTicketModel

class ZendeskTicketExtractor:
    """Handles Module 3: Ticket Intelligence extraction."""
    
    def __init__(self, client):
        self.client = client

    async def fetch_recent_tickets(self, status: str = "open,new,pending") -> List[ZendeskTicketModel]:
        print(f"🎫 [Zendesk Extractor] Fetching '{status}' tickets from {self.client.subdomain}...")
        try:
            raw_data = await self.client.get(
                "tickets", 
                params={"status": status, "sort_by": "updated_at", "sort_order": "desc"}
            )
            
            tickets_data = raw_data.get("tickets", [])
            tickets = [ZendeskTicketModel(**item) for item in tickets_data]
                    
            print(f"   ✅ Extracted {len(tickets)} tickets.")
            return tickets
            
        except Exception as e:
            print(f"🚨 [Zendesk Extractor] Failed to fetch tickets: {e}")
            return []