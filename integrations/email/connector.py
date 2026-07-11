from typing import Dict, Any
from integrations.base import BaseConnector
from .providers.gmail import GmailProvider
from .providers.outlook import OutlookProvider
from .normalizer import EmailNormalizer

class EmailConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.active_provider = None
        self.provider_name = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        self.provider_name = auth_payload.get("provider", "").lower()
        access_token = auth_payload.get("access_token") # Fetched via frontend OAuth
        
        if not all([self.provider_name, access_token]):
            return {"status": "error", "message": "Missing provider or access_token"}
            
        try:
            if self.provider_name == "gmail":
                self.active_provider = GmailProvider(access_token)
            elif self.provider_name == "outlook":
                self.active_provider = OutlookProvider(access_token)
                pass
            
            sync_result = await self.sync()
            return {"status": "connected", "provider": self.provider_name, "sync_info": sync_result}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def sync(self) -> Dict[str, Any]:
        if not self.active_provider:
            return {"status": "error", "message": "No active email provider"}
            
        threads = await self.active_provider.fetch_recent_threads()
        
        normalized_events = []
        for t in threads:
            if t.messages:
                normalized_events.append(EmailNormalizer.normalize_thread(t))
        
        if normalized_events:
            print(f"⚙️ [AgentOS] Routing {self.provider_name} Emails to Event Bus...")
            from core.event_bus import event_bus
            from core.models.event import UniversalEvent
            
            events_objs = [UniversalEvent(**e) for e in normalized_events]
            await event_bus.publish(events_objs)
            print(f"✅ [AgentOS] Email Intelligence Sync Complete!")
        
        return {"status": "synced", "threads_processed": len(normalized_events)}

    async def webhook(self, payload: Dict[str, Any]) -> bool: pass
    async def disconnect(self) -> bool: pass