import json
from typing import Dict, Any
from database.postgres_setup import SessionLocal
from database.models import WorkspaceIntegration
from integrations.jira.services.auto_prd_service import AutoPRDToJiraOrchestrator
from agents.llm_router import call_cloud_llm

class ClosedLoopAutomation:
    """
    The 'Killer Feature' Engine.
    Listens to customer pain (Zendesk), extracts revenue impact, and autonomously 
    orchestrates engineering work (Jira Epics/Stories).
    """

    async def _analyze_customer_ticket(self, ticket_text: str) -> Dict[str, Any]:
        """Micro-agent to analyze Zendesk ticket for Theme and Revenue Risk."""
        print("🤖 [Killer Loop] Analyzing Customer Ticket via AI...")
        
        prompt = f"""
        Analyze this customer support ticket: "{ticket_text}"
        
        Extract the following as a strict JSON object:
        {{
            "title": "A short 5-word title for the engineering ticket",
            "theme": "The core technical theme (e.g., Authentication, Payments, UI)",
            "revenue_risk_usd": 5000, 
            "priority": "High/Medium/Low"
        }}
        Estimate revenue_risk_usd based on standard enterprise SaaS logic (e.g., checkout bugs = high risk).
        """
        
        try:
            res = await call_cloud_llm(prompt=prompt, system_prompt="You are a strict JSON data extractor. Output ONLY valid JSON.")
            return json.loads(res.strip())
        except Exception as e:
            print(f"🚨 [Killer Loop AI Error]: {e}")
            return {
                "title": "Customer Reported Issue",
                "theme": "General",
                "revenue_risk_usd": 1000,
                "priority": "Medium"
            }

    async def execute_zendesk_to_jira_loop(self, workspace_id: str, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the full pipeline: Zendesk -> AI Analysis -> Jira PRD/Epic Creation.
        """
        print(f"\n🌪️ [Killer Loop] TRIGGERED for Workspace: {workspace_id}")
        
        # 1. Extract raw Zendesk Data
        ticket_text = ticket_data.get("description", "")
        customer_email = ticket_data.get("requester_email", "customer@example.com")
        
        # 2. Run AI Analysis
        ai_insights = await self._analyze_customer_ticket(ticket_text)
        print(f"📈 [Killer Loop] AI Insights: {ai_insights['theme']} | Risk: ${ai_insights['revenue_risk_usd']}")

        db = SessionLocal()
        try:
            # 3. Fetch Jira Credentials for execution
            integration = db.query(WorkspaceIntegration).filter(
                WorkspaceIntegration.workspace_id == workspace_id,
                WorkspaceIntegration.provider == "jira"
            ).first()

            if not integration or not integration.access_token:
                return {"status": "error", "message": "Execution halted. Jira not connected."}

            domain = integration.account_name.replace(".atlassian.net", "").replace("https://", "")
            
            # 4. Hand over to Module 11 (Auto PRD -> Jira)
            print("⚙️ [Killer Loop] Handing over to Jira Auto-PRD Orchestrator...")
            orchestrator = AutoPRDToJiraOrchestrator(
                domain=domain, 
                email=customer_email, # Using customer email for context
                token=integration.access_token, 
                project_key="ENG" # Defaulting to ENG project
            )

            jira_result = await orchestrator.execute_autonomous_pipeline(
                title=ai_insights["title"],
                feedback_text=ticket_text,
                theme_data={"core_theme": ai_insights["theme"], "source": "Zendesk Integration"},
                revenue_risk=ai_insights["revenue_risk_usd"]
            )

            # 5. The Ultimate Closed-Loop Result
            return {
                "status": "success",
                "message": "Closed-loop automation executed successfully.",
                "trigger_source": "Zendesk",
                "customer_impact": f"${ai_insights['revenue_risk_usd']} at risk",
                "jira_execution": jira_result
            }

        except Exception as e:
            print(f"🚨 [Killer Loop Execution Error]: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

# Global Instance
killer_loop_engine = ClosedLoopAutomation()