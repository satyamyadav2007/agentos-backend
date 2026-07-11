from typing import List
from datetime import datetime
from integrations.bitbucket.models.pr import (
    BitbucketPRModel, BitbucketUserModel, BitbucketRepositoryModel
)

class BitbucketPRExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_recent_prs(self, workspace: str, repo_slug: str, limit: int = 20) -> List[BitbucketPRModel]:
        print(f"🔄 [Bitbucket Extractor] Fetching PRs for {workspace}/{repo_slug}...")
        
        endpoint = f"repositories/{workspace}/{repo_slug}/pullrequests"
        # Fetching all states (OPEN, MERGED, DECLINED) to feed complete intelligence
        params = {"state": "ALL", "pagelen": limit, "sort": "-updated_on"}
        
        try:
            raw_data = await self.client.get(endpoint, params=params)
            pr_list = raw_data.get("values", [])
            
            standardized_prs = []
            for pr in pr_list:
                author_data = pr.get("author", {})
                repo_data = pr.get("destination", {}).get("repository", {})
                
                author = BitbucketUserModel(
                    account_id=author_data.get("account_id", "unknown"),
                    display_name=author_data.get("display_name", "Unknown"),
                    nickname=author_data.get("nickname")
                )
                
                repository = BitbucketRepositoryModel(
                    uuid=repo_data.get("uuid", ""),
                    name=repo_data.get("name", repo_slug),
                    full_name=repo_data.get("full_name", f"{workspace}/{repo_slug}")
                )
                
                standardized_prs.append(BitbucketPRModel(
                    id=pr.get("id"),
                    title=pr.get("title"),
                    description=pr.get("description") or "",
                    state=pr.get("state"),
                    author=author,
                    repository=repository,
                    created_on=datetime.fromisoformat(pr.get("created_on", "").replace('Z', '+00:00')),
                    updated_on=datetime.fromisoformat(pr.get("updated_on", "").replace('Z', '+00:00')),
                    merge_commit=pr.get("merge_commit"),
                    links=pr.get("links", {})
                ))
                
            print(f"   ✅ Extracted {len(standardized_prs)} Bitbucket Pull Requests.")
            return standardized_prs
            
        except Exception as e:
            print(f"🚨 [Bitbucket Extractor] Failed to fetch PRs: {e}")
            return []