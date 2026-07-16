from typing import Dict, Any, Optional
from integrations.base import BaseConnector
from .oauth import GitHubAuthManager
from database.postgres_setup import SessionLocal
from database.models import WorkspaceIntegration
import traceback

from .services.sync_service import GitHubSyncService
from .utils.client import GitHubClient

class GitHubConnector(BaseConnector):
    """Orchestrates the GitHub integration with a strict Universal Return Contract."""
    
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.auth_manager = GitHubAuthManager()
        self.access_token = None
        self.installation_id = None

    # ⚡ PURANA LOGIC: Satisfy BaseConnector strict requirements
    async def connect(self, *args, **kwargs): pass
    async def disconnect(self, *args, **kwargs): pass
    async def normalize(self, data, *args, **kwargs): return data
    async def webhook(self, request, *args, **kwargs): pass

    def _get_error_contract(self, message: str) -> Dict[str, Any]:
        """Strict failure contract ensuring the UI doesn't crash."""
        return {
            "provider": "github",
            "metrics": {"repositories": 0, "issues": 0, "pull_requests": 0, "commits": 0},
            "records": [],
            "cursor": None,
            "sync_status": "error",
            "message": message
        }

    async def sync(self, user_email: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetches real data from GitHub and returns it strictly matching the AgentOS Contract.
        """
        db = SessionLocal()
        try:
            print(f"🔍 [Connector] Looking up DB for Workspace: {self.workspace_id}")
            
            # ⚡ NAYA LOGIC: Fetch dynamically from Webhook-saved Postgres DB
            integration = db.query(WorkspaceIntegration).filter(
                WorkspaceIntegration.workspace_id == self.workspace_id,
                WorkspaceIntegration.provider == "github"
            ).first()

            if not integration or not integration.installation_id:
                return self._get_error_contract("No GitHub App installation found in Postgres DB.")

            self.installation_id = integration.installation_id
            print(f"🔑 [Connector] Database match found! Installation ID: {self.installation_id}")

            # Generate Fresh Token
            token_data = self.auth_manager.get_installation_token(self.installation_id)
            self.access_token = token_data.get("token") if isinstance(token_data, dict) else token_data

            if not self.access_token:
                return self._get_error_contract("Failed to generate secure GitHub Token.")

            # ⚡ NAYA LOGIC: Fire the massive async Sync Service
            client = GitHubClient(self.access_token)
            sync_service = GitHubSyncService(client)
            
            print("🚀 [Connector] Token verified. Executing modular extraction pipeline...")
            records = await sync_service.run_full_sync(
                installation_id=self.installation_id,
                workspace_id=self.workspace_id,
                db=db
            )

            # ⚡ PURANA LOGIC: Meticulous Metrics Calculation for the Dashboard
            unique_repos = set()
            issue_count = 0
            pr_count = 0
            commit_count = 0

            for record in records:
                repo_name = record.get("repository")
                if repo_name:
                    unique_repos.add(repo_name)
                    
                entity_type = record.get("entity_type")
                if entity_type == "issue":
                    issue_count += 1
                elif entity_type == "pull_request":
                    pr_count += 1
                elif entity_type == "commit":
                    commit_count += 1

            repo_count = len(unique_repos)
            print(f"✅ [GitHub Connector] Extracted {issue_count} issues, {pr_count} PRs, {commit_count} commits from {repo_count} repos.")

            # ⚡ PURANA LOGIC: The exact Universal AgentOS Contract 
            return {
                "provider": "github",
                "metrics": {
                    "repositories": repo_count,
                    "issues": issue_count,
                    "pull_requests": pr_count,
                    "commits": commit_count
                },
                "records": records,
                "cursor": "initial_sync_complete",
                "sync_status": "completed"
            }

        except Exception as e:
            print(f"🚨 [GitHub Extractor Error]: {e}")
            import traceback
            traceback.print_exc()
            return self._get_error_contract(str(e))
        finally:
            db.close()