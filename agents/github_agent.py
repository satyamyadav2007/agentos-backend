import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

class EnterpriseGitHubAgent:
    def __init__(self):
        print("🐙 [GitHub Agent] Initializing Enterprise Git-Graph Engine...")
        token = os.getenv("GITHUB_TOKEN")
        self.g = Github(token) if token else Github() # Fallback to public if no token

    def extract_issue_context(self, repo_name: str, issue_number: int):
        print(f"      ↳ Fetching deep context for {repo_name}#{issue_number}...")
        
        try:
            repo = self.g.get_repo(repo_name)
            issue = repo.get_issue(number=issue_number)
            
            # 1. Base Issue & Author
            context = {
                "id": f"GH-{issue.number}",
                "title": issue.title,
                "body": issue.body or "",
                "state": issue.state,
                "author": issue.user.login,
                "labels": [label.name for label in issue.labels],
            }
            
            # 2. Comments (To understand the discussion/frustration)
            comments = issue.get_comments()
            context["comments"] = [
                {"author": c.user.login, "body": c.body} 
                for c in comments
            ][:3]  # Taking top 3 to save LLM tokens
            
            # 3. Linked PRs & Commits (Simulated for speed in MVP, but architecture is ready)
            # In production, we use GitHub GraphQL API to find exact linked PRs.
            # For this MVP push, we fetch the latest PR and Commit from the repo as context.
            pulls = repo.get_pulls(state='open', sort='created', direction='desc')
            if pulls.totalCount > 0:
                latest_pr = pulls[0]
                context["latest_pr"] = {
                    "number": latest_pr.number,
                    "title": latest_pr.title,
                    "author": latest_pr.user.login,
                    "reviews": latest_pr.get_reviews().totalCount
                }
                
            commits = repo.get_commits()
            if commits.totalCount > 0:
                latest_commit = commits[0]
                context["recent_commit"] = {
                    "sha": latest_commit.sha[:7],
                    "message": latest_commit.commit.message.split('\n')[0],
                    "author": latest_commit.author.login if latest_commit.author else "Unknown"
                }

            print(f"✅ [GitHub Agent] Context enriched with PRs, Commits, and Labels.")
            return context

        except Exception as e:
            print(f"🚨 [GitHub Agent Error] Failed to fetch deep context: {str(e)[:100]}")
            return None

# Global Instance
github_agent = EnterpriseGitHubAgent()