from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class GitLabPipelineModel(BaseModel):
    id: int
    project_id: int
    status: str  # success, failed, running, pending, canceled
    ref: str     # branch name
    web_url: str
    created_at: datetime
    updated_at: datetime
    duration: Optional[int] = None
    
    @property
    def is_critical_failure(self) -> bool:
        """AI Heuristic: A failed pipeline on master/main is a critical deployment blocker."""
        return self.status == "failed" and self.ref in ["master", "main", "production"]

class GitLabMergeRequestModel(BaseModel):
    id: int
    iid: int
    project_id: int
    title: str
    description: Optional[str] = ""
    state: str  # opened, closed, merged
    author: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    web_url: str
    has_conflicts: bool = False