import requests
from typing import Dict, Any, List

class GitHubDiscovery:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def fetch_repositories(self) -> List[Dict[str, Any]]:
        """Fetches all repositories this GitHub App installation has access to."""
        print("🔍 [GitHub Discovery] Scanning for authorized repositories...")
        url = "https://api.github.com/installation/repositories"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"🚨 [GitHub Discovery] Failed to fetch repos: {response.text}")
            return []
            
        data = response.json()
        raw_repos = data.get("repositories", [])
        
        clean_repos = []
        for repo in raw_repos:
            repo_info = {
                "id": repo["id"],
                "name": repo["name"],
                "full_name": repo["full_name"],
                "private": repo["private"],
                "default_branch": repo["default_branch"],
                "language": repo["language"],
                "open_issues_count": repo["open_issues_count"]
            }
            clean_repos.append(repo_info)
            print(f"   📦 Found Repo: {repo['full_name']} (Language: {repo['language']})")
            
        return clean_repos