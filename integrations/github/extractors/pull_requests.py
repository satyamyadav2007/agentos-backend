from typing import List
from integrations.github.models.pull_request import GitHubPullRequestModel

class GitHubPRExtractor:
    """Handles data collection for GitHub Pull Requests."""
    
    def __init__(self, client):
        self.client = client

    async def fetch_pull_requests(self, repo_full_name: str, state: str = "all") -> List[GitHubPullRequestModel]:
        print(f"🔄 [GitHub Extractor] Fetching PRs for {repo_full_name}...")
        try:
            raw_data = await self.client.get(
                f"repos/{repo_full_name}/pulls", 
                params={"state": state, "per_page": 100}
            )
            
            prs = []
            for item in raw_data:
                prs.append(GitHubPullRequestModel(**item))
                
            print(f"   ✅ Extracted {len(prs)} PRs from {repo_full_name}")
            return prs
            
        except Exception as e:
            print(f"🚨 [GitHub Extractor] Failed to fetch PRs for {repo_full_name}: {e}")
            return []