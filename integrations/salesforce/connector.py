from typing import Dict, Any
from integrations.base import BaseConnector
from .oauth import SalesforceAuthManager
from .client import SalesforceClient
from .services.sync_service import SalesforceSyncService

class SalesforceConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.auth_manager = SalesforceAuthManager()
        self.sf_client = None
        self.instance_url = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        auth_code = auth_payload.get("auth_code")
        if not auth_code:
            return {"status": "error", "message": "Missing auth_code"}
            
        try:
            # 1. Exchange token
            token, instance_url = await self.auth_manager.authenticate(auth_code)
            self.instance_url = instance_url
            
            # 2. Initialize the Centralized Client
            self.sf_client = SalesforceClient(instance_url=instance_url, access_token=token)
            
            # 3. Trigger initial sync immediately
            sync_result = await self.sync()
            
            return {
                "status": "connected",
                "provider": "salesforce",
                "instance_url": instance_url,
                "sync_info": sync_result
            }
        except Exception as e:
            print(f"🚨 [Salesforce Connector Error]: {e}")
            return {"status": "error", "message": str(e)}

    async def sync(self) -> Dict[str, Any]:
        if not self.sf_client:
            return {"status": "error", "message": "Not authenticated"}
            
        sync_service = SalesforceSyncService(self.sf_client)
        normalized_events = await sync_service.run_full_sync()
        
        if normalized_events:
            print("⚙️ [AgentOS] Handoff to AI Orchestrator started for Salesforce data...")
            from orchestrator import run_orchestrator
            
            # Feeding Revenue data into the exact same AI pipeline!
            await run_orchestrator(github_issues=normalized_events, user_email="satyam@startup.com")
            print("✅ [AgentOS] AI Processing Complete for Salesforce Sync!")
        
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