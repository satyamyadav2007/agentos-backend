from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class LinearTeamModel(BaseModel):
    id: str
    name: str
    key: str

class LinearStateModel(BaseModel):
    id: str
    name: str
    type: str # backlog, unstarted, started, completed, canceled

class LinearIssueModel(BaseModel):
    id: str
    title: str
    description: Optional[str] = ""
    priority: int # 0 = No priority, 1 = Urgent, 2 = High, 3 = Normal, 4 = Low
    team: LinearTeamModel
    state: LinearStateModel
    assignee_name: Optional[str] = "Unassigned"
    created_at: datetime
    updated_at: datetime
    url: str

    @property
    def is_blocked(self) -> bool:
        """AI Heuristic: Detects if the issue state implies it's blocked."""
        return "block" in self.state.name.lower()

    @property
    def severity_label(self) -> str:
        if self.priority == 1: return "Critical"
        if self.priority == 2: return "High"
        if self.priority == 3: return "Medium"
        return "Low"