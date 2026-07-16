from typing import List
from integrations.github.models.repository import GitHubRepositoryModel

class GitHubRepositoryExtractor:
    """Handles data collection for GitHub Repositories."""
    
    def __init__(self, client):
        self.client = client

    async def fetch_authorized_repos(self) -> List[GitHubRepositoryModel]:
        # Ab installation_id pass karne ki zaroorat nahi, token khud batayega wo kiska hai
        print(f"📦 [GitHub Extractor] Fetching repositories for active installation...")
        try:
            # ⚡ CORRECT ENDPOINT FOR INSTALLATION TOKENS
            raw_data = await self.client.get("installation/repositories")
            repos_data = raw_data.get("repositories", [])
            
            repos = []
            for item in repos_data:
                repos.append(GitHubRepositoryModel(**item))
                    
            print(f"   ✅ Extracted {len(repos)} repositories.")
            return repos
            
        except Exception as e:
            print(f"🚨 [GitHub Extractor] Failed to fetch repositories: {e}")
            return []