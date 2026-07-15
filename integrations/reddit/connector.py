from typing import Dict, Any
from integrations.base import BaseConnector
from .oauth import RedditAuthManager
from .client import RedditClient
from .services.sync_service import RedditSyncService

class RedditConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.auth_manager = RedditAuthManager()
        self.reddit_client = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        auth_code = auth_payload.get("auth_code")
        if not auth_code:
            return {"status": "error", "message": "Missing auth_code"}
            
        try:
            # 1. Get Token
            token = await self.auth_manager.authenticate(auth_code)
            
            # 2. Initialize Client
            self.reddit_client = RedditClient(access_token=token)
            
            # 3. Trigger Initial Sync
            sync_result = await self.sync()
            
            return {
                "status": "connected",
                "provider": "reddit",
                "sync_info": sync_result
            }
        except Exception as e:
            print(f"🚨 [Reddit Connector Error]: {e}")
            return {"status": "error", "message": str(e)}

    async def sync(self) -> Dict[str, Any]:
        if not self.reddit_client:
            return {"status": "error", "message": "Not authenticated"}
            
        sync_service = RedditSyncService(self.reddit_client)
        
        # Tracking our product and competitors
        tracking_keywords = ["AgentOS", "Jira", "Zendesk"]
        normalized_events = await sync_service.run_full_sync(tracking_keywords=tracking_keywords)
        
        if normalized_events:
            print("⚙️ [AgentOS] Handoff to AI Orchestrator started for Reddit Market Data...")
            from orchestrator import run_orchestrator
            
            await run_orchestrator(github_issues=normalized_events, user_email="satyam@startup.com")
            print("✅ [AgentOS] AI Processing Complete for Reddit Sync!")
        
        return {"status": "synced", "events_processed": len(normalized_events)}

    async def webhook(self, payload: Dict[str, Any]) -> bool:
        # Reddit lacks real-time webhooks for search/posts. This will rely on scheduled syncs.
        pass
        
    async def disconnect(self) -> bool:
        pass