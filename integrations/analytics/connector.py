from typing import Dict, Any
from integrations.base import BaseConnector
from .oauth import AnalyticsAuthManager
from .providers.posthog import PostHogProvider
from .providers.mixpanel import MixpanelProvider      # ⚡ Uncommented
from .providers.amplitude import AmplitudeProvider    # ⚡ Uncommented
from .services.sync_service import AnalyticsSyncService

class AnalyticsConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.auth_manager = AnalyticsAuthManager()
        self.active_provider = None
        self.provider_name = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        self.provider_name = auth_payload.get("provider", "").lower()
        api_key = auth_payload.get("api_key")
        project_id = auth_payload.get("project_id")
        
        if not all([self.provider_name, api_key, project_id]):
            return {"status": "error", "message": "Missing provider, api_key, or project_id"}
            
        try:
            # 1. Validate Keys
            is_valid = await self.auth_manager.validate_credentials(self.provider_name, api_key, project_id)
            if not is_valid:
                return {"status": "error", "message": f"Invalid {self.provider_name} credentials."}
            
            # 2. Factory: Initialize the correct Provider Class
            if self.provider_name == "posthog":
                self.active_provider = PostHogProvider(api_key=api_key, project_id=project_id)
            elif self.provider_name == "mixpanel":
                self.active_provider = MixpanelProvider(api_key=api_key, project_id=project_id)
            elif self.provider_name == "amplitude":
                self.active_provider = AmplitudeProvider(api_key=api_key, project_id=project_id)
            
            # 3. Trigger Initial Sync
            sync_result = await self.sync()
            
            return {
                "status": "connected",
                "provider": self.provider_name,
                "sync_info": sync_result
            }
        except Exception as e:
            print(f"🚨 [Analytics Connector Error]: {e}")
            return {"status": "error", "message": str(e)}
    async def sync(self) -> Dict[str, Any]:
        if not self.active_provider:
            return {"status": "error", "message": "No active analytics provider"}
            
        sync_service = AnalyticsSyncService(self.active_provider)
        normalized_events = await sync_service.run_full_sync()
        
        if normalized_events:
            print(f"⚙️ [AgentOS] Handoff to AI Orchestrator started for {self.provider_name} data...")
            from orchestrator import run_orchestrator
            
            await run_orchestrator(github_issues=normalized_events, user_email="satyam@startup.com")
            print(f"✅ [AgentOS] AI Processing Complete for {self.provider_name} Sync!")
        
        return {"status": "synced", "events_processed": len(normalized_events)}

    async def webhook(self, payload: Dict[str, Any]) -> bool:
        pass
    async def disconnect(self) -> bool:
        pass