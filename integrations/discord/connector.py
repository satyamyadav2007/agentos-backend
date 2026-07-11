from typing import Dict, Any
from integrations.base import BaseConnector
from .oauth import DiscordOAuthManager
from .client import DiscordClient
from .services.sync_service import DiscordSyncService

class DiscordConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.oauth_manager = DiscordOAuthManager()
        self.discord_client = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        auth_code = auth_payload.get("auth_code")
        if not auth_code:
            return {"status": "error", "message": "Missing auth_code"}
            
        try:
            # 1. Get Token
            token = await self.oauth_manager.authenticate(auth_code)
            
            # Note: For reading all community messages, you typically use a Bot Token. 
            # We initialize client with the OAuth token for user-specific actions, 
            # but in production, you might fallback to a static Bot Token for global server scraping.
            self.discord_client = DiscordClient(token=token, is_bot=False)
            
            # 2. Trigger Initial Sync
            sync_result = await self.sync()
            
            return {
                "status": "connected",
                "provider": "discord",
                "sync_info": sync_result
            }
        except Exception as e:
            print(f"🚨 [Discord Connector Error]: {e}")
            return {"status": "error", "message": str(e)}

    async def sync(self) -> Dict[str, Any]:
        if not self.discord_client:
            return {"status": "error", "message": "Not authenticated"}
            
        sync_service = DiscordSyncService(self.discord_client)
        
        # NOTE: Ideally these channel IDs come from a database config. Hardcoded for testing.
        target_channels = ["YOUR_CHANNEL_ID_1", "YOUR_CHANNEL_ID_2"]
        normalized_events = await sync_service.run_full_sync(target_channel_ids=target_channels)
        
        if normalized_events:
            print("⚙️ [AgentOS] Handoff to AI Orchestrator started for Discord Community data...")
            from orchestrator import run_orchestrator
            
            await run_orchestrator(github_issues=normalized_events, user_email="satyam@startup.com")
            print("✅ [AgentOS] AI Processing Complete for Discord Sync!")
        
        return {"status": "synced", "events_processed": len(normalized_events)}

    async def webhook(self, payload: Dict[str, Any]) -> bool:
        pass
    async def disconnect(self) -> bool:
        pass