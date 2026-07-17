from pydantic import BaseModel, Field
from typing import Optional

class JiraProject(BaseModel):
    """Pydantic model for validating Jira Project data."""
    id: str
    key: str = Field(..., description="The unique project identifier (e.g., ENG, PROD)")
    name: str
    project_type: Optional[str] = Field(default="software", alias="projectTypeKey")
    
    class Config:
        populate_by_name = True
        extra = "ignore" # Ignores hundreds of useless Jira fields