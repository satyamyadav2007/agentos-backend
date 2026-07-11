import httpx
from datetime import datetime
from typing import List, Dict, Any
from .base import BaseEmailProvider
from ..models.thread import EmailThreadModel, EmailMessageModel

class GmailProvider(BaseEmailProvider):
    """Gmail implementation of the unified Email engine."""
    
    def __init__(self, access_token: str):
        super().__init__(access_token)
        self.base_url = "https://gmail.googleapis.com/gmail/v1/users/me"
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    async def fetch_recent_threads(self, limit: int = 20) -> List[EmailThreadModel]:
        print(f"📧 [Gmail Provider] Fetching latest enterprise conversations...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. Get Thread IDs
            list_url = f"{self.base_url}/threads"
            list_res = await client.get(list_url, headers=self.headers, params={"maxResults": limit})
            list_res.raise_for_status()
            thread_ids = [t['id'] for t in list_res.json().get('threads', [])]
            
            standardized_threads = []
            
            # 2. Fetch details for each thread
            for t_id in thread_ids:
                detail_url = f"{self.base_url}/threads/{t_id}"
                detail_res = await client.get(detail_url, headers=self.headers)
                t_data = detail_res.json()
                
                messages = []
                for msg in t_data.get("messages", []):
                    headers = {h['name'].lower(): h['value'] for h in msg.get("payload", {}).get("headers", [])}
                    
                    # Very simplified snippet extraction (real implementation decodes base64 body)
                    messages.append(EmailMessageModel(
                        id=msg['id'],
                        thread_id=t_id,
                        sender=headers.get("from", "unknown"),
                        recipients=headers.get("to", "").split(","),
                        cc=headers.get("cc", "").split(","),
                        subject=headers.get("subject", "No Subject"),
                        body_text=msg.get("snippet", ""),
                        timestamp=datetime.fromtimestamp(int(msg.get("internalDate", 0)) / 1000.0),
                    ))
                
                standardized_threads.append(EmailThreadModel(
                    id=t_id,
                    provider="gmail",
                    messages=messages,
                    labels_or_categories=[]
                ))
                
            print(f"   ✅ Standardized {len(standardized_threads)} Gmail threads.")
            return standardized_threads