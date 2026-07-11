from typing import Dict, Any, List
from integrations.base import BaseConnector
from .client import FreshdeskClient
from .extractors.tickets import FreshdeskTicketExtractor
from .normalizer import FreshdeskNormalizer

class FreshdeskSyncService:
    def __init__(self, client):
        self.client = client
        self.ticket_extractor = FreshdeskTicketExtractor(client)
        
    async def run_full_sync(self) -> List[Dict[str, Any]]:
        print(f"\n🚀 [Freshdesk Sync] Starting Customer Intelligence Sync...")
        
        tickets = await self.ticket_extractor.fetch_recent_tickets(limit=30)
        all_universal_events = [FreshdeskNormalizer.normalize_ticket(t) for t in tickets]
                
        print(f"🧠 [AgentOS Brain] Normalized {len(all_universal_events)} Freshdesk support events!")
        return all_universal_events


class FreshdeskConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.freshdesk_client = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        api_key = auth_payload.get("api_key")
        domain = auth_payload.get("domain")
        
        if not api_key or not domain:
            return {"status": "error", "message": "Missing API Key or Domain"}
            
        try:
            self.freshdesk_client = FreshdeskClient(api_key, domain)
            sync_result = await self.sync()
            return {"status": "connected", "provider": "freshdesk", "sync_info": sync_result}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def sync(self) -> Dict[str, Any]:
        if not self.freshdesk_client:
            return {"status": "error", "message": "Not authenticated"}
            
        sync_service = FreshdeskSyncService(self.freshdesk_client)
        normalized_events = await sync_service.run_full_sync()
        
        if normalized_events:
            print("⚙️ [AgentOS] Routing Freshdesk data to Universal Event Bus...")
            
            # Using your existing Event Bus!
            from core.event_bus import event_bus
            from core.models.event import UniversalEvent
            
            events_objs = [UniversalEvent(**e) for e in normalized_events]
            await event_bus.publish(events_objs)
            print("✅ [AgentOS] Freshdesk Intelligence Sync Complete!")
            
        return {"status": "synced", "events_processed": len(normalized_events)}

    async def webhook(self, payload: Dict[str, Any]) -> bool: pass
    async def disconnect(self) -> bool: pass
