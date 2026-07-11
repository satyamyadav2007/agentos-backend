from abc import ABC, abstractmethod
from typing import List, Dict, Any
from integrations.conversations.models.call import ConversationCallModel

class BaseConversationProvider(ABC):
    """Abstract Base Class for Conversation Intelligence (Gong, Fireflies, etc.)."""
    
    def __init__(self, api_key: str, api_secret: Optional[str] = None):
        self.api_key = api_key
        self.api_secret = api_secret

    @abstractmethod
    async def fetch_recent_calls(self, limit: int = 50) -> List[ConversationCallModel]:
        """Module 3: Fetch recent calls with transcripts and speakers."""
        pass