from abc import ABC, abstractmethod
from typing import List
from integrations.email.models.thread import EmailThreadModel

class BaseEmailProvider(ABC):
    """Abstract Base Class for Email Providers (Gmail, Outlook)."""
    
    def __init__(self, access_token: str):
        self.access_token = access_token

    @abstractmethod
    async def fetch_recent_threads(self, limit: int = 20) -> List[EmailThreadModel]:
        """Module 4: Thread Intelligence - Fetch recent conversational threads."""
        pass