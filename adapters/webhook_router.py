# adapters/webhook_router.py
import json

def identify_signal_source(headers: dict, payload: dict) -> str:
    """
    Detects the source of the webhook based on specific signatures.
    Covers 6 major platforms instantly.
    """
    headers_lower = {k.lower(): v for k, v in headers.items()}
    payload_str = json.dumps(payload).lower()

    # 1. GitHub
    if "x-github-event" in headers_lower:
        return f"GitHub ({headers_lower.get('x-github-event')})"
    
    # 2. Jira
    if "webhookevent" in payload and "jira" in payload.get("webhookevent", ""):
        return "Jira"
    
    # 3. Zendesk
    if "zendesk" in payload_str:
        return "Zendesk"
    
    # 4. Slack
    if "token" in payload and "team_id" in payload and "event" in payload:
        return "Slack Workspace"
    
    # 5. Discord
    if "application_id" in payload or "guild_id" in payload:
        return "Discord Server"
    
    # 6. Intercom
    if "type" in payload and payload.get("type") == "notification_event":
        return "Intercom"
    
    # Fallback
    return payload.get("source_name", "Unknown Webhook Source")


def normalize_pusher_payload(source: str, payload: dict) -> dict:
    """
    Takes raw JSON from standard webhooks and formats it instantly
    without using heavy third-party parsing tools (Zero RAM impact).
    """
    normalized = {
        "title": "Incoming Live Signal",
        "body": "No description provided.",
        "severity": "Medium"
    }
    
    try:
        # 1. GitHub Issue or Crash Hook
        if "issue" in payload:
            normalized["title"] = payload["issue"].get("title", "GitHub Issue")
            normalized["body"] = payload["issue"].get("body", "")
            normalized["severity"] = "High" if "bug" in json.dumps(payload).lower() else "Medium"
            
        # 2. Jira Webhook Event
        elif "issue" in payload and "fields" in payload["issue"]:
            fields = payload["issue"]["fields"]
            normalized["title"] = fields.get("summary", "Jira Ticket")
            normalized["body"] = fields.get("description", "")
            normalized["severity"] = fields.get("priority", {}).get("name", "Medium")
            
        # 3. Zendesk / Intercom Ticket Hook
        elif "ticket" in payload:
            normalized["title"] = payload["ticket"].get("subject", "Support Ticket")
            normalized["body"] = payload["ticket"].get("description", "")
            
        # 4. Slack / Discord Chat Signals
        elif "event" in payload and "text" in payload["event"]:
            normalized["title"] = "Slack Channel Mention"
            normalized["body"] = payload["event"]["text"]
        elif "content" in payload: # Discord standard
            normalized["title"] = "Discord Message Alert"
            normalized["body"] = payload["content"]
            
    except Exception as e:
        print(f"⚠️ [Pusher Normalizer Warning] Parsing minor glitch: {e}")
        
    return normalized    