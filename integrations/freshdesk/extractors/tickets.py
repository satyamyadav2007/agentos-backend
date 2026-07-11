from typing import List
from datetime import datetime
from integrations.freshdesk.models.ticket import FreshdeskTicketModel

class FreshdeskTicketExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_recent_tickets(self, limit: int = 30) -> List[FreshdeskTicketModel]:
        print(f"🎫 [Freshdesk Extractor] Fetching recent customer support tickets...")
        
        # Fetch unresolved tickets to prioritize current customer pains
        params = {"updated_since": "2023-01-01T00:00:00Z", "per_page": limit, "order_by": "updated_at", "order_type": "desc"}
        
        try:
            raw_data = await self.client.get("tickets", params=params)
            ticket_data = raw_data.get("data", [])
            
            tickets = []
            for t in ticket_data:
                tickets.append(FreshdeskTicketModel(
                    id=t.get("id"),
                    subject=t.get("subject", "No Subject"),
                    description_text=t.get("description_text", ""),
                    status=t.get("status", 2),
                    priority=t.get("priority", 1),
                    requester_id=t.get("requester_id"),
                    created_at=datetime.fromisoformat(t.get("created_at", "").replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(t.get("updated_at", "").replace('Z', '+00:00')),
                    tags=t.get("tags", [])
                ))
            
            print(f"   ✅ Extracted {len(tickets)} Freshdesk tickets.")
            return tickets
            
        except Exception as e:
            print(f"🚨 [Freshdesk Extractor] Failed to fetch tickets: {e}")
            return []