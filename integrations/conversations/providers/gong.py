import httpx
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .base import BaseConversationProvider
from ..models.call import ConversationCallModel, SpeakerModel

class GongProvider(BaseConversationProvider):
    """Gong.io implementation of the Conversation Intelligence engine."""
    
    def __init__(self, api_key: str, api_secret: str):
        super().__init__(api_key, api_secret)
        self.base_url = "https://api.gong.io/v2"
        
        # Gong uses Basic Auth
        auth_string = f"{self.api_key}:{self.api_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        self.headers = {"Authorization": f"Basic {encoded_auth}"}

    async def fetch_recent_calls(self, limit: int = 50) -> List[ConversationCallModel]:
        print(f"🎙️ [Gong Provider] Fetching latest sales and renewal calls...")
        
        url = f"{self.base_url}/calls/extensive"
        from_date = (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z"
        
        params = {
            "fromDateTime": from_date,
            "contentSelector": {
                "context": "Extended",
                "exposedFields": {"parties": True, "content": True}
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Note: Gong extensive API is a POST request even for fetching data
            response = await client.post(url, headers=self.headers, json=params)
            response.raise_for_status()
            raw_calls = response.json().get("calls", [])
            
            standardized_calls = []
            for call in raw_calls[:limit]:
                meta = call.get("metaData", {})
                parties = call.get("parties", [])
                
                # In production, Gong returns transcripts via a separate /calls/transcript endpoint
                # For this architecture, we map the abstract flow.
                speakers = [
                    SpeakerModel(
                        id=p.get("id", "unknown"),
                        name=p.get("name", "Unknown Speaker"),
                        role=p.get("title", "Participant")
                    ) for p in parties
                ]
                
                standardized_calls.append(ConversationCallModel(
                    id=meta.get("id"),
                    provider="gong",
                    title=meta.get("title", "Sales Call"),
                    workspace_id=meta.get("workspaceId", "default"),
                    start_time=datetime.fromisoformat(meta.get("started", "").replace('Z', '+00:00')),
                    duration_minutes=int(meta.get("duration", 0) / 60),
                    speakers=speakers,
                    transcript_text="[Transcript fetched from Gong API...]",
                    deal_id=call.get("context", {}).get("opportunityId")
                ))
                
            print(f"   ✅ Standardized {len(standardized_calls)} Gong calls.")
            return standardized_calls