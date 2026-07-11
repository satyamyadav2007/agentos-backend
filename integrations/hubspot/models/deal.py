from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class HubSpotDealModel(BaseModel):
    id: str
    dealname: str
    amount: Optional[float] = 0.0
    dealstage: str
    pipeline: str
    closedate: Optional[datetime] = None
    createdate: datetime
    hubspot_owner_id: Optional[str] = None
    
    # Custom AI fields that will be enriched later
    win_probability: Optional[float] = None
    risk_level: Optional[str] = "Low"

    @classmethod
    def from_hubspot_response(cls, data: Dict[str, Any]):
        """Helper to flatten HubSpot's nested 'properties' structure."""
        props = data.get("properties", {})
        return cls(
            id=data.get("id"),
            dealname=props.get("dealname", "Unknown Deal"),
            amount=float(props.get("amount", 0.0)) if props.get("amount") else 0.0,
            dealstage=props.get("dealstage", "unknown"),
            pipeline=props.get("pipeline", "default"),
            closedate=props.get("closedate"),
            createdate=props.get("createdate"),
            hubspot_owner_id=props.get("hubspot_owner_id")
        )