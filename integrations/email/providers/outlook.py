import httpx
from datetime import datetime
from typing import List, Dict, Any
from .base import BaseEmailProvider
from ..models.thread import EmailThreadModel, EmailMessageModel

class OutlookProvider(BaseEmailProvider):
    """Outlook (Microsoft Graph API) implementation of the unified Email engine."""
    
    def __init__(self, access_token: str):
        super().__init__(access_token)
        # Microsoft Graph API endpoint for the authenticated user's emails
        self.base_url = "https://graph.microsoft.com/v1.0/me"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

    async def fetch_recent_threads(self, limit: int = 20) -> List[EmailThreadModel]:
        print(f"📧 [Outlook Provider] Fetching latest enterprise conversations via MS Graph...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. Fetch recent messages
            # Using $top to limit and $select for payload reduction to keep it fast
            url = f"{self.base_url}/messages"
            params = {
                "$top": limit * 2,  # Fetch extra to effectively group into threads
                "$select": "id,conversationId,sender,toRecipients,ccRecipients,subject,bodyPreview,receivedDateTime,hasAttachments",
                "$orderby": "receivedDateTime desc"
            }
            
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            raw_messages = response.json().get('value', [])
            
            # 2. Group messages by conversationId to match our AgentOS Thread Model
            grouped_threads: Dict[str, List[EmailMessageModel]] = {}
            
            for msg in raw_messages:
                conv_id = msg.get("conversationId", "unknown_thread")
                
                # Safely extract email addresses from Microsoft's nested structure
                sender_email = msg.get("sender", {}).get("emailAddress", {}).get("address", "unknown")
                recipients = [r.get("emailAddress", {}).get("address", "") for r in msg.get("toRecipients", [])]
                cc_recipients = [r.get("emailAddress", {}).get("address", "") for r in msg.get("ccRecipients", [])]
                
                email_msg = EmailMessageModel(
                    id=msg.get("id"),
                    thread_id=conv_id,
                    sender=sender_email,
                    recipients=recipients,
                    cc=cc_recipients,
                    subject=msg.get("subject", "No Subject"),
                    body_text=msg.get("bodyPreview", ""),
                    timestamp=datetime.fromisoformat(msg.get("receivedDateTime", "").replace('Z', '+00:00')),
                    has_attachments=msg.get("hasAttachments", False)
                )
                
                if conv_id not in grouped_threads:
                    grouped_threads[conv_id] = []
                grouped_threads[conv_id].append(email_msg)
            
            # 3. Convert grouped dict into our unified list of Thread Models
            standardized_threads = []
            for t_id, messages in list(grouped_threads.items())[:limit]:
                standardized_threads.append(EmailThreadModel(
                    id=t_id,
                    provider="outlook",
                    messages=messages,
                    labels_or_categories=[] # Can fetch categories in a separate Graph API call if needed
                ))
                
            print(f"   ✅ Standardized {len(standardized_threads)} Outlook threads.")
            return standardized_threads