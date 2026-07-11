from typing import Dict, Any, List
from integrations.base import BaseConnector
from .client import DatadogClient
from .extractors.monitors import DatadogMonitorExtractor
from .normalizer import DatadogNormalizer

class DatadogSyncService:
    def __init__(self, client):
        self.client = client
        self.extractor = DatadogMonitorExtractor(client)
        
    async def run_full_sync(self) -> List[Dict[str, Any]]:
        print(f"\n🚀 [Datadog Sync] Starting Infrastructure Intelligence Sync...")
        
        alerts = await self.extractor.fetch_recent_alerts(limit=30)
        all_universal_events = [DatadogNormalizer.normalize_alert(a) for a in alerts]
                
        print(f"🧠 [AgentOS Brain] Normalized {len(all_universal_events)} Datadog observability events!")
        return all_universal_events


class DatadogConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.dd_client = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        api_key = auth_payload.get("api_key")
        app_key = auth_payload.get("app_key")
        site = auth_payload.get("site", "datadoghq.com")
        
        if not api_key or not app_key:
            return {"status": "error", "message": "Missing API Key or App Key"}
            
        try:
            self.dd_client = DatadogClient(api_key, app_key, site)
            sync_result = await self.sync()
            return {"status": "connected", "provider": "datadog", "sync_info": sync_result}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def sync(self) -> Dict[str, Any]:
        if not self.dd_client:
            return {"status": "error", "message": "Not authenticated"}
            
        sync_service = DatadogSyncService(self.dd_client)
        normalized_events = await sync_service.run_full_sync()
        
        if normalized_events:
            print("⚙️ [AgentOS] Routing Datadog anomalies to Universal Event Bus...")
            
            # Using your existing Event Bus directly!
            from core.event_bus import event_bus
            from core.models.event import UniversalEvent
            
            events_objs = [UniversalEvent(**e) for e in normalized_events]
            await event_bus.publish(events_objs)
            print("✅ [AgentOS] Datadog Observability Sync Complete!")
            
        return {"status": "synced", "events_processed": len(normalized_events)}

    async def webhook(self, payload: Dict[str, Any]) -> bool: pass
    async def disconnect(self) -> bool: pass