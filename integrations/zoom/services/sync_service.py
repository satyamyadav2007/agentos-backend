from typing import Dict, Any, List
from integrations.zoom.extractors.meetings import ZoomMeetingExtractor
from integrations.zoom.normalizer import ZoomNormalizer

class ZoomSyncService:
    """Orchestrates extraction of Spoken Customer Feedback (Transcripts)."""
    
    def __init__(self, client):
        self.client = client
        self.meeting_extractor = ZoomMeetingExtractor(client)
        
    async def run_full_sync(self) -> List[Dict[str, Any]]:
        print("\n🚀 [Zoom Sync] Starting Customer Meeting Intelligence Sync...")
        
        all_universal_events = []
        
        # 1. Fetch Transcripts for recent meetings
        meeting_models = await self.meeting_extractor.fetch_recent_meetings_with_transcripts(days=3)
        
        # 2. Normalize to Universal Format
        for meeting in meeting_models:
            normalized = ZoomNormalizer.normalize_meeting(meeting)
            all_universal_events.append(normalized)
            
        print(f"🧠 [AgentOS Brain] Normalized {len(all_universal_events)} Spoken Conversations for AI Processing!")
        return all_universal_events