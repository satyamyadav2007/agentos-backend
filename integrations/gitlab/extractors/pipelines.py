from typing import List
from datetime import datetime
from integrations.gitlab.models.devsecops import GitLabMergeRequestModel, GitLabPipelineModel

class GitLabDevSecOpsExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_recent_pipelines(self, project_id: str, limit: int = 20) -> List[GitLabPipelineModel]:
        print(f"⚙️ [GitLab Extractor] Fetching CI/CD Pipelines for Project {project_id}...")
        try:
            raw_data = await self.client.get(f"projects/{project_id}/pipelines", params={"per_page": limit})
            pipelines_data = raw_data.get("data", [])
            
            pipelines = []
            for p in pipelines_data:
                pipelines.append(GitLabPipelineModel(
                    id=p.get("id"),
                    project_id=p.get("project_id"),
                    status=p.get("status"),
                    ref=p.get("ref"),
                    web_url=p.get("web_url"),
                    created_at=datetime.fromisoformat(p.get("created_at", "").replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(p.get("updated_at", "").replace('Z', '+00:00')),
                ))
            print(f"   ✅ Extracted {len(pipelines)} CI/CD Pipelines.")
            return pipelines
        except Exception as e:
            print(f"🚨 [GitLab Extractor] Failed to fetch pipelines: {e}")
            return []

    async def fetch_merge_requests(self, project_id: str, limit: int = 20) -> List[GitLabMergeRequestModel]:
        # Similar logic to fetch /projects/{project_id}/merge_requests
        pass