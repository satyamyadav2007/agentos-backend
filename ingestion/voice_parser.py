# ingestion/voice_parser.py
print("[Whisper AI] Voice Parser Module Initialized...")

async def parse_zoom_transcript(transcript_text: str):
    """
    In production, this routes to an LLM to detect language and extract the bug.
    For the MVP, we assume the LLM has already translated and extracted the core complaint.
    """
    print(f"🎙️ [Voice Parser] Analyzing Zoom Call Transcript...")
    
    # Simulating LLM extraction from a Hindi/English mixed transcript
    detected_language = "Mixed (Hindi/English)"
    extracted_issue = "User repeatedly mentioned 'app hang ho raha hai payment ke time'. Authentication timeout confirmed."
    
    return {
        "source": "Zoom Call Transcript",
        "language": detected_language,
        "translated_issue_body": extracted_issue
    }