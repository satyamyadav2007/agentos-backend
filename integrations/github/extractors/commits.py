from typing import List
from integrations.github.models.commit import GitHubCommitModel

class GitHubCommitExtractor:
    """Handles data collection for GitHub Commits."""
    
    def __init__(self, client):
        self.client = client

    async def fetch_recent_commits(self, repo_full_name: str, branch: str = "main", limit: int = 50) -> List[GitHubCommitModel]:
        print(f"📜 [GitHub Extractor] Fetching recent commits for {repo_full_name} ({branch})...")
        try:
            raw_data = await self.client.get(
                f"repos/{repo_full_name}/commits", 
                params={"sha": branch, "per_page": limit}
            )
            
            commits = []
            for item in raw_data:
                commits.append(GitHubCommitModel(**item))
                
            print(f"   ✅ Extracted {len(commits)} commits from {repo_full_name}")
            return commits
            
        except Exception as e:
            print(f"🚨 [GitHub Extractor] Failed to fetch commits for {repo_full_name}: {e}")
            return []