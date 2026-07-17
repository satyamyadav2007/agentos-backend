from typing import Dict, Any
from .normalizer import GitHubNormalizer

class GitHubWebhookHandler:
    def __init__(self):
        print("🕸️ [GitHub Webhook] Initialized. Listening for live events...")
        
    # ⚡ DB parameter removed! Webhook ka kaam ab sirf live data route karna hai
    async def handle_event(self, event_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        print(f"\n🔔 [GitHub Webhook] Received live event: '{event_name}'")
        action = payload.get("action", "unknown")
        
        # 1. SETUP EVENTS (NO DB SAVING HERE)
        # Ye events bas acknowledge honge, DB save '/connect' API me hoga
        if event_name in ["installation", "installation_repositories"]:
            installation_id = str(payload.get("installation", {}).get("id"))
            
            print(f"⚙️ [GitHub App Event] Installation: {installation_id} | Action: {action}")
            return {"status": "processed", "type": "setup_event_ignored_for_db"}
            
        # 2. ISSUE OPENED OR EDITED
        elif event_name == "issues" and action in ["opened", "edited"]:
            raw_issue = payload.get("issue", {})
            repo_name = payload.get("repository", {}).get("full_name", "Unknown")
            
            print(f"🚨 [Live Alert] Issue {action} in {repo_name}: {raw_issue.get('title')}")
            
            # Universal format mein convert karo
            normalized_event = GitHubNormalizer.normalize_issue(raw_issue, repo_name)
            
            # FUTURE: Yahan se sidha orchestrator ko bhejenge
            return {"status": "processed", "type": "issue", "data": normalized_event}
            
        # 3. PR OPENED OR SYNCED
        elif event_name == "pull_request" and action in ["opened", "synchronize"]:
            raw_pr = payload.get("pull_request", {})
            repo_name = payload.get("repository", {}).get("full_name", "Unknown")
            
            print(f"🚀 [Live Alert] PR {action} in {repo_name}: {raw_pr.get('title')}")
            
            # Universal format mein convert karo
            normalized_event = GitHubNormalizer.normalize_pr(raw_pr, repo_name)
            
            # FUTURE: Yahan se sidha orchestrator ko bhejenge
            return {"status": "processed", "type": "pr", "data": normalized_event}
            
        # 4. IGNORE EVERYTHING ELSE
        else:
            return {"status": "ignored", "reason": f"Event '{event_name}' with action '{action}' not tracked."}

github_webhook_handler = GitHubWebhookHandler()