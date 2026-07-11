from typing import Dict, Any, List
from integrations.base import BaseConnector
from .oauth import GitHubAuthManager
from .discovery import GitHubDiscovery
from .extractors.issues import GitHubIssuesExtractor
from .extractors.prs import GitHubPRExtractor      # ⚡ Naya import
from .normalizer import GitHubNormalizer  
        # ⚡ Naya import

class GitHubConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.auth_manager = GitHubAuthManager()
        self.installation_id = None 
        self.access_token = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        self.installation_id = auth_payload.get("installation_id")
        if not self.installation_id:
            return {"status": "error", "message": "Missing installation_id"}
        try:
            self.access_token = self.auth_manager.get_installation_token(self.installation_id)
            return {"status": "connected", "provider": "github"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ==========================================
    # 🔄 DATA PIPELINE: Discovery -> Extract -> Normalize
    # ==========================================
    async def sync(self) -> Dict[str, Any]:
        if not self.access_token:
            return {"status": "error", "message": "Not authenticated"}

        discovery_engine = GitHubDiscovery(token=self.access_token)
        repos = discovery_engine.fetch_repositories()
        
        issues_engine = GitHubIssuesExtractor(token=self.access_token)
        prs_engine = GitHubPRExtractor(token=self.access_token)
        
        normalized_events = []
        
        for repo in repos:
            repo_name = repo["full_name"]
            
            # 1. Fetch & Normalize Issues
            raw_issues = issues_engine.fetch_issues(repo_full_name=repo_name)
            for issue in raw_issues:
                normalized = GitHubNormalizer.normalize_issue(issue, repo_name)
                normalized_events.append(normalized)
                
            # 2. Fetch & Normalize PRs
            raw_prs = prs_engine.fetch_prs(repo_full_name=repo_name)
            for pr in raw_prs:
                normalized = GitHubNormalizer.normalize_pr(pr, repo_name)
                normalized_events.append(normalized)
            
        # ... connector.py ka baaki sync() code ...
    
        print(f"\n🧠 [AgentOS Brain] Normalized {len(normalized_events)} total events from GitHub!")
        
        # Agar data hai, toh AgentOS Orchestrator (AI) ko trigger karo!
        if normalized_events:
            print("⚙️ [AgentOS] Handoff to AI Orchestrator started...")
            
            # ⚡ FIX: Import ko yahan andar daalo taaki Circular Import error na aaye!
            from orchestrator import run_orchestrator 
            
            # Email abhi ke liye dummy pass kar rahe hain
            orchestrator_result = await run_orchestrator(github_issues=normalized_events, user_email="satyam@startup.com")
            print("✅ [AgentOS] AI Processing Complete for Sync!")
            
        return {
            "status": "synced",
            "repositories_found": len(repos),
            "events_processed": len(normalized_events)
        }

    async def webhook(self, payload: Dict[str, Any]) -> bool:
        pass
    async def disconnect(self) -> bool:
        pass
    async def normalize(self, raw_data: Any) -> Any:
        pass