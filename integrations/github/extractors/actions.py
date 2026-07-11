from typing import List, Dict, Any

class GitHubActionsExtractor:
    """Handles data collection for GitHub Actions (CI/CD Workflow Runs)."""
    
    def __init__(self, client):
        self.client = client

    async def fetch_recent_workflow_runs(self, repo_full_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        print(f"⚙️ [GitHub Extractor] Fetching CI/CD workflow runs for {repo_full_name}...")
        try:
            raw_data = await self.client.get(
                f"repos/{repo_full_name}/actions/runs",
                params={"per_page": limit}
            )
            
            workflow_runs = raw_data.get("workflow_runs", [])
            print(f"   ✅ Extracted {len(workflow_runs)} workflow runs from {repo_full_name}")
            return workflow_runs
            
        except Exception as e:
            print(f"🚨 [GitHub Extractor] Failed to fetch workflow runs for {repo_full_name}: {e}")
            return []