from typing import Dict, Any
from .normalizer import GitHubNormalizer

class GitHubWebhookHandler:
    def __init__(self):
        print("🕸️ [GitHub Webhook] Initialized. Listening for live events...")
        
    async def handle_event(self, event_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        print(f"\n🔔 [GitHub Webhook] Received live event: '{event_name}'")
        
        # 1. ISSUE OPENED OR EDITED
        if event_name == "issues" and payload.get("action") in ["opened", "edited"]:
            raw_issue = payload["issue"]
            repo_name = payload["repository"]["full_name"]
            
            print(f"🚨 [Live Alert] New Issue in {repo_name}: {raw_issue['title']}")
            
            # Universal format mein convert karo
            normalized_event = GitHubNormalizer.normalize_issue(raw_issue, repo_name)
            
            # FUTURE: Yahan se sidha orchestrator.process_single_issue() ko bhejenge
            return {"status": "processed", "type": "issue", "data": normalized_event}
            
        # 2. PR OPENED
        elif event_name == "pull_request" and payload.get("action") in ["opened", "synchronize"]:
            raw_pr = payload["pull_request"]
            repo_name = payload["repository"]["full_name"]
            
            print(f"🚀 [Live Alert] New PR in {repo_name}: {raw_pr['title']}")
            
            normalized_event = GitHubNormalizer.normalize_pr(raw_pr, repo_name)
            return {"status": "processed", "type": "pr", "data": normalized_event}
            
        # Ignore unsupported events (like stars, forks, etc.)
        return {"status": "ignored", "reason": f"Event action '{payload.get('action')}' not tracked."}

github_webhook_handler = GitHubWebhookHandler()