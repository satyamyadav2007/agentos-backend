import httpx
from typing import Dict, Any, Optional

class GoogleWorkspaceClient:
    """Centralized HTTP Client for Google Calendar & Drive APIs."""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.calendar_api = "https://www.googleapis.com/calendar/v3"
        self.drive_api = "https://www.googleapis.com/drive/v3"
        self.timeout = httpx.Timeout(30.0)
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

    async def get_calendar_events(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.calendar_api}/calendars/primary/events"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

    async def get_drive_file_text(self, file_id: str) -> str:
        """Fetches the actual text content of a Google Meet transcript from Drive."""
        url = f"{self.drive_api}/files/{file_id}/export?mimeType=text/plain"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.text
            return ""