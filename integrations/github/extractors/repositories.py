from typing import List
from integrations.github.models.repository import GitHubRepositoryModel

class GitHubRepositoryExtractor:
    """Handles data collection for GitHub Repositories."""
    
    def __init__(self, client):
        self.client = client

    async def fetch_authorized_repos(self, installation_id: str) -> List[GitHubRepositoryModel]:
        print(f"📦 [GitHub Extractor] Fetching repositories for installation {installation_id}...")
        try:
            # GitHub endpoint for app installation repos
            raw_data = await self.client.get(f"user/installations/{installation_id}/repositories")
            repos_data = raw_data.get("repositories", [])
            
            repos = []
            for item in repos_data:
                repos.append(GitHubRepositoryModel(**item))
                    
            print(f"   ✅ Extracted {len(repos)} repositories.")
            return repos
            
        except Exception as e:
            print(f"🚨 [GitHub Extractor] Failed to fetch repositories: {e}")
            return []