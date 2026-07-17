from typing import Dict, Any, Optional
from integrations.base import BaseConnector
from database.postgres_setup import SessionLocal
from database.models import WorkspaceIntegration
import traceback

from .oauth import JiraAuthManager
from .client import JiraClient
from .services.sync_service import JiraSyncService

class JiraConnector(BaseConnector):
    """Enterprise Jira Connector with Postgres Persistence and Universal Sync Contract."""
    
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.auth_manager = JiraAuthManager()
        self.jira_client = None
        self.site_url = None
        self.cloud_id = None
        self.access_token = None

    def _get_error_contract(self, message: str) -> Dict[str, Any]:
        """Graceful failure contract to prevent UI crashes during sync failures."""
        return {
            "provider": "jira",
            "metrics": {"projects": 0, "epics": 0, "sprints": 0, "issues": 0},
            "records": [],
            "events_processed": 0,
            "sync_status": "error",
            "message": message
        }

    async def connect(self, auth_payload: Dict[str, Any], user_email: Optional[str] = None) -> Dict[str, Any]:
        """Handles OAuth exchange, saves Cloud ID to Postgres, and triggers initial sync."""
        auth_code = auth_payload.get("auth_code")
        if not auth_code:
            return {"status": "error", "message": "Missing auth_code"}
            
        db = SessionLocal()
        try:
            print(f"🔐 [Jira Connector] Authenticating workspace: {self.workspace_id}")
            
            # 1. Execute OAuth Exchange
            token, cloud_id, site_url = await self.auth_manager.authenticate(auth_code)
            self.access_token = token
            self.cloud_id = cloud_id
            self.site_url = site_url
            self.jira_client = JiraClient(access_token=token, cloud_id=cloud_id)
            
            # 2. 🐘 Database Persistence (Mapping Jira data to your schema)
            existing = db.query(WorkspaceIntegration).filter(
                WorkspaceIntegration.workspace_id == self.workspace_id,
                WorkspaceIntegration.provider == "jira"
            ).first()

            if existing:
                existing.installation_id = str(cloud_id) # Saving Jira Cloud ID
                existing.account_name = site_url         # Saving Jira Site URL
                existing.is_active = True
            else:
                new_integration = WorkspaceIntegration(
                    workspace_id=self.workspace_id,
                    provider="jira",
                    installation_id=str(cloud_id),
                    account_name=site_url
                )
                db.add(new_integration)
            
            db.commit()
            print(f"✅ [DB] Jira Integration saved for Workspace {self.workspace_id}")

            # 3. Trigger Initial Sync dynamically
            sync_result = await self.sync(user_email=user_email)
            
            return {
                "status": "connected",
                "provider": "jira",
                "site_url": site_url,
                "sync_info": sync_result
            }

        except Exception as e:
            db.rollback()
            print(f"🚨 [Jira Connector Error]: {e}")
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    async def sync(self, user_email: Optional[str] = None) -> Dict[str, Any]:
        """Executes the full intelligence extraction and returns the Universal Contract."""
        db = SessionLocal()
        try:
            # 1. Fetch Cloud ID from DB for background syncs (When UI isn't actively connecting)
            if not self.cloud_id or not self.access_token:
                integration = db.query(WorkspaceIntegration).filter(
                    WorkspaceIntegration.workspace_id == self.workspace_id,
                    WorkspaceIntegration.provider == "jira"
                ).first()

                if not integration or not integration.installation_id:
                    return self._get_error_contract("No Jira integration found in Postgres DB.")

                self.cloud_id = integration.installation_id
                self.site_url = integration.account_name
                
                # NOTE: For future background cron jobs, refresh token logic goes here.
                # Assuming access_token is temporarily available via auth manager for MVP
                if not self.access_token:
                     return self._get_error_contract("Access token missing. Re-authentication required.")
                     
                self.jira_client = JiraClient(access_token=self.access_token, cloud_id=self.cloud_id)

            print("🚀 [Jira Connector] Handing over to Enterprise Sync Service...")
            
            # 2. Fire the Sync Service
            sync_service = JiraSyncService(self.jira_client)
            normalized_events = await sync_service.run_full_sync()

            # 3. Calculate Meticulous Metrics for the Dashboard
            project_count = len(set(e.get("metadata", {}).get("project_key") for e in normalized_events if "metadata" in e))
            issue_count = len([e for e in normalized_events if e.get("entity_type") == "issue"])
            epic_count = len([e for e in normalized_events if e.get("entity_type") == "epic"])
            sprint_count = len([e for e in normalized_events if e.get("entity_type") == "sprint"])

            print(f"✅ [Jira Connector] Processed {issue_count} issues, {epic_count} epics, {sprint_count} sprints from {project_count} projects.")

            # 4. The Universal AgentOS Contract 
            return {
                "provider": "jira",
                "metrics": {
                    "projects": project_count,
                    "epics": epic_count,
                    "sprints": sprint_count,
                    "issues": issue_count
                },
                "records": normalized_events,
                "events_processed": len(normalized_events),
                "sync_status": "completed"
            }

        except Exception as e:
            print(f"🚨 [Jira Sync Error]: {e}")
            traceback.print_exc()
            return self._get_error_contract(str(e))
        finally:
            db.close()
            
    # Required BaseConnector methods
    async def disconnect(self, *args, **kwargs): pass
    async def normalize(self, data, *args, **kwargs): return data
    async def webhook(self, request, *args, **kwargs): pass