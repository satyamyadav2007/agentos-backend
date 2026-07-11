from typing import Dict, Any, List
from integrations.base import BaseConnector
from .client import LinearClient
from .extractors.issues import LinearIssueExtractor
from .normalizer import LinearNormalizer

class LinearSyncService:
    def __init__(self, client):
        self.client = client
        self.issue_extractor = LinearIssueExtractor(client)
        
    async def run_full_sync(self) -> List[Dict[str, Any]]:
        print(f"\n🚀 [Linear Sync] Starting Modern Product Planning Sync...")
        
        issues = await self.issue_extractor.fetch_recent_issues(limit=30)
        all_universal_events = [LinearNormalizer.normalize_issue(issue) for issue in issues]
                
        print(f"🧠 [AgentOS Brain] Normalized {len(all_universal_events)} Linear tasks!")
        return all_universal_events


class LinearConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.linear_client = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        # Linear uses OAuth or simple API keys (Personal API keys are common for integrations)
        api_key = auth_payload.get("api_key") 
        
        if not api_key:
            return {"status": "error", "message": "Missing Linear API Key"}
            
        try:
            self.linear_client = LinearClient(api_key)
            sync_result = await self.sync()
            return {"status": "connected", "provider": "linear", "sync_info": sync_result}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def sync(self) -> Dict[str, Any]:
        if not self.linear_client:
            return {"status": "error", "message": "Not authenticated"}
            
        sync_service = LinearSyncService(self.linear_client)
        normalized_events = await sync_service.run_full_sync()
        
        if normalized_events:
            print("⚙️ [AgentOS] Routing Linear data to Universal Event Bus...")
            # Integrating with the exact structure from your screenshots!
            import sys
            import os
            # Ensuring it talks to your existing Event Bus logic smoothly
            from core.event_bus import event_bus
            from core.models.event import UniversalEvent
            
            events_objs = [UniversalEvent(**e) for e in normalized_events]
            await event_bus.publish(events_objs)
            print("✅ [AgentOS] Product Planning Intelligence Sync Complete!")
            
        return {"status": "synced", "events_processed": len(normalized_events)}

    async def webhook(self, payload: Dict[str, Any]) -> bool: pass
    async def disconnect(self) -> bool: pass