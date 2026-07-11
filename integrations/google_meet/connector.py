from typing import Dict, Any, List
from integrations.base import BaseConnector
from .client import GoogleWorkspaceClient
from .extractors.meetings import GoogleMeetExtractor
from .normalizer import GoogleMeetNormalizer

class GoogleMeetSyncService:
    def __init__(self, client):
        self.client = client
        self.extractor = GoogleMeetExtractor(client)
        
    async def run_full_sync(self) -> List[Dict[str, Any]]:
        print(f"\n🚀 [Google Meet Sync] Starting Workspace Meeting Intelligence Sync...")
        
        meetings = await self.extractor.fetch_recent_meetings(limit=20)
        all_universal_events = [GoogleMeetNormalizer.normalize_meeting(m) for m in meetings]
                
        print(f"🧠 [AgentOS Brain] Normalized {len(all_universal_events)} Workspace meetings!")
        return all_universal_events


class GoogleMeetConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.google_client = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        access_token = auth_payload.get("access_token") # Provided by Google OAuth
        
        if not access_token:
            return {"status": "error", "message": "Missing Google OAuth Token"}
            
        try:
            self.google_client = GoogleWorkspaceClient(access_token)
            sync_result = await self.sync()
            return {"status": "connected", "provider": "google_meet", "sync_info": sync_result}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def sync(self) -> Dict[str, Any]:
        if not self.google_client:
            return {"status": "error", "message": "Not authenticated"}
            
        sync_service = GoogleMeetSyncService(self.google_client)
        normalized_events = await sync_service.run_full_sync()
        
        if normalized_events:
            print("⚙️ [AgentOS] Routing Google Meet transcripts to Universal Event Bus...")
            
            # Leveraging your solid architecture!
            from core.event_bus import event_bus
            from core.models.event import UniversalEvent
            
            events_objs = [UniversalEvent(**e) for e in normalized_events]
            await event_bus.publish(events_objs)
            print("✅ [AgentOS] Google Workspace Intelligence Sync Complete!")
            
        return {"status": "synced", "events_processed": len(normalized_events)}

    async def webhook(self, payload: Dict[str, Any]) -> bool: pass
    async def disconnect(self) -> bool: pass