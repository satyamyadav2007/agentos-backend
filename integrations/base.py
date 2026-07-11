from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseConnector(ABC):
    """
    Enterprise Data Pipeline Interface.
    Every connector (GitHub, Jira, Slack) must implement this.
    """
    
    def __init__(self, workspace_id: str, org_id: str):
        self.workspace_id = workspace_id
        self.org_id = org_id

    @abstractmethod
    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handles OAuth flow and token storage."""
        pass

    @abstractmethod
    async def sync(self) -> Dict[str, Any]:
        """Pulls data from the source (initial or delta sync)."""
        pass

    @abstractmethod
    async def webhook(self, payload: Dict[str, Any]) -> bool:
        """Handles real-time incoming webhooks."""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Revokes tokens and cleans up."""
        pass

    @abstractmethod
    async def normalize(self, raw_data: Any) -> Any:
        """Converts vendor-specific data into AgentOS universal schema."""
        pass