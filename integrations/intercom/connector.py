from typing import Dict, Any
from integrations.base import BaseConnector
from .oauth import IntercomAuthManager
from .client import IntercomClient
from .services.sync_service import IntercomSyncService

class IntercomConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.auth_manager = IntercomAuthManager()
        self.intercom_client = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        auth_code = auth_payload.get("auth_code")
        if not auth_code:
            return {"status": "error", "message": "Missing auth_code"}
            
        try:
            token = await self.auth_manager.authenticate(auth_code)
            self.intercom_client = IntercomClient(access_token=token)
            
            # Initial Data Sync 
            sync_result = await self.sync()
            
            return {
                "status": "connected",
                "provider": "intercom",
                "sync_info": sync_result
            }
        except Exception as e:
            print(f"🚨 [Intercom Connector Error]: {e}")
            return {"status": "error", "message": str(e)}

    async def sync(self) -> Dict[str, Any]:
        if not self.intercom_client:
            return {"status": "error", "message": "Not authenticated"}
            
        sync_service = IntercomSyncService(self.intercom_client)
        normalized_events = await sync_service.run_full_sync()
        
        if normalized_events:
            print("⚙️ [AgentOS] Handoff to AI Orchestrator started for Intercom data...")
            from orchestrator import run_orchestrator
            
            await run_orchestrator(github_issues=normalized_events, user_email="satyam@startup.com")
            print("✅ [AgentOS] AI Processing Complete for Intercom Sync!")
        
        return {"status": "synced", "events_processed": len(normalized_events)}

    async def webhook(self, payload: Dict[str, Any]) -> bool:
        pass
    async def disconnect(self) -> bool:
        pass
    async def normalize(self, raw_data: Any) -> Any:
        pass