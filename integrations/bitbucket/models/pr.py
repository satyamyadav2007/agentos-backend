from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class BitbucketUserModel(BaseModel):
    account_id: str
    display_name: str
    nickname: Optional[str] = None

class BitbucketRepositoryModel(BaseModel):
    uuid: str
    name: str
    full_name: str # format: workspace/repo_slug

class BitbucketPRModel(BaseModel):
    id: int
    title: str
    description: Optional[str] = ""
    state: str  # MERGED, SUPERSEDED, OPEN, DECLINED
    author: BitbucketUserModel
    repository: BitbucketRepositoryModel
    created_on: datetime
    updated_on: datetime
    merge_commit: Optional[Dict[str, str]] = None
    links: Dict[str, Any] = {}

    @property
    def web_url(self) -> str:
        return self.links.get("html", {}).get("href", "")

    @property
    def is_risky(self) -> bool:
        """AI Heuristic: Detects high-risk PRs based on keywords."""
        keywords = ["refactor", "hotfix", "critical", "payment", "auth", "security"]
        title_desc = f"{self.title} {self.description}".lower()
        return any(k in title_desc for k in keywords)