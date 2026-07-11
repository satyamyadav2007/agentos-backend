from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class GoogleParticipantModel(BaseModel):
    email: str
    display_name: Optional[str] = None
    response_status: str  # accepted, declined, needsAction

class GoogleMeetModel(BaseModel):
    id: str
    summary: str
    description: Optional[str] = ""
    start_time: datetime
    end_time: datetime
    meet_link: str
    organizer_email: str
    participants: List[GoogleParticipantModel] = []
    
    # Linked Drive Artifacts
    recording_url: Optional[str] = None
    transcript_text: Optional[str] = None

    @property
    def is_strategic_call(self) -> bool:
        """AI Heuristic: Detects high-value meetings based on keywords and participant count."""
        keywords = ["renewal", "enterprise", "qbr", "planning", "escalation", "architecture"]
        is_important = any(k in f"{self.summary} {self.description}".lower() for k in keywords)
        return is_important or len(self.participants) >= 4