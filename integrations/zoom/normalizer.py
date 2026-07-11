from typing import Dict, Any
from .models.meeting import ZoomMeetingModel

class ZoomNormalizer:
    
    @staticmethod
    def normalize_meeting(meeting: ZoomMeetingModel) -> Dict[str, Any]:
        """Converts a Zoom Meeting & Transcript into an AgentOS UniversalEvent."""
        
        # A simple keyword check to boost severity before the heavy AI kicks in
        content = meeting.transcript.text_content.lower()
        is_escalated = any(word in content for word in ["cancel", "competitor", "frustrated", "blocking"])
        
        severity = "Critical" if is_escalated else "High" if meeting.is_high_value else "Medium"

        return {
            "source": "zoom",
            "entity_type": "meeting_transcript",
            "repository": "Cloud_Recordings", 
            "title": f"Meeting: {meeting.topic}",
            "description": f"Transcript Snippet: {meeting.transcript.text_content[:800]}...", 
            "author": meeting.host_id,
            "severity": severity,
            "timestamp": meeting.start_time.isoformat(),
            "metadata": {
                "meeting_id": meeting.id,
                "duration": meeting.duration_minutes,
                "has_churn_signals": is_escalated
            },
            # Module 17 & 20: Neo4j will connect this meeting to Salesforce Accounts & Zendesk Tickets!
            "linked_entities": [] 
        }