from typing import Dict, Any
import traceback
from integrations.base import BaseConnector
from database.postgres_setup import SessionLocal
from database.models import WorkspaceIntegration
from .oauth import SlackAuthManager
from .client import SlackClient
from .services.sync_service import SlackSyncService

class SlackConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.auth_manager = SlackAuthManager()
        self.slack_client = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        auth_code = auth_payload.get("auth_code")
        if not auth_code:
            return {"status": "error", "message": "Missing auth_code"}
            
        db = SessionLocal()
        try:
            # 1. Exchange auth_code for bot_token
            bot_token = await self.auth_manager.authenticate(auth_code)
            self.slack_client = SlackClient(access_token=bot_token)
            
            # 2. 🐘 Database Persistence Logic
            existing = db.query(WorkspaceIntegration).filter(
                WorkspaceIntegration.workspace_id == self.workspace_id,
                WorkspaceIntegration.provider == "slack"
            ).first()

            if existing:
                existing.access_token = bot_token
                existing.is_active = True
            else:
                new_integration = WorkspaceIntegration(
                    workspace_id=self.workspace_id,
                    provider="slack",
                    access_token=bot_token
                )
                db.add(new_integration)
            
            db.commit()
            print(f"✅ [DB] Slack Integration saved for Workspace {self.workspace_id}")
            
            # 3. Trigger initial sync immediately after connect
            sync_result = await self.sync()
            
            return {
                "status": "connected",
                "provider": "slack",
                "sync_info": sync_result
            }
        except Exception as e:
            db.rollback()
            print(f"🚨 [Slack Connector Error]: {e}")
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    async def sync(self) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            # 1. Fetch from DB if running in background without active client
            if not self.slack_client:
                existing = db.query(WorkspaceIntegration).filter(
                    WorkspaceIntegration.workspace_id == self.workspace_id,
                    WorkspaceIntegration.provider == "slack",
                    WorkspaceIntegration.is_active == True
                ).first()

                if not existing or not existing.access_token:
                    return {"status": "error", "message": "No active Slack integration found in DB."}

                self.slack_client = SlackClient(access_token=existing.access_token)
                
            # 2. Run Sync Process
            sync_service = SlackSyncService(self.slack_client)
            normalized_events = await sync_service.run_full_sync()
            
            # 3. Handoff to AgentOS AI Orchestrator
            if normalized_events:
                print(f"⚙️ [AgentOS] Handoff {len(normalized_events)} Slack events to AI Orchestrator...")
                from orchestrator import run_orchestrator
                
                # Using the EXACT SAME pipeline used for Jira and GitHub
                await run_orchestrator(github_issues=normalized_events, user_email="satyam@startup.com")
                print("✅ [AgentOS] AI Processing Complete for Slack Sync!")
            
            return {
                "status": "synced",
                "events_processed": len(normalized_events)
            }
        except Exception as e:
            print(f"🚨 [Slack Sync Error]: {e}")
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    async def webhook(self, payload: Dict[str, Any]) -> bool:
        pass
        
    async def disconnect(self) -> bool:
        pass
        
    async def normalize(self, raw_data: Any) -> Any:
        pass