from typing import Dict, Any, List
from integrations.base import BaseConnector
from .client import BitbucketClient
from .extractors.prs import BitbucketPRExtractor
from .normalizer import BitbucketNormalizer

class BitbucketSyncService:
    def __init__(self, client):
        self.client = client
        self.pr_extractor = BitbucketPRExtractor(client)
        
    async def run_full_sync(self, target_repos: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        print(f"\n🚀 [Bitbucket Sync] Starting Enterprise Source Code Intelligence Sync...")
        all_universal_events = []
        
        for repo in target_repos:
            workspace = repo.get("workspace")
            repo_slug = repo.get("repo_slug")
            
            prs = await self.pr_extractor.fetch_recent_prs(workspace, repo_slug, limit=30)
            for pr in prs:
                all_universal_events.append(BitbucketNormalizer.normalize_pr(pr))
                
        print(f"🧠 [AgentOS Brain] Normalized {len(all_universal_events)} Bitbucket events!")
        return all_universal_events


class BitbucketConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.bitbucket_client = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        token = auth_payload.get("token")
        username = auth_payload.get("username") # Required if using App Passwords
        is_basic_auth = bool(username)
        
        if not token:
            return {"status": "error", "message": "Missing Bitbucket Token"}
            
        try:
            self.bitbucket_client = BitbucketClient(token, is_basic_auth, username)
            sync_result = await self.sync()
            return {"status": "connected", "provider": "bitbucket", "sync_info": sync_result}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def sync(self) -> Dict[str, Any]:
        if not self.bitbucket_client:
            return {"status": "error", "message": "Not authenticated"}
            
        sync_service = BitbucketSyncService(self.bitbucket_client)
        
        # Hardcoded target for MVP. Will be dynamic via Discovery Engine later.
        target_repos = [
            {"workspace": "YOUR_WORKSPACE", "repo_slug": "YOUR_REPO_SLUG"}
        ]
        
        normalized_events = await sync_service.run_full_sync(target_repos)
        
        if normalized_events:
            print("⚙️ [AgentOS] Routing Bitbucket data to Universal Event Bus...")
            
            # Using your EXACT existing architecture import here!
            from core.event_bus import event_bus
            from core.models.event import UniversalEvent
            
            events_objs = [UniversalEvent(**e) for e in normalized_events]
            await event_bus.publish(events_objs)
            print("✅ [AgentOS] Bitbucket Source Code Sync Complete!")
            
        return {"status": "synced", "events_processed": len(normalized_events)}

    async def webhook(self, payload: Dict[str, Any]) -> bool:
        pass
        
    async def disconnect(self) -> bool:
        pass