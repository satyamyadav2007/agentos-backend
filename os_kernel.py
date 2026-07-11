import asyncio
from orchestrator import run_orchestrator
from ingestion.voice_parser import parse_zoom_transcript
from agents.github_agent import github_agent

# ⚡ THE FIX: Missing import added
from agents.support_agent import normalize_support_ticket 

class AgentOSKernel:
    def __init__(self):
        print("🧠 [AgentOS Kernel] Booting up centralized AI Router...")

    async def _route_github_issue(self, payload: dict, user_email: str):
        print("🚥 [Router] Intent detected: GitHub Bug/Issue Tracking.")
        
        repo_name = payload.get("repository", {}).get("full_name", "satyamyadav2007/satyamos")
        issue_number = payload.get("number", payload.get("issue", {}).get("number", 1))
        
        enriched_issue = github_agent.extract_issue_context(repo_name, issue_number)
        final_payload = enriched_issue if enriched_issue else payload
        
        print("      ↳ [Router] Handoff from GitHub Agent -> Orchestrator")
        return await run_orchestrator([final_payload], user_email)

    async def _route_voice_call(self, transcript: str, user_email: str):
        print("🚥 [Router] Intent detected: Customer Voice/Zoom Transcript.")
        parsed_data = await parse_zoom_transcript(transcript)
        
        simulated_issue = {
            "id": "VOICE-001",
            "title": "Reported via Zoom: Critical Error",
            "body": parsed_data["translated_issue_body"]
        }
        print("      ↳ [Router] Handoff from Voice Parser -> Orchestrator")
        return await run_orchestrator([simulated_issue], user_email)

    async def _route_zendesk_ticket(self, payload: dict, user_email: str):
        print("🚥 [Router] Intent detected: Zendesk Support Ticket.")
        
        raw_desc = payload.get("description", "")
        ticket_id = payload.get("id", "000")
        subject = payload.get("subject", "Customer Escalation")
        
        normalized_issue_body = await normalize_support_ticket(raw_desc)
        
        standard_issue = {
            "id": f"ZD-{ticket_id}",
            "title": subject,
            "body": normalized_issue_body
        }
        
        print("      ↳ [Router] Handoff from Support Agent -> Orchestrator")
        return await run_orchestrator([standard_issue], user_email)

    async def execute(self, request_type: str, raw_payload: any, user_email: str = "default@client.com"):
        try:
            if request_type == "github_issue":
                return await self._route_github_issue(raw_payload, user_email)
            elif request_type == "zoom_transcript":
                return await self._route_voice_call(raw_payload, user_email)
            elif request_type == "zendesk_ticket":
                return await self._route_zendesk_ticket(raw_payload, user_email)
            else:
                return {"error": f"Unknown request type '{request_type}'."}
                
        except Exception as e:
            import traceback
            traceback.print_exc() # ⚡ NEW: Ye exact line number batayega next time
            print(f"🚨 [Kernel Panic] Routing failed: {str(e)}")
            return {"error": "Critical system failure in AgentOS Kernel."}

kernel = AgentOSKernel()