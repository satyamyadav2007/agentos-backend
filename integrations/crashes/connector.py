from typing import Dict, Any
from integrations.base import BaseConnector
from .oauth import CrashesAuthManager
from .providers.sentry import SentryProvider
from .providers.crashlytics import CrashlyticsProvider
from .services.sync_service import CrashSyncService

class CrashesConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.auth_manager = CrashesAuthManager()
        self.active_provider = None
        self.provider_name = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        self.provider_name = auth_payload.get("provider", "").lower()
        api_key = auth_payload.get("api_key")
        org_slug = auth_payload.get("org_slug")
        project_slug = auth_payload.get("project_slug") # Serves as app_id for Crashlytics
        
        if not all([self.provider_name, api_key, org_slug, project_slug]):
            return {"status": "error", "message": "Missing credentials or slugs."}
            
        try:
            # 1. Validate Keys
            is_valid = await self.auth_manager.validate_credentials(self.provider_name, api_key, org_slug, project_slug)
            if not is_valid:
                return {"status": "error", "message": f"Invalid {self.provider_name} credentials."}
            
            # 2. Factory Initialization
            if self.provider_name == "sentry":
                self.active_provider = SentryProvider(api_key, org_slug, project_slug)
            elif self.provider_name == "crashlytics":
                self.active_provider = CrashlyticsProvider(api_key, org_slug, project_slug)
            
            # 3. Trigger Initial Sync
            sync_result = await self.sync()
            
            return {
                "status": "connected",
                "provider": self.provider_name,
                "sync_info": sync_result
            }
        except Exception as e:
            print(f"🚨 [Crashes Connector Error]: {e}")
            return {"status": "error", "message": str(e)}

    async def sync(self) -> Dict[str, Any]:
        if not self.active_provider:
            return {"status": "error", "message": "No active crash provider"}
            
        sync_service = CrashSyncService(self.active_provider)
        normalized_events = await sync_service.run_full_sync()
        
        if normalized_events:
            print(f"⚙️ [AgentOS] AI Incident Commander initializing for {self.provider_name} crashes...")
            from orchestrator import run_orchestrator
            
            # This triggers the massive AI Root Cause & ARR Risk calculation pipeline!
            await run_orchestrator(github_issues=normalized_events, user_email="satyam@startup.com")
            print(f"✅ [AgentOS] AI Incident Commander Complete!")
        
        return {"status": "synced", "crashes_processed": len(normalized_events)}

    async def webhook(self, payload: Dict[str, Any]) -> bool:
        pass
    async def disconnect(self) -> bool:
        pass