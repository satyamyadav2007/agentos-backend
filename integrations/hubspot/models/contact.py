from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class HubSpotContactModel(BaseModel):
    id: str
    firstname: Optional[str] = ""
    lastname: Optional[str] = ""
    email: Optional[str] = None
    lifecyclestage: Optional[str] = "lead"
    createdate: datetime
    lastmodifieddate: datetime

    @property
    def full_name(self) -> str:
        return f"{self.firstname} {self.lastname}".strip() or "Unknown Contact"

    @classmethod
    def from_hubspot_response(cls, data: Dict[str, Any]):
        props = data.get("properties", {})
        return cls(
            id=data.get("id"),
            firstname=props.get("firstname"),
            lastname=props.get("lastname"),
            email=props.get("email"),
            lifecyclestage=props.get("lifecyclestage"),
            createdate=props.get("createdate"),
            lastmodifieddate=props.get("lastmodifieddate")
        )