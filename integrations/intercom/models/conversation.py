from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class IntercomConversationModel(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    source: Dict[str, Any]  # Contains the first message/snippet
    contacts: Dict[str, Any] # Identifies the customer
    state: str  # 'open', 'closed', 'snoozed'
    read: bool
    tags: Dict[str, Any] = {}
    custom_attributes: Dict[str, Any] = {}
    
    # AI Enriched Fields
    detected_intent: Optional[str] = None
    sentiment: Optional[str] = "Neutral"

    @property
    def snippet(self) -> str:
        """Helper to quickly grab the chat's context."""
        return self.source.get('body', 'No text body')
        
    @property
    def primary_contact_id(self) -> str:
        contact_list = self.contacts.get('contacts', [])
        return contact_list[0].get('id', 'Unknown') if contact_list else 'Unknown'