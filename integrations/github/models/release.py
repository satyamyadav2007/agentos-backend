from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .issue import GitHubUser

class GitHubReleaseModel(BaseModel):
    id: int
    tag_name: str
    target_commitish: str  # Usually 'main' or 'master'
    name: Optional[str] = ""
    body: Optional[str] = ""
    draft: bool
    prerelease: bool
    created_at: datetime
    published_at: Optional[datetime] = None
    author: GitHubUser
    tarball_url: Optional[str] = None
    zipball_url: Optional[str] = None
    html_url: str

    @property
    def is_production(self) -> bool:
        """If it's not a draft and not a prerelease, it's a production release."""
        return not self.draft and not self.prerelease