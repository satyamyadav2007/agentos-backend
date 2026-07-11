# adapters/log_engine.py

def parse_engineering_logs(payload: dict, source: str) -> dict:
    """
    Parses complex, nested JSON from engineering and analytics tools 
    (Sentry, Datadog, Mixpanel, Amplitude) into a clean string for the LLM.
    """
    print(f"⚙️ [Log Engine] Decoding raw machine data from {source}...")
    
    parsed_data = {
        "title": "System Alert",
        "raw_text": ""
    }
    
    # 1. Sentry / Datadog (Crash Logs)
    if source in ["Sentry", "Datadog"]:
        event = payload.get("event", {})
        parsed_data["title"] = event.get("title", "Unhandled Exception")
        parsed_data["raw_text"] = f"Error Type: {event.get('type')}\nStacktrace: {str(event.get('stacktrace', 'Hidden'))}"
        
    # 2. Mixpanel / Amplitude (Product Analytics Anomaly)
    elif source in ["Mixpanel", "Amplitude"]:
        parsed_data["title"] = "Product Analytics Drop-off Warning"
        parsed_data["raw_text"] = f"Event: {payload.get('event_name')} dropped by {payload.get('drop_percentage')}%. User segment: {payload.get('segment')}."
        
    return parsed_data