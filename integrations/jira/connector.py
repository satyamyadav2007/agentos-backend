from typing import Dict, Any
from integrations.base import BaseConnector
from .oauth import JiraOAuthManager
from .client import JiraClient
from .services.sync_service import JiraSyncService

class JiraConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.oauth_manager = JiraOAuthManager()
        self.jira_client = None
        self.site_url = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        auth_code = auth_payload.get("auth_code")
        if not auth_code:
            return {"status": "error", "message": "Missing auth_code"}
            
        try:
            token, cloud_id, site_url = await self.oauth_manager.authenticate(auth_code)
            self.jira_client = JiraClient(access_token=token, cloud_id=cloud_id)
            self.site_url = site_url
            
            # Trigger initial sync immediately after connect
            sync_result = await self.sync()
            
            return {
                "status": "connected",
                "provider": "jira",
                "site_url": site_url,
                "sync_info": sync_result
            }
        except Exception as e:
            print(f"🚨 [Jira Connector Error]: {e}")
            return {"status": "error", "message": str(e)}

    async def sync(self) -> Dict[str, Any]:
        if not self.jira_client:
            return {"status": "error", "message": "Not authenticated"}
            
        # Call the dedicated Sync Service
        sync_service = JiraSyncService(self.jira_client)
        normalized_events = await sync_service.run_full_sync()
        
        # Handoff to AgentOS Orchestrator
        if normalized_events:
            print("⚙️ [AgentOS] Handoff to AI Orchestrator started for Jira data...")
            from orchestrator import run_orchestrator
            
            # Using the identical orchestrator pipeline we built for GitHub!
            await run_orchestrator(github_issues=normalized_events, user_email="satyam@startup.com")
            print("✅ [AgentOS] AI Processing Complete for Jira Sync!")
        
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