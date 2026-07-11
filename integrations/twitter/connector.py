from typing import Dict, Any, List
from integrations.base import BaseConnector
from .client import TwitterClient
from .extractors.tweets import TweetExtractor
from .normalizer import TwitterNormalizer

class TwitterSyncService:
    def __init__(self, client):
        self.client = client
        self.tweet_extractor = TweetExtractor(client)
        
    async def run_full_sync(self, tracking_query: str) -> List[Dict[str, Any]]:
        print(f"\n🚀 [Twitter Sync] Starting Crisis & Brand Intelligence Sync...")
        
        tweets = await self.tweet_extractor.fetch_brand_mentions(query=tracking_query, limit=50)
        all_universal_events = [TwitterNormalizer.normalize_tweet(t, tracking_query) for t in tweets]
                
        print(f"🧠 [AgentOS Brain] Normalized {len(all_universal_events)} Public Mentions!")
        return all_universal_events


class TwitterConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.twitter_client = None
        self.tracking_query = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        bearer_token = auth_payload.get("bearer_token")
        self.tracking_query = auth_payload.get("tracking_query", "AgentOS") # Default brand track
        
        if not bearer_token:
            return {"status": "error", "message": "Missing Twitter Bearer Token"}
            
        try:
            self.twitter_client = TwitterClient(bearer_token)
            sync_result = await self.sync()
            return {"status": "connected", "provider": "twitter", "sync_info": sync_result}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def sync(self) -> Dict[str, Any]:
        if not self.twitter_client:
            return {"status": "error", "message": "Not authenticated"}
            
        sync_service = TwitterSyncService(self.twitter_client)
        normalized_events = await sync_service.run_full_sync(self.tracking_query)
        
        if normalized_events:
            print("⚙️ [AgentOS] Routing Public Mentions to Universal Event Bus...")
            
            # Using your perfectly established Event Bus architecture!
            from core.event_bus import event_bus
            from core.models.event import UniversalEvent
            
            events_objs = [UniversalEvent(**e) for e in normalized_events]
            await event_bus.publish(events_objs)
            print("✅ [AgentOS] Twitter/X Intelligence Sync Complete!")
            
        return {"status": "synced", "events_processed": len(normalized_events)}

    async def webhook(self, payload: Dict[str, Any]) -> bool: pass
    async def disconnect(self) -> bool: pass