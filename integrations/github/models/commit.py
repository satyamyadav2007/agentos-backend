from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class CommitAuthor(BaseModel):
    name: str
    email: str
    date: datetime

class InnerCommit(BaseModel):
    author: CommitAuthor
    committer: CommitAuthor
    message: str
    comment_count: int

class GitHubCommitModel(BaseModel):
    sha: str
    node_id: str
    commit: InnerCommit
    url: str
    html_url: str
    # 'author' can be None if the user hasn't linked their local git email to a GitHub account
    author: Optional[Dict[str, Any]] = None 
    committer: Optional[Dict[str, Any]] = None
    parents: List[Dict[str, Any]] = []

    @property
    def commit_message_summary(self) -> str:
        """Returns the first line of the commit message for clean logs."""
        return self.commit.message.split("\n")[0] if self.commit.message else "No message"