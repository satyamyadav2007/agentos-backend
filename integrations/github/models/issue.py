from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class GitHubUser(BaseModel):
    login: str
    id: int
    type: str

class GitHubIssueModel(BaseModel):
    id: int
    number: int
    title: str
    state: str
    body: Optional[str] = ""
    user: GitHubUser
    labels: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime
    pull_request: Optional[Dict[str, Any]] = None
    
    @property
    def is_pr(self) -> bool:
        return self.pull_request is not None