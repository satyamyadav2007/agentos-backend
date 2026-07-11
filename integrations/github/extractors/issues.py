# File: integrations/github/extractors/issues.py

import requests
from typing import List, Dict, Any
from integrations.github.models.issues import GitHubIssueModel

class GitHubIssuesExtractor:
    def __init__(self, token: str):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def fetch_issues(self, repo_full_name: str) -> List[Dict[str, Any]]:
        """Fetches all real issues (excluding PRs) for a specific repository."""
        print(f"\n🐛 [GitHub Extractor] Scanning issues for {repo_full_name}...")
        
        # GitHub API url (state=all means fetch both open and closed issues)
        url = f"https://api.github.com/repos/{repo_full_name}/issues?state=all&per_page=100"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"🚨 [GitHub Extractor] Failed to fetch issues: {response.text}")
            return []
            
        raw_issues = response.json()
        clean_issues = []
        
        for issue in raw_issues:
            # ⚡ CRITICAL FIX: GitHub API treats Pull Requests as issues. 
            # We must skip them because we will build a separate PR extractor.
            if "pull_request" in issue:
                continue
                
            clean_issue = {
                "id": str(issue["id"]),
                "number": issue["number"],
                "title": issue["title"],
                "body": issue["body"],
                "state": issue["state"], # open or closed
                "author": issue["user"]["login"] if issue.get("user") else "Unknown",
                "labels": [label["name"] for label in issue.get("labels", [])],
                "created_at": issue["created_at"],
                "closed_at": issue["closed_at"]
            }
            clean_issues.append(clean_issue)
            
        print(f"   ✅ Successfully extracted {len(clean_issues)} issues from {repo_full_name}")
        return clean_issues