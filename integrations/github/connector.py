from typing import Dict, Any, Optional
from integrations.base import BaseConnector
from .oauth import GitHubAuthManager
from github import Github # Make sure PyGithub is installed (pip install PyGithub)

class GitHubConnector(BaseConnector):
    """Orchestrates the GitHub integration with a strict Universal Return Contract."""
    
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.auth_manager = GitHubAuthManager()
        self.access_token = None
        self.installation_id = None

    # ⚡ ADD THESE 4 METHODS TO SATISFY BaseConnector ⚡
    async def connect(self, *args, **kwargs): pass
    async def disconnect(self, *args, **kwargs): pass
    async def normalize(self, data, *args, **kwargs): return data
    async def webhook(self, request, *args, **kwargs): pass

    async def sync(self, user_email: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetches real data from GitHub and returns it strictly matching the AgentOS Contract.
        """
        if not self.access_token:
            return {
                "provider": "github",
                "metrics": {"repositories": 0, "issues": 0, "pull_requests": 0, "commits": 0},
                "records": [],
                "cursor": None,
                "sync_status": "failed",
                "message": "Access token is missing. Please authenticate."
            }

        try:
            print("🐙 [GitHub Connector] Initializing real API extraction...")
            gh = Github(self.access_token)
            user = gh.get_user()
            
            records = []
            repo_count = 0
            issue_count = 0
            pr_count = 0
            
            # ⚡ SMART REPO FETCHING (Handles both OAuth Users & GitHub App Integrations)
            repos_to_sync = []
            try:
                # Pehle normal tareeqa try karega
                repos_to_sync = list(user.get_repos(sort="updated", direction="desc")[:5])
            except Exception as e:
                if "403" in str(e) or "integration" in str(e).lower():
                    print("🔄 [GitHub Connector] Switched to GitHub App Installation mode...")
                    # Agar 403 aaya (Resource not accessible by integration), toh App Installations ke through repos nikalega
                    installations = user.get_installations()
                    if installations.totalCount > 0:
                        repos_to_sync = list(installations[0].get_repos()[:5])
                    else:
                        raise Exception("No GitHub App installations found for this user.")
                else:
                    raise e
            
            # Ab repos mil gaye hain, toh issues aur PRs nikalte hain
            for repo in repos_to_sync:
                repo_count += 1
                
                # Fetching recent open issues (GitHub API treats PRs as issues too)
                open_items = repo.get_issues(state='open', sort='updated')[:15]
                
                for item in open_items:
                    is_pr = item.pull_request is not None
                    if is_pr:
                        pr_count += 1
                        record_type = "pull_request"
                    else:
                        issue_count += 1
                        record_type = "issue"
                        
                    records.append({
                        "id": f"gh-{item.id}",
                        "type": record_type,
                        "source": "github",
                        "title": item.title,
                        "description": item.body[:1000] if item.body else "No description provided.",
                        "url": item.html_url,
                        "state": item.state,
                        "created_at": item.created_at.isoformat() if item.created_at else None,
                        "metadata": {
                            "repository": repo.name,
                            "author": item.user.login if item.user else "Unknown"
                        }
                    })

            print(f"✅ [GitHub Connector] Extracted {issue_count} issues & {pr_count} PRs from {repo_count} repos.")

            return {
                "provider": "github",
                "metrics": {
                    "repositories": repo_count,
                    "issues": issue_count,
                    "pull_requests": pr_count,
                    "commits": 0 
                },
                "records": records,
                "cursor": "initial_sync_complete",
                "sync_status": "completed"
            }

        except Exception as e:
            print(f"🚨 [GitHub Extractor Error]: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "provider": "github",
                "metrics": {"repositories": 0, "issues": 0, "pull_requests": 0, "commits": 0},
                "records": [],
                "cursor": None,
                "sync_status": "error",
                "message": str(e)
            }