from typing import Dict, Any
from .models.meeting import GoogleMeetModel

class GoogleMeetNormalizer:
    
    @staticmethod
    def normalize_meeting(meeting: GoogleMeetModel) -> Dict[str, Any]:
        """Converts a Google Meet session into an AgentOS UniversalEvent."""
        
        severity = "High" if meeting.is_strategic_call else "Medium"
        
        # Combine summary and transcript snippet for the AI Theme Agent
        content_desc = meeting.description
        if meeting.transcript_text:
            content_desc += f"\n\nTranscript Snippet: {meeting.transcript_text[:1000]}"

        return {
            "source": "google_meet",
            "entity_type": "meeting",
            "repository": "Workspace_Calendar",
            "title": f"Meet: {meeting.summary}",
            "description": content_desc,
            "author": meeting.organizer_email,
            "severity": severity,
            "timestamp": meeting.start_time.isoformat(),
            "metadata": {
                "meeting_id": meeting.id,
                "meet_url": meeting.meet_link,
                "participant_count": len(meeting.participants),
                "has_transcript": bool(meeting.transcript_text)
            },
            # Graph Connections! Module 7: Meeting -> Decision -> Jira -> GitHub
            "linked_entities": [] 
        }