from typing import Dict, Any, List
from integrations.base import BaseConnector
from .client import TeamsGraphClient
from .extractors.messages import TeamsMessageExtractor
from .normalizer import TeamsNormalizer

class TeamsSyncService:
    def __init__(self, client):
        self.client = client
        self.message_extractor = TeamsMessageExtractor(client)
        
    async def run_full_sync(self, target_channels: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        print(f"\n🚀 [Teams Sync] Starting Enterprise Collaboration Sync...")
        all_universal_events = []
        
        for channel in target_channels:
            team_id = channel.get("team_id")
            channel_id = channel.get("channel_id")
            
            messages = await self.message_extractor.fetch_channel_messages(team_id, channel_id)
            
            for msg in messages:
                # Filter out extremely short messages to keep signal-to-noise ratio high
                if len(msg.content) > 10:
                    all_universal_events.append(TeamsNormalizer.normalize_message(msg))
                    
        print(f"🧠 [AgentOS Brain] Normalized {len(all_universal_events)} Microsoft Teams messages!")
        return all_universal_events

class TeamsConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.teams_client = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        access_token = auth_payload.get("access_token") # Fetched via frontend MSAL
        
        if not access_token:
            return {"status": "error", "message": "Missing Microsoft Graph access token"}
            
        try:
            self.teams_client = TeamsGraphClient(access_token)
            sync_result = await self.sync()
            
            return {"status": "connected", "provider": "teams", "sync_info": sync_result}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def sync(self) -> Dict[str, Any]:
        if not self.teams_client:
            return {"status": "error", "message": "Not authenticated"}
            
        sync_service = TeamsSyncService(self.teams_client)
        
        # Hardcoded for MVP: In production, these come from Discovery Engine
        target_channels = [
            {"team_id": "YOUR_TEAM_ID", "channel_id": "YOUR_CHANNEL_ID"}
        ]
        
        normalized_events = await sync_service.run_full_sync(target_channels)
        
        if normalized_events:
            print("⚙️ [AgentOS] Routing Teams messages to Universal Event Bus...")
            from core.event_bus import event_bus
            from core.models.event import UniversalEvent
            
            events_objs = [UniversalEvent(**e) for e in normalized_events]
            await event_bus.publish(events_objs)
            print("✅ [AgentOS] Enterprise Collaboration Sync Complete!")
            
        return {"status": "synced", "messages_processed": len(normalized_events)}

    async def webhook(self, payload: Dict[str, Any]) -> bool: pass
    async def disconnect(self) -> bool: pass