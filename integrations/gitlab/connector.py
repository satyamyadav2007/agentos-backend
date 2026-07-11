from typing import Dict, Any, List
from integrations.base import BaseConnector
from .client import GitLabClient
from .extractors.pipelines import GitLabDevSecOpsExtractor
from .normalizer import GitLabNormalizer

class GitLabSyncService:
    def __init__(self, client):
        self.client = client
        self.devops_extractor = GitLabDevSecOpsExtractor(client)
        
    async def run_full_sync(self, target_projects: List[str]) -> List[Dict[str, Any]]:
        print("\n🚀 [GitLab Sync] Starting Enterprise DevSecOps Sync...")
        all_universal_events = []
        
        for project_id in target_projects:
            pipelines = await self.devops_extractor.fetch_recent_pipelines(project_id)
            
            for pipeline in pipelines:
                all_universal_events.append(GitLabNormalizer.normalize_pipeline(pipeline))
                
        print(f"🧠 [AgentOS Brain] Normalized {len(all_universal_events)} GitLab DevSecOps events!")
        return all_universal_events

class GitLabConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.gitlab_client = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        token = auth_payload.get("token") # OAuth or Personal Access Token
        host = auth_payload.get("host", "https://gitlab.com")
        
        if not token:
            return {"status": "error", "message": "Missing GitLab Token"}
            
        try:
            self.gitlab_client = GitLabClient(token, host)
            sync_result = await self.sync()
            return {"status": "connected", "provider": "gitlab", "sync_info": sync_result}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def sync(self) -> Dict[str, Any]:
        if not self.gitlab_client:
            return {"status": "error", "message": "Not authenticated"}
            
        sync_service = GitLabSyncService(self.gitlab_client)
        
        # Hardcoded for MVP. Production uses Discovery Engine.
        target_projects = ["YOUR_PROJECT_ID"] 
        
        normalized_events = await sync_service.run_full_sync(target_projects)
        
        if normalized_events:
            print("⚙️ [AgentOS] Routing GitLab CI/CD data to Universal Event Bus...")
            from core.event_bus import event_bus
            from core.models.event import UniversalEvent
            
            events_objs = [UniversalEvent(**e) for e in normalized_events]
            await event_bus.publish(events_objs)
            print("✅ [AgentOS] Enterprise DevSecOps Sync Complete!")
            
        return {"status": "synced", "events_processed": len(normalized_events)}

    async def webhook(self, payload: Dict[str, Any]) -> bool: pass
    async def disconnect(self) -> bool: pass