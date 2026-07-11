from typing import Dict, Any, List
from integrations.base import BaseConnector
from .providers.appstore import AppStoreProvider
from .providers.googleplay import GooglePlayProvider
from .providers.chrome import ChromeWebStoreProvider
from .normalizer import ReviewsNormalizer

class ReviewsSyncService:
    def __init__(self, provider):
        self.provider = provider
        
    async def run_full_sync(self) -> List[Dict[str, Any]]:
        print(f"\n🚀 [Reviews Sync] Starting Public Product Feedback Sync...")
        
        reviews = await self.provider.fetch_recent_reviews(limit=30)
        all_universal_events = [ReviewsNormalizer.normalize_review(r) for r in reviews]
                
        print(f"🧠 [AgentOS Brain] Normalized {len(all_universal_events)} Public App Reviews!")
        return all_universal_events


class ReviewsConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.active_provider = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        provider_name = auth_payload.get("provider", "").lower()
        app_id = auth_payload.get("app_id")
        
        if not provider_name or not app_id:
            return {"status": "error", "message": "Missing Provider or App ID"}
            
        try:
            # ⚡ Dynamic Provider Initialization based on Frontend Selection
            if provider_name == "appstore":
                self.active_provider = AppStoreProvider(app_id)
            elif provider_name == "googleplay":
                self.active_provider = GooglePlayProvider(app_id)
            elif provider_name == "chrome":
                self.active_provider = ChromeWebStoreProvider(app_id)
            else:
                return {"status": "error", "message": "Invalid Review Provider"}
                
            sync_result = await self.sync()
            return {"status": "connected", "provider": f"reviews_{provider_name}", "sync_info": sync_result}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    async def sync(self) -> Dict[str, Any]:
        if not self.active_provider:
            return {"status": "error", "message": "No active review provider"}
            
        sync_service = ReviewsSyncService(self.active_provider)
        normalized_events = await sync_service.run_full_sync()
        
        if normalized_events:
            print("⚙️ [AgentOS] Routing Public Reviews to Universal Event Bus...")
            
            # Leveraging your rock-solid unified architecture!
            from core.event_bus import event_bus
            from core.models.event import UniversalEvent
            
            events_objs = [UniversalEvent(**e) for e in normalized_events]
            await event_bus.publish(events_objs)
            print("✅ [AgentOS] Reviews Intelligence Sync Complete!")
            
        return {"status": "synced", "events_processed": len(normalized_events)}

    async def webhook(self, payload: Dict[str, Any]) -> bool: pass
    async def disconnect(self) -> bool: pass