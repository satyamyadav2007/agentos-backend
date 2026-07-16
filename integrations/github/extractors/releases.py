from typing import List
from integrations.github.models.release import GitHubReleaseModel

class GitHubReleasesExtractor:
    """Handles data collection for GitHub Releases."""
    
    def __init__(self, client):
        self.client = client

    async def fetch_recent_releases(self, repo_full_name: str, limit: int = 10) -> List[GitHubReleaseModel]:
        print(f"🚀 [GitHub Extractor] Scanning releases for {repo_full_name}...")
        try:
            # Using the unified async client
            raw_data = await self.client.get(
                f"repos/{repo_full_name}/releases",
                params={"per_page": limit}
            )
            
            clean_releases = []
            for item in raw_data:
                clean_releases.append(GitHubReleaseModel(**item))
                
            print(f"   ✅ Successfully extracted {len(clean_releases)} releases from {repo_full_name}")
            return clean_releases
            
        except Exception as e:
            print(f"🚨 [GitHub Extractor] Failed to fetch releases for {repo_full_name}: {e}")
            return []