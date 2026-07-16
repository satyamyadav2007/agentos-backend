from typing import Dict, Any
from .normalizer import GitHubNormalizer
from sqlalchemy.orm import Session
from models.db_models import WorkspaceIntegration

class GitHubWebhookHandler:
    def __init__(self):
        print("🕸️ [GitHub Webhook] Initialized. Listening for live events...")
        
    async def handle_event(self, event_name: str, payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
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
        # 3. GITHUB APP INSTALLATION
        if event_name in ["installation", "installation_repositories"]:
            action = payload.get("action")
            installation_id = str(payload.get("installation", {}).get("id"))
            account_name = payload.get("installation", {}).get("account", {}).get("login")
            
            # Agar action "created" hai, toh DB me save karo
            if action == "created":
                # Note: Real scenario me workspace_id frontend payload ya state se aayega. 
                # Abhi ke liye hum default maan rahe hain.
                new_integration = WorkspaceIntegration(
                    workspace_id="default_workspace", 
                    provider="github",
                    installation_id=installation_id,
                    account_name=account_name
                )
                db.add(new_integration)
                db.commit()
                print(f"✅ Saved installation {installation_id} to Postgres!")

            return {"status": "processed", "type": "auth_setup"}
            
        # Ignore unsupported events (like stars, forks, etc.)
        return {"status": "ignored", "reason": f"Event action '{payload.get('action')}' not tracked."}

github_webhook_handler = GitHubWebhookHandler()