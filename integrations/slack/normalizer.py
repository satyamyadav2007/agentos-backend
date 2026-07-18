from typing import Dict, Any

class SlackNormalizer:
    
    @staticmethod
    def normalize_message(raw_msg: Dict[str, Any], channel_name: str) -> Dict[str, Any]:
        """Converts a raw Slack Message into the AgentOS UniversalEvent format with AI Heuristics."""
        
        text = raw_msg.get("text", "")
        text_lower = text.lower()
        
        # 🚨 Module 4: Incident Detection
        incident_keywords = ["down", "broken", "critical", "incident", "outage", "p0", "timeout", "rollback", "sev-1", "crash"]
        is_incident = any(w in text_lower for w in incident_keywords)
        
        # 🤝 Module 5: Decision Tracking
        decision_keywords = ["we should", "decided to", "agreed to", "will proceed with", "approved"]
        contains_decision = any(w in text_lower for w in decision_keywords)
        
        # 🛠️ Module 6: Action Item Extraction
        action_keywords = ["i will", "i'll", "on it", "fixing it", "looking into it", "tomorrow"]
        contains_action = any(w in text_lower for w in action_keywords)
        
        # 😡 Module 9: Sentiment Analysis (Pre-LLM heuristics)
        sentiment = "neutral"
        if any(w in text_lower for w in ["fuck", "shit", "frustrating", "blocker", "stuck", "failing"]):
            sentiment = "frustrated"
        elif any(w in text_lower for w in ["urgent", "asap", "now", "hurry", "immediately"]):
            sentiment = "urgent"
            
        # Determine Entity Type and Severity
        entity_type = "incident" if is_incident else ("decision" if contains_decision else "conversation")
        severity = "High" if (is_incident or sentiment == "urgent") else "Medium"

        # Using a snippet of the text as the Title
        title = text[:60] + "..." if len(text) > 60 else text
        if not title.strip():
            title = "Empty Message / File Attachment"

        return {
            "source": "slack",
            "entity_type": entity_type,
            "repository": channel_name, # Treating channel as the 'repo/project' equivalent
            "title": title,
            "description": text,
            "author": raw_msg.get("user", "Unknown"),
            "severity": severity,
            "timestamp": raw_msg.get("ts"),
            "metadata": {
                "thread_ts": raw_msg.get("thread_ts"),
                "channel": channel_name,
                "reactions": [r.get("name") for r in raw_msg.get("reactions", [])],
                "contains_decision": contains_decision,
                "contains_action": contains_action,
                "sentiment_flag": sentiment
            },
            "linked_entities": []
        }