from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SalesforceOpportunityModel(BaseModel):
    id: str
    account_id: str
    name: str
    stage_name: str
    amount: Optional[float] = 0.0
    probability: Optional[float] = 0.0
    close_date: datetime
    is_closed: bool
    is_won: bool
    owner_id: str

    @property
    def is_at_risk(self) -> bool:
        """Simple heuristic: High value but low probability near close date."""
        return not self.is_closed and self.amount > 50000 and self.probability < 50.0