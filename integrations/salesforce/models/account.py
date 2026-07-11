from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class SalesforceAccountModel(BaseModel):
    id: str
    name: str
    industry: Optional[str] = None
    annual_revenue: Optional[float] = 0.0
    type: Optional[str] = "Customer"
    customer_tier: Optional[str] = "Standard" # Derived from custom fields
    health_score: Optional[str] = "Unknown"   # Derived from custom fields
    renewal_date: Optional[datetime] = None
    created_date: datetime
    last_modified_date: datetime

    @property
    def is_enterprise(self) -> bool:
        return self.annual_revenue and self.annual_revenue > 1000000.0 or self.customer_tier == "Enterprise"