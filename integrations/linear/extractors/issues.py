from typing import List
from datetime import datetime
from integrations.linear.models.issue import (
    LinearIssueModel, LinearTeamModel, LinearStateModel
)

class LinearIssueExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_recent_issues(self, limit: int = 50) -> List[LinearIssueModel]:
        print(f"🎯 [Linear Extractor] Fetching recent modern product issues via GraphQL...")
        
        query = """
        query GetRecentIssues($first: Int!) {
          issues(first: $first, orderBy: updatedAt) {
            nodes {
              id
              title
              description
              priority
              url
              createdAt
              updatedAt
              team { id name key }
              state { id name type }
              assignee { name }
            }
          }
        }
        """
        
        try:
            raw_data = await self.client.execute_query(query, variables={"first": limit})
            issue_nodes = raw_data.get("issues", {}).get("nodes", [])
            
            issues = []
            for node in issue_nodes:
                assignee = node.get("assignee")
                
                issues.append(LinearIssueModel(
                    id=node["id"],
                    title=node["title"],
                    description=node.get("description") or "",
                    priority=node["priority"],
                    team=LinearTeamModel(**node["team"]),
                    state=LinearStateModel(**node["state"]),
                    assignee_name=assignee["name"] if assignee else "Unassigned",
                    created_at=datetime.fromisoformat(node["createdAt"].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(node["updatedAt"].replace('Z', '+00:00')),
                    url=node["url"]
                ))
            
            print(f"   ✅ Extracted {len(issues)} Linear Issues.")
            return issues
            
        except Exception as e:
            print(f"🚨 [Linear Extractor] Failed to fetch issues: {e}")
            return []