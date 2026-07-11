import os
import json
import uuid

class ActionEngine:
    def __init__(self):
        print("⚙️ [Action Engine] Initializing Universal Execution Arm (Jira / Linear)...")
        # In production, these come from the client's integration settings
        self.preferred_tool = os.getenv("DEFAULT_AGILE_TOOL", "jira").lower()

    async def _estimate_sprint_points(self, prd_text: str, severity: str):
        """
        AI estimates the complexity and story points based on the PRD.
        """
        print("      ↳ [Sprint Planner] AI is estimating story points and sprint allocation...")
        
        # ⚡ MVP Simulation: In production, you'd send the PRD to Groq/LLM to get these numbers.
        points = 8 if severity.lower() == "high" else 3
        sprint = "Current Sprint (Sprint 21)" if severity.lower() == "high" else "Backlog"
        
        return {"story_points": points, "target_sprint": sprint}

    async def _push_to_jira(self, title: str, prd_text: str, planning_data: dict):
        print(f"      ↳ [Jira Connector] Pushing to Atlassian API... Assigned {planning_data['story_points']} Points.")

        # TODO: Replace with actual Jira REST API call
        jira_response = {
            "key": "ENG-142",
            "self": "https://agentos-core.atlassian.net/browse/ENG-142"
        }

        return jira_response["self"]

    async def _push_to_linear(self, title: str, prd_text: str, planning_data: dict):
        print(f"      ↳ [Linear Connector] Pushing to Linear API... Assigned {planning_data['story_points']} Points.")

        # Temporary dynamic issue ID
        issue_id = uuid.uuid4().hex[:10]

        return f"https://linear.app/agentos/issue/{issue_id}"

    async def execute_ticket_creation(self, issue_title: str, prd_text: str, severity: str):
        """
        The Universal Webhook: Decides the tool and executes the creation.
        """
        # Step 1: AI Sprint Planning
        planning_data = await self._estimate_sprint_points(prd_text, severity)
        
        enriched_prd = f"{prd_text}\n\n---\n**AI Sprint Plan:**\n- Story Points: {planning_data['story_points']}\n- Allocation: {planning_data['target_sprint']}"

        # Step 2: Route to the correct Agile Tool
        ticket_url = None
        if self.preferred_tool == "linear":
            ticket_url = await self._push_to_linear(issue_title, enriched_prd, planning_data)
        else:
            ticket_url = await self._push_to_jira(issue_title, enriched_prd, planning_data)
            
        print(f"✅ [Action Engine] Ticket successfully mapped and created: {ticket_url}")
        return {
            "ticket_url": ticket_url,
            "story_points": planning_data["story_points"],
            "sprint": planning_data["target_sprint"]
        }

# Global Instance
action_engine = ActionEngine()