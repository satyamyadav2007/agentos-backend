from typing import Dict, Any
from integrations.base import BaseConnector
from .oauth import SlackOAuthManager
from .client import SlackClient
from .services.sync_service import SlackSyncService

class SlackConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.oauth_manager = SlackOAuthManager()
        self.slack_client = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        auth_code = auth_payload.get("auth_code")
        if not auth_code:
            return {"status": "error", "message": "Missing auth_code"}
            
        try:
            bot_token = await self.oauth_manager.authenticate(auth_code)
            self.slack_client = SlackClient(access_token=bot_token)
            
            # Trigger initial sync immediately after connect
            sync_result = await self.sync()
            
            return {
                "status": "connected",
                "provider": "slack",
                "sync_info": sync_result
            }
        except Exception as e:
            print(f"🚨 [Slack Connector Error]: {e}")
            return {"status": "error", "message": str(e)}

    async def sync(self) -> Dict[str, Any]:
        if not self.slack_client:
            return {"status": "error", "message": "Not authenticated"}
            
        sync_service = SlackSyncService(self.slack_client)
        normalized_events = await sync_service.run_full_sync()
        
        # Handoff to AgentOS AI Orchestrator
        if normalized_events:
            print("⚙️ [AgentOS] Handoff to AI Orchestrator started for Slack data...")
            from orchestrator import run_orchestrator
            
            # Using the EXACT SAME pipeline used for Jira and GitHub
            await run_orchestrator(github_issues=normalized_events, user_email="satyam@startup.com")
            print("✅ [AgentOS] AI Processing Complete for Slack Sync!")
        
        return {
            "status": "synced",
            "events_processed": len(normalized_events)
        }

    async def webhook(self, payload: Dict[str, Any]) -> bool:
        pass
    async def disconnect(self) -> bool:
        pass
    async def normalize(self, raw_data: Any) -> Any:
        pass