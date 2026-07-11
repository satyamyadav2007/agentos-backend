from typing import Dict, Any
from integrations.base import BaseConnector
from .client import YouTubeClient
from .services.sync_service import YouTubeSyncService

class YouTubeConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.yt_client = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        api_key = auth_payload.get("api_key")
        
        if not api_key:
            return {"status": "error", "message": "Missing YouTube API Key"}
            
        try:
            # Initialize Client
            self.yt_client = YouTubeClient(api_key=api_key)
            
            # Trigger Initial Sync (Mock video IDs - e.g., your product tutorials)
            sync_result = await self.sync()
            
            return {
                "status": "connected",
                "provider": "youtube",
                "sync_info": sync_result
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def sync(self) -> Dict[str, Any]:
        sync_service = YouTubeSyncService(self.yt_client)
        
        # Example: Array of Video IDs (e.g., onboarding tutorials or competitor reviews)
        target_videos = ["dQw4w9WgXcQ"] # Replace with real Video IDs
        normalized_events = await sync_service.run_full_sync(target_videos)
        
        if normalized_events:
            print("⚙️ [AgentOS] Handoff to AI Orchestrator started for YouTube Data...")
            from orchestrator import run_orchestrator
            await run_orchestrator(github_issues=normalized_events, user_email="satyam@startup.com")
            
        return {"status": "synced", "events_processed": len(normalized_events)}

    async def webhook(self, payload: Dict[str, Any]) -> bool: pass
    async def disconnect(self) -> bool: pass