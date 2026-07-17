from typing import List, Dict, Any


class GitHubDiscovery:
    """
    Discovers all repositories that the GitHub App Installation
    has access to.

    Uses the shared async GitHub client so the architecture matches
    all other extractors (Issues, PRs, Commits, Actions).
    """

    def __init__(self, client):
        self.client = client

    async def fetch_authorized_repos(
        self,
        installation_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Returns all repositories accessible to the installation.

        installation_id is kept only for API compatibility with
        GitHubSyncService. It is not required because the
        installation token already identifies the installation.
        """

        print("🔍 [GitHub Discovery] Scanning authorized repositories...")

        try:
            data = await self.client.get(
                "installation/repositories"
            )

            repositories = []

            for repo in data.get("repositories", []):
                repositories.append({
                    "id": repo["id"],
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "private": repo.get("private", False),
                    "default_branch": repo.get("default_branch"),
                    "language": repo.get("language"),
                    "open_issues_count": repo.get("open_issues_count", 0),
                })

                print(
                    f"   📦 Found Repo: {repo['full_name']} "
                    f"(Language: {repo.get('language')})"
                )

            print(
                f"✅ [GitHub Discovery] Found {len(repositories)} repositories."
            )

            return repositories

        except Exception as e:
            print(f"🚨 [GitHub Discovery Error]: {e}")
            return []