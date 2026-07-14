from typing import Dict, Any
from integrations.base import BaseConnector
from .oauth import GitHubAuthManager
from .client import GitHubClient
from .services.sync_service import GitHubSyncService

class GitHubConnector(BaseConnector):
    """Orchestrates the GitHub integration lifecycle."""
    
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.oauth_manager = GitHubAuthManager()
        self.github_client = None
        self.installation_id = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Triggered when user installs the GitHub App."""
        self.installation_id = auth_payload.get("installation_id")
        
        if not self.installation_id:
            return {"status": "error", "message": "Missing installation_id"}
            
        try:
            # 1. Exchange installation_id for an API token
            # ⚡ FIX: Removed 'await' because get_installation_token is a synchronous requests call
            token = self.oauth_manager.get_installation_token(self.installation_id)
            
            # 2. Initialize the Centralized Client
            self.github_client = GitHubClient(access_token=token)
            
            # 3. Trigger initial sync immediately after connect
            # Passing user_email if it's available in the payload
            user_email = auth_payload.get("user_email")
            sync_result = await self.sync(user_email=user_email)
            
            return {
                "status": "connected",
                "provider": "github",
                "sync_info": sync_result
            }
        except Exception as e:
            print(f"🚨 [GitHub Connector Error]: {e}")
            return {"status": "error", "message": str(e)}

    # ⚡ FIX: Added user_email parameter with a default value
    async def sync(self, user_email: str = None) -> Dict[str, Any]:
        """Runs the full data extraction and AI handoff pipeline."""
        if not self.github_client or not self.installation_id:
            return {"status": "error", "message": "Not authenticated"}
            
        # 1. Initialize Sync Service (The Brain)
        sync_service = GitHubSyncService(self.github_client)
        
        # 2. Run extraction and normalization
        normalized_events = await sync_service.run_full_sync(self.installation_id)
        
        # 3. Handoff to AgentOS Orchestrator
        if normalized_events:
            print(f"⚙️ [AgentOS] Handoff to AI Orchestrator started for GitHub data (User: {user_email})...")
            from orchestrator import run_orchestrator
            
            # ⚡ FIX: Replaced hardcoded email with the dynamic user_email
            target_email = user_email or "fallback@domain.com"
            await run_orchestrator(github_issues=normalized_events, user_email=target_email)
            print("✅ [AgentOS] AI Processing Complete for GitHub Sync!")
            
        return {
            "status": "synced",
            "events_processed": len(normalized_events) if normalized_events else 0
        }

    async def webhook(self, payload: Dict[str, Any]) -> bool:
        # The webhook logic is handled in webhook.py and routed from main.py
        pass

    async def disconnect(self) -> bool:
        pass