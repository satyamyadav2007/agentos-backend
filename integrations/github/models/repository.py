from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .issue import GitHubUser  # Using the user model we created earlier

class GitHubRepositoryModel(BaseModel):
    id: int
    name: str
    full_name: str
    private: bool
    description: Optional[str] = ""
    html_url: str
    language: Optional[str] = None
    stargazers_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0
    owner: GitHubUser
    created_at: datetime
    updated_at: datetime
    pushed_at: Optional[datetime] = None
    default_branch: str = "main"

    @property
    def is_active(self) -> bool:
        """Helper to determine if the repo is actively maintained."""
        return not self.archived if hasattr(self, 'archived') else True