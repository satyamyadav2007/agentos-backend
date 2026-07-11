from typing import Dict, Any, List
from integrations.base import BaseConnector
from .providers.gong import GongProvider
# from .providers.fireflies import FirefliesProvider
from .normalizer import ConversationNormalizer

class ConversationSyncService:
    def __init__(self, provider):
        self.provider = provider
        
    async def run_full_sync(self) -> List[Dict[str, Any]]:
        print(f"\n🚀 [Conversation Sync] Starting Revenue Intelligence Sync...")
        calls = await self.provider.fetch_recent_calls()
        
        events = [ConversationNormalizer.normalize_call(c) for c in calls]
        print(f"🧠 [AgentOS Brain] Normalized {len(events)} sales conversations for AI Processing!")
        return events

class ConversationConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.active_provider = None
        self.provider_name = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        self.provider_name = auth_payload.get("provider", "").lower()
        api_key = auth_payload.get("api_key")
        api_secret = auth_payload.get("api_secret") # Required for Gong
        
        if not self.provider_name or not api_key:
            return {"status": "error", "message": "Missing credentials"}
            
        try:
            if self.provider_name == "gong":
                self.active_provider = GongProvider(api_key, api_secret)
            elif self.provider_name == "fireflies":
                # self.active_provider = FirefliesProvider(api_key)
                pass
            
            sync_result = await self.sync()
            return {"status": "connected", "provider": self.provider_name, "sync_info": sync_result}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def sync(self) -> Dict[str, Any]:
        if not self.active_provider:
            return {"status": "error", "message": "No active provider"}
            
        sync_service = ConversationSyncService(self.active_provider)
        normalized_events = await sync_service.run_full_sync()
        
        if normalized_events:
            print(f"⚙️ [AgentOS] Routing {self.provider_name} transcripts to Event Bus...")
            from core.event_bus import event_bus
            from core.models.event import UniversalEvent
            
            events_objs = [UniversalEvent(**e) for e in normalized_events]
            await event_bus.publish(events_objs)
            print(f"✅ [AgentOS] Revenue Intelligence Sync Complete!")
            
        return {"status": "synced", "calls_processed": len(normalized_events)}

    async def webhook(self, payload: Dict[str, Any]) -> bool: pass
    async def disconnect(self) -> bool: pass