from typing import Dict, Any
from integrations.base import BaseConnector
from .extractors.posts import CommunityExtractor
from .models.post import CommunityPostModel

class CommunityNormalizer:
    @staticmethod
    def normalize_post(post: CommunityPostModel) -> Dict[str, Any]:
        severity = "High" if post.is_trending else "Medium"
        return {
            "source": "community",
            "entity_type": "discussion",
            "repository": "User_Forum",
            "title": post.title,
            "description": post.content,
            "author": post.author_username,
            "severity": severity,
            "timestamp": post.created_at.isoformat(),
            "metadata": {"topic_id": post.id, "views": post.views, "replies": post.reply_count}
        }

class CommunityConnector(BaseConnector):
    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        self.api_key = auth_payload.get("api_key")
        self.domain = auth_payload.get("domain")
        return {"status": "connected", "provider": "community", "sync_info": await self.sync()}

    async def sync(self) -> Dict[str, Any]:
        extractor = CommunityExtractor(self.api_key, self.domain)
        posts = await extractor.fetch_recent_discussions()
        
        normalized_events = [CommunityNormalizer.normalize_post(p) for p in posts]
        
        if normalized_events:
            print("⚙️ [AgentOS] Routing Community data to Universal Event Bus...")
            from core.event_bus import event_bus
            from core.models.event import UniversalEvent
            
            await event_bus.publish([UniversalEvent(**e) for e in normalized_events])
            print("✅ [AgentOS] Community Intelligence Sync Complete!")
            
        return {"status": "synced", "events": len(normalized_events)}