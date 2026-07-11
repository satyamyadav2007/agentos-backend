from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ZoomTranscriptModel(BaseModel):
    id: str
    meeting_id: str
    text_content: str  # The full or chunked conversation
    speaker_diarization: bool = False # Did we identify who said what?

class ZoomMeetingModel(BaseModel):
    id: str
    uuid: str
    host_id: str
    topic: str
    start_time: datetime
    duration_minutes: int
    total_participants: int
    
    # Linked Transcript
    transcript: Optional[ZoomTranscriptModel] = None
    
    # AI Enriched Fields
    detected_pain_points: List[str] = []
    churn_risk_signal: bool = False

    @property
    def is_high_value(self) -> bool:
        """AI Heuristic: Long meetings with many participants usually hold strategic value."""
        return self.duration_minutes > 30 and self.total_participants >= 3