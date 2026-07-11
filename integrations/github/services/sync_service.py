from typing import Dict, Any, List
from integrations.github.discovery import GitHubDiscovery
from integrations.github.extractors.issues import GitHubIssuesExtractor
# from integrations.github.extractors.pull_requests import GitHubPRExtractor
from integrations.github.normalizer import GitHubNormalizer

class GitHubSyncService:
    """Orchestrates extraction, validation, and normalization for the entire integration."""
    
    def __init__(self, client):
        self.client = client
        self.discovery = GitHubDiscovery(client)
        self.issues_extractor = GitHubIssuesExtractor(client)
        # self.pr_extractor = GitHubPRExtractor(client)
        
    async def run_full_sync(self, installation_id: str) -> List[Dict[str, Any]]:
        print("\n🚀 [GitHub Sync Service] Starting Full Organization Sync...")
        
        # 1. Discover Repositories
        repos = await self.discovery.fetch_authorized_repos(installation_id)
        
        all_universal_events = []
        
        # 2. Extract Data per Repository
        for repo in repos:
            repo_name = repo["full_name"]
            
            # Extract Issues
            issues_models = await self.issues_extractor.fetch_repository_issues(repo_name)
            
            # Extract PRs (Once you create pull_requests.py)
            # prs_models = await self.pr_extractor.fetch_pull_requests(repo_name)
            
            # 3. Normalize to AgentOS Universal Format
            for issue in issues_models:
                # Passing the Pydantic model's dict representation to the normalizer
                normalized = GitHubNormalizer.normalize_issue(issue.model_dump(), repo_name)
                all_universal_events.append(normalized)
                
        print(f"🧠 [AgentOS Brain] Normalized {len(all_universal_events)} total events from GitHub!")
        return all_universal_events