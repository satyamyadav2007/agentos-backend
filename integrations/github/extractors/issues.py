# File: integrations/github/extractors/issues.py

from typing import List
from integrations.github.models.issue import GitHubIssueModel

class GitHubIssuesExtractor:
    """Handles data collection for GitHub Issues (Async)."""
    
    def __init__(self, client):
        self.client = client

    async def fetch_repository_issues(self, repo_full_name: str, state: str = "all") -> List[GitHubIssueModel]:
        print(f"🐛 [GitHub Extractor] Scanning issues for {repo_full_name}...")
        try:
            # Using the unified async client
            raw_data = await self.client.get(
                f"repos/{repo_full_name}/issues", 
                params={"state": state, "per_page": 100}
            )
            
            clean_issues = []
            for item in raw_data:
                # ⚡ CRITICAL FIX: GitHub API treats Pull Requests as issues. 
                # We skip them here using the Pydantic model's data.
                if "pull_request" in item:
                    continue
                    
                clean_issues.append(GitHubIssueModel(**item))
                
            print(f"   ✅ Successfully extracted {len(clean_issues)} issues from {repo_full_name}")
            return clean_issues
            
        except Exception as e:
            print(f"🚨 [GitHub Extractor] Failed to fetch issues for {repo_full_name}: {e}")
            return []