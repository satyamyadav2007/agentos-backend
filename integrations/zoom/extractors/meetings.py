from typing import List
from datetime import datetime
from integrations.zoom.models.meeting import ZoomMeetingModel, ZoomTranscriptModel

class ZoomMeetingExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_recent_meetings_with_transcripts(self, user_id: str = "me", days: int = 7) -> List[ZoomMeetingModel]:
        print(f"📹 [Zoom Extractor] Fetching Cloud Recordings & Transcripts for last {days} days...")
        
        from datetime import timedelta
        from_date = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        try:
            # 1. Get user's cloud recordings
            params = {"from": from_date, "page_size": 30}
            raw_data = await self.client.get(f"users/{user_id}/recordings", params=params)
            meetings_data = raw_data.get("meetings", [])
            
            meetings = []
            for m_data in meetings_data:
                meeting = ZoomMeetingModel(
                    id=str(m_data.get("id")),
                    uuid=m_data.get("uuid"),
                    host_id=m_data.get("host_id"),
                    topic=m_data.get("topic", "Zoom Meeting"),
                    start_time=datetime.fromisoformat(m_data.get("start_time", "").replace('Z', '+00:00')),
                    duration_minutes=m_data.get("duration", 0),
                    total_participants=m_data.get("recording_count", 0) # Approximation if actual participants API not called
                )
                
                # 2. Find Transcript File in Recording Files
                for rec_file in m_data.get("recording_files", []):
                    if rec_file.get("file_type") == "TRANSCRIPT":
                        download_url = rec_file.get("download_url")
                        # In production, we queue this download. Here we do it sequentially for the MVP.
                        transcript_text = await self.client.download_transcript(download_url)
                        
                        meeting.transcript = ZoomTranscriptModel(
                            id=rec_file.get("id"),
                            meeting_id=meeting.id,
                            text_content=transcript_text[:5000] # Cap for AI context limits
                        )
                        break # Got the transcript
                        
                # Only keep meetings that actually have spoken data
                if meeting.transcript:
                    meetings.append(meeting)
                    
            print(f"   ✅ Extracted {len(meetings)} meetings with full transcripts.")
            return meetings
            
        except Exception as e:
            print(f"🚨 [Zoom Extractor] Failed to fetch meetings: {e}")
            return []