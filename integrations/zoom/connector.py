from typing import Dict, Any
from integrations.base import BaseConnector
from .oauth import ZoomOAuthManager
from .client import ZoomClient
from .services.sync_service import ZoomSyncService

class ZoomConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.oauth_manager = ZoomOAuthManager()
        self.zoom_client = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        print("🔗 [Zoom Connector] Connecting Zoom Intelligence Engine...")
        try:
            # 1. Fetch S2S Token
            token = await self.oauth_manager.get_access_token()
            self.zoom_client = ZoomClient(access_token=token)
            
            # 2. Trigger Initial Data Sync
            sync_result = await self.sync()
            
            return {
                "status": "connected",
                "provider": "zoom",
                "sync_info": sync_result
            }
        except Exception as e:
            print(f"🚨 [Zoom Connector Error]: {e}")
            return {"status": "error", "message": str(e)}

    async def sync(self) -> Dict[str, Any]:
        if not self.zoom_client:
            return {"status": "error", "message": "Not authenticated"}
            
        sync_service = ZoomSyncService(self.zoom_client)
        normalized_events = await sync_service.run_full_sync()
        
        if normalized_events:
            print("⚙️ [AgentOS] Handoff to Universal Event Bus started for Zoom transcripts...")
            from core.event_bus import event_bus
            from core.models.event import UniversalEvent
            
            events_objs = [UniversalEvent(**e) for e in normalized_events]
            await event_bus.publish(events_objs)
            print("✅ [AgentOS] AI Processing Complete for Zoom Meeting Sync!")
            
        return {"status": "synced", "meetings_processed": len(normalized_events)}

    async def webhook(self, payload: Dict[str, Any]) -> bool:
        pass
    async def disconnect(self) -> bool:
        pass