from typing import List
from datetime import datetime, timedelta
from integrations.google_meet.models.meeting import GoogleMeetModel, GoogleParticipantModel

class GoogleMeetExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_recent_meetings(self, limit: int = 20) -> List[GoogleMeetModel]:
        print(f"📅 [Google Meet Extractor] Scanning Workspace for recent intelligent meetings...")
        
        time_min = (datetime.utcnow() - timedelta(days=7)).isoformat() + 'Z'
        params = {
            "timeMin": time_min,
            "maxResults": limit * 2,
            "singleEvents": True,
            "orderBy": "startTime"
        }
        
        try:
            raw_data = await self.client.get_calendar_events(params=params)
            events = raw_data.get("items", [])
            
            meetings = []
            for event in events:
                # Only process events with a Google Meet conference attached
                conference_data = event.get("conferenceData", {})
                if not conference_data:
                    continue
                    
                entry_points = conference_data.get("entryPoints", [])
                meet_link = next((ep["uri"] for ep in entry_points if ep["entryPointType"] == "video"), None)
                
                if not meet_link:
                    continue
                    
                participants = [
                    GoogleParticipantModel(
                        email=a.get("email", ""),
                        display_name=a.get("displayName"),
                        response_status=a.get("responseStatus", "unknown")
                    ) for a in event.get("attendees", [])
                ]
                
                meeting = GoogleMeetModel(
                    id=event.get("id"),
                    summary=event.get("summary", "Untitled Meeting"),
                    description=event.get("description", ""),
                    start_time=datetime.fromisoformat(event.get("start", {}).get("dateTime", "").replace('Z', '+00:00')),
                    end_time=datetime.fromisoformat(event.get("end", {}).get("dateTime", "").replace('Z', '+00:00')),
                    meet_link=meet_link,
                    organizer_email=event.get("organizer", {}).get("email", ""),
                    participants=participants
                )
                
                # In production: Map Google Drive attachments (Transcripts/Recordings) to the meeting
                attachments = event.get("attachments", [])
                for att in attachments:
                    if "transcript" in att.get("title", "").lower():
                        # Here we would call self.client.get_drive_file_text(att['fileId'])
                        meeting.transcript_text = "[Google Meet Transcript Content placeholder...]"
                
                meetings.append(meeting)
                
            print(f"   ✅ Extracted {len(meetings)} Google Meet records.")
            return meetings[:limit]
            
        except Exception as e:
            print(f"🚨 [Google Meet Extractor] Failed to fetch meetings: {e}")
            return []