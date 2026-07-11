from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from .issue import GitHubUser

class PRBranch(BaseModel):
    label: str
    ref: str
    sha: str

class GitHubPullRequestModel(BaseModel):
    id: int
    number: int
    title: str
    state: str  # 'open', 'closed', etc.
    locked: bool
    title: str
    body: Optional[str] = ""
    user: GitHubUser
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None
    merge_commit_sha: Optional[str] = None
    head: PRBranch
    base: PRBranch
    draft: bool = False
    
    # These fields are usually available when fetching a specific PR
    merged: Optional[bool] = None
    additions: Optional[int] = 0
    deletions: Optional[int] = 0
    changed_files: Optional[int] = 0

    @property
    def is_merged(self) -> bool:
        return self.merged_at is not None