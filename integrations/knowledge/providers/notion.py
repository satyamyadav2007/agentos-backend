import httpx
from datetime import datetime
from typing import List
from ..models.document import KnowledgeDocumentModel

class NotionProvider:
    """Notion API Provider for Enterprise Knowledge."""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        self.timeout = httpx.Timeout(30.0)

    async def fetch_recent_pages(self, limit: int = 20) -> List[KnowledgeDocumentModel]:
        print(f"📓 [Notion Provider] Fetching latest PRDs, Docs, and Meeting Notes...")
        
        try:
            # Note: Notion API requires fetching pages, then fetching blocks for content.
            # This is the architectural representation of that workflow.
            
            # Mocking the structured extraction for architecture demonstration
            mock_notion_data = [
                {
                    "id": "notion_auth_123",
                    "title": "Authentication V2 PRD",
                    "content": "We are migrating to OAuth 2.0. Acceptance Criteria: 1. SSO must work for Enterprise. 2. JWT tokens must expire in 1hr.",
                    "author": "satyam@agentos.com",
                    "url": "https://notion.so/auth-v2-prd",
                    "updated_at": datetime.utcnow()
                }
            ]
            
            docs = []
            for entry in mock_notion_data:
                docs.append(KnowledgeDocumentModel(
                    id=entry["id"],
                    provider="notion",
                    title=entry["title"],
                    content=entry["content"],
                    author=entry["author"],
                    url=entry["url"],
                    created_at=entry["updated_at"],
                    updated_at=entry["updated_at"]
                ))
            
            print(f"   ✅ Extracted {len(docs)} Notion Knowledge Documents.")
            return docs
                
        except Exception as e:
            print(f"🚨 [Notion Provider] Failed: {e}")
            return []