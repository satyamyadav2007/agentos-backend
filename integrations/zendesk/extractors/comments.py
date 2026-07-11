from typing import List
from integrations.zendesk.models.comment import ZendeskCommentModel

class ZendeskCommentExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_ticket_comments(self, ticket_id: int) -> List[ZendeskCommentModel]:
        print(f"💬 [Zendesk Extractor] Reading conversation for Ticket #{ticket_id}...")
        try:
            raw_data = await self.client.get(f"tickets/{ticket_id}/comments")
            comments = [ZendeskCommentModel(**item) for item in raw_data.get("comments", [])]
            print(f"   ✅ Extracted {len(comments)} comments from Ticket #{ticket_id}.")
            return comments
        except Exception as e:
            print(f"🚨 [Zendesk Extractor] Failed to fetch comments for ticket {ticket_id}: {e}")
            return []