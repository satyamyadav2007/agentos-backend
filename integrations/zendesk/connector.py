from typing import Dict, Any
from integrations.base import BaseConnector
from .oauth import ZendeskAuthManager
from .client import ZendeskClient
from .services.sync_service import ZendeskSyncService

class ZendeskConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.auth_manager = ZendeskAuthManager()
        self.zendesk_client = None
        self.subdomain = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        auth_code = auth_payload.get("auth_code")
        self.subdomain = auth_payload.get("subdomain")
        
        if not auth_code or not self.subdomain:
            return {"status": "error", "message": "Missing auth_code or subdomain"}
            
        try:
            token = await self.auth_manager.authenticate(auth_code, self.subdomain)
            self.zendesk_client = ZendeskClient(subdomain=self.subdomain, access_token=token, is_oauth=True)
            
            # Trigger initial sync immediately after connect
            sync_result = await self.sync()
            
            return {
                "status": "connected",
                "provider": "zendesk",
                "subdomain": self.subdomain,
                "sync_info": sync_result
            }
        except Exception as e:
            print(f"🚨 [Zendesk Connector Error]: {e}")
            return {"status": "error", "message": str(e)}

    async def sync(self) -> Dict[str, Any]:
        if not self.zendesk_client:
            return {"status": "error", "message": "Not authenticated"}
            
        sync_service = ZendeskSyncService(self.zendesk_client)
        normalized_events = await sync_service.run_full_sync()
        
        if normalized_events:
            print("⚙️ [AgentOS] Handoff to AI Orchestrator started for Zendesk data...")
            from orchestrator import run_orchestrator
            
            # Using the EXACT SAME pipeline
            await run_orchestrator(github_issues=normalized_events, user_email="satyam@startup.com")
            print("✅ [AgentOS] AI Processing Complete for Zendesk Sync!")
        
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