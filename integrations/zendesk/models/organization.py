from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ZendeskOrganizationModel(BaseModel):
    id: int
    name: str
    domain_names: List[str] = []
    tags: List[str] = []
    organization_fields: Dict[str, Any] = {}  # CRITICAL: This is where CRM syncs ARR and Tier
    created_at: datetime
    updated_at: datetime

    @property
    def is_enterprise(self) -> bool:
        """Helper to quickly identify high-value targets based on tags or fields."""
        return "enterprise" in self.tags or self.organization_fields.get("tier") == "Tier 1"