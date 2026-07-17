from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class JiraSprint(BaseModel):
    """Pydantic model for validating Jira Sprint data."""
    id: int
    name: str
    state: str = Field(..., description="active, future, or closed")
    start_date: Optional[datetime] = Field(None, alias="startDate")
    end_date: Optional[datetime] = Field(None, alias="endDate")
    goal: Optional[str] = "No sprint goal defined"
    board_id: int
    
    class Config:
        populate_by_name = True
        extra = "ignore"