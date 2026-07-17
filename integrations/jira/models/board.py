 from pydantic import BaseModel, Field
from typing import Optional

class JiraBoard(BaseModel):
    """Pydantic model for validating Jira Agile Boards."""
    id: int
    name: str
    type: str = Field(..., description="E.g., scrum or kanban")
    project_key: Optional[str] = None
    
    class Config:
        extra = "ignore"