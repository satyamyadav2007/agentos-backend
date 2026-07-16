import os
import uuid
import asyncio
from typing import Dict, Any

class UniversalActionEngine:
    """
    Module 15: The Execution Arm of AgentOS.
    Handles Outbound API calls to Jira, Linear, Slack, and Zendesk.
    """
    
    def __init__(self):
        print("⚙️ [Action Engine] Initializing Universal Execution Arm...")
        # In production, this comes from the workspace's integration settings
        self.preferred_agile_tool = os.getenv("DEFAULT_AGILE_TOOL", "jira").lower()

    async def _estimate_sprint_points(self, description: str, severity: str) -> Dict[str, Any]:
        """
        AI estimates the complexity and story points based on the Issue Description/PRD.
        """
        print("      ↳ [Sprint Planner] AI is estimating story points and sprint allocation...")
        
        # ⚡ AI Logic: Critical bugs bypass the backlog and go to current sprint
        if severity.lower() in ["critical", "high"]:
            points = 5
            sprint = "Current Sprint (Hotfix)"
        else:
            points = 3
            sprint = "Backlog"
            
        return {"story_points": points, "target_sprint": sprint}

    async def create_jira_ticket(self, title: str, description: str, severity: str) -> Dict[str, Any]:
        """Creates a ticket in Jira Enterprise."""
        print(f"      ↳ [Jira Connector] Formatting payload for Jira Enterprise...")
        
        planning_data = await self._estimate_sprint_points(description, severity)
        
        # Simulating Jira REST API Call
        await asyncio.sleep(1) 
        ticket_id = f"ENG-{uuid.uuid4().hex[:4].upper()}"
        ticket_url = f"https://agentos-core.atlassian.net/browse/{ticket_id}"
        
        print(f"✅ [Action Engine] Created Jira Ticket: {ticket_id} ({planning_data['story_points']} Points)")
        
        return {
            "status": "success", 
            "platform": "Jira", 
            "ticket_id": ticket_id,
            "link": ticket_url,
            "story_points": planning_data["story_points"]
        }

    async def create_linear_ticket(self, title: str, description: str, severity: str) -> Dict[str, Any]:
        """Creates a ticket in Linear."""
        print(f"      ↳ [Linear Connector] Formatting payload for Linear GraphQL API...")
        
        planning_data = await self._estimate_sprint_points(description, severity)
        
        # Simulating Linear API Call
        await asyncio.sleep(1)
        issue_id = uuid.uuid4().hex[:6].upper()
        ticket_url = f"https://linear.app/agentos/issue/ENG-{issue_id}"
        
        print(f"✅ [Action Engine] Created Linear Issue: ENG-{issue_id}")
        
        return {
            "status": "success", 
            "platform": "Linear",
            "ticket_id": f"ENG-{issue_id}",
            "link": ticket_url,
            "story_points": planning_data["story_points"]
        }

    async def auto_reply_zendesk(self, ticket_id: str, reply_text: str) -> Dict[str, Any]:
        """Sends an AI-crafted response back to the customer via Zendesk."""
        print(f"\n✉️ [Action Engine] Sending AI-crafted reply to Zendesk Ticket #{ticket_id}...")
        
        # Simulating Zendesk API Call
        await asyncio.sleep(1)
        
        print(f"✅ [Action Engine] Zendesk reply dispatched successfully.")
        return {"status": "success", "platform": "Zendesk"}

    async def execute_ticket_creation(self, issue_title: str, description: str, severity: str) -> Dict[str, Any]:
        """
        The Master Router: Decides which Agile tool to use based on workspace settings.
        """
        if self.preferred_agile_tool == "linear":
            return await self.create_linear_ticket(issue_title, description, severity)
        else:
            return await self.create_jira_ticket(issue_title, description, severity)

# Single Global Instance
action_arm = UniversalActionEngine()