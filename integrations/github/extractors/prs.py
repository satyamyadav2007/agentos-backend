import requests
from typing import List, Dict, Any

class GitHubPRExtractor:
    def __init__(self, token: str):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def fetch_prs(self, repo_full_name: str) -> List[Dict[str, Any]]:
        """Fetches Pull Requests for a specific repository."""
        print(f"🔄 [GitHub Extractor] Scanning Pull Requests for {repo_full_name}...")
        
        url = f"https://api.github.com/repos/{repo_full_name}/pulls?state=all&per_page=100"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"🚨 [GitHub Extractor] Failed to fetch PRs: {response.text}")
            return []
            
        raw_prs = response.json()
        clean_prs = []
        
        for pr in raw_prs:
            clean_pr = {
                "id": str(pr["id"]),
                "number": pr["number"],
                "title": pr["title"],
                "body": pr.get("body", ""),
                "state": pr["state"],
                "author": pr["user"]["login"] if pr.get("user") else "Unknown",
                "created_at": pr["created_at"],
                "merged_at": pr.get("merged_at"),
                "draft": pr.get("draft", False)
            }
            clean_prs.append(clean_pr)
            
        print(f"   ✅ Successfully extracted {len(clean_prs)} PRs from {repo_full_name}")
        return clean_prs