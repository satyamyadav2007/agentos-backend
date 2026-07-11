from typing import Dict, Any

class SlackNormalizer:
    
    @staticmethod
    def normalize_message(raw_msg: Dict[str, Any], channel_name: str) -> Dict[str, Any]:
        """Converts a raw Slack Message into the AgentOS UniversalEvent format."""
        
        text = raw_msg.get("text", "")
        
        # Simple heuristic fallback (AI Theme Agent will refine this later)
        severity = "Medium"
        text_lower = text.lower()
        if any(w in text_lower for w in ["down", "broken", "critical", "incident", "outage", "p0"]):
            severity = "High"

        # Using a snippet of the text as the Title
        title = text[:50] + "..." if len(text) > 50 else text
        if not title.strip():
            title = "Empty Message / File Attachment"

        return {
            "source": "slack",
            "entity_type": "message",
            "repository": channel_name, # Treating channel as the 'repo/project' equivalent
            "title": title,
            "description": text,
            "author": raw_msg.get("user", "Unknown"),
            "severity": severity,
            "timestamp": raw_msg.get("ts"),
            "metadata": {
                "thread_ts": raw_msg.get("thread_ts"),
                "channel": channel_name,
                "reactions": [r.get("name") for r in raw_msg.get("reactions", [])]
            },
            "linked_entities": []
        }