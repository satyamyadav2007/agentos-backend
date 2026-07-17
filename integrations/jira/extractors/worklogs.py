from typing import Dict, Any, List

class JiraWorklogsExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_issue_worklogs(self, issue_key: str) -> List[Dict[str, Any]]:
        """Fetches logged work time for a specific issue."""
        try:
            endpoint = f"rest/api/3/issue/{issue_key}/worklog"
            response = await self.client.get(endpoint)
            
            worklogs = response.get("worklogs", [])
            return worklogs
            
        except Exception as e:
            # We don't print a huge error here because many issues naturally have no worklogs
            # print(f"⚠️ [Jira Extractor] No worklogs fetched for {issue_key}: {e}")
            return []