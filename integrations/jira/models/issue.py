from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class JiraIssueMetadata(BaseModel):
    """Holds Jira-specific metadata that the AI might need for deep context."""
    jira_id: str
    key: str
    status: str
    issue_type: str
    project_key: str

class JiraIssue(BaseModel):
    """
    The standardized issue format. 
    This acts as a strict contract between the Extractor and the Normalizer.
    """
    id: str
    key: str
    entity_type: str = Field(..., description="epic, story, bug, task")
    title: str
    description: str = "No description provided."
    status: str
    priority: str = "Medium"
    assignee: str = "Unassigned"
    created_at: datetime
    metadata: JiraIssueMetadata
    
    class Config:
        extra = "ignore"