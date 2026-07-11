from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class EmailMessageModel(BaseModel):
    id: str
    thread_id: str
    sender: str
    recipients: List[str] = []
    cc: List[str] = []
    subject: str
    body_text: str
    timestamp: datetime
    has_attachments: bool = False

class EmailThreadModel(BaseModel):
    id: str
    provider: str  # 'gmail' or 'outlook'
    messages: List[EmailMessageModel] = []
    labels_or_categories: List[str] = []
    
    @property
    def latest_message(self) -> Optional[EmailMessageModel]:
        if not self.messages:
            return None
        return sorted(self.messages, key=lambda x: x.timestamp, reverse=True)[0]
        
    @property
    def is_executive_escalation(self) -> bool:
        """AI Heuristic: Detects if C-level is involved in the thread."""
        exec_keywords = ['ceo@', 'cto@', 'vp@', 'founder@']
        all_participants = []
        for msg in self.messages:
            all_participants.extend([msg.sender] + msg.recipients + msg.cc)
            
        for participant in all_participants:
            if any(keyword in participant.lower() for keyword in exec_keywords):
                return True
        return False