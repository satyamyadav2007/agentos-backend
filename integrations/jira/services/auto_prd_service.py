import re
import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, Any, Optional

# Integrating your existing routing and knowledge retrieval[cite: 1]
from agents.llm_router import call_cloud_llm
from integrations.knowledge_gateway import knowledge_gateway

class AutoPRDToJiraOrchestrator:
    """
    Module 11: Auto PRD → Jira
    Autonomously drafts a PRD using internal architecture docs and converts it 
    into a cascading Jira hierarchy (Epic -> Story -> Task).
    """

    def __init__(self, domain: str, email: str, token: str, project_key: str):
        self.domain = domain
        self.email = email
        self.token = token
        self.project_key = project_key
        
        # Initializing HTTP Basic Auth for Jira REST API v2 #[cite: 2]
        self.auth = HTTPBasicAuth(self.email, self.token) #[cite: 2]
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        } #[cite: 2]

    async def _generate_prd_content(self, text: str, theme_data: dict, revenue_risk: int) -> str:
        """Uses the PRDAgent logic to generate a structured PRD."""
        print("📝 [PRD Agent] Drafting Autonomous Engineering Ticket...")

        # RAG: Fetch internal company architecture/docs based on the theme[cite: 1]
        issue_topic = theme_data.get("summary") or theme_data.get("category") or "general bug"

        try:
            internal_docs = await knowledge_gateway.fetch_architecture_context(issue_topic)
        except Exception as e:
            print(f"[Warning] Knowledge Gateway failed: {e}")
            internal_docs = "No internal documentation available."

        system_prompt = """
You are an expert Enterprise AI Product Manager.

Generate a concise Jira-ready PRD.

Use EXACTLY this format:

**User Story:**
<1 sentence>

**Acceptance Criteria:**
- Bullet 1
- Bullet 2
- Bullet 3

**Engineering Task:**
<1 short implementation task>

IMPORTANT:
- Follow the internal company architecture and engineering rules.
- Keep the response under 150 words.
- Do not add introductions or conclusions.
"""

        user_prompt = f"""
User Feedback:
{text}

AI Analysis:
{theme_data}

Revenue at Risk:
${revenue_risk}

===========================
INTERNAL COMPANY DOCUMENTS
(Notion / Confluence / Architecture)
===========================

{internal_docs}

The solution MUST follow the internal company documentation above.
"""

        try:
            prd_draft = await call_cloud_llm(
                prompt=user_prompt, #[cite: 1]
                system_prompt=system_prompt #[cite: 1]
            )
            return prd_draft.strip()

        except Exception as e:
            print(f"[Error] PRD Agent failed: {e}")
            return ""

    def _create_jira_issue(self, summary: str, description: str, issue_type: str, parent_key: Optional[str] = None) -> Optional[str]:
        """Creates an individual ticket in Jira using the REST API."""
        url = f"https://{self.domain}.atlassian.net/rest/api/2/issue"
        
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary[:255],  # Jira has a 255 character limit for titles #[cite: 2]
                "description": description,
                "issuetype": {"name": issue_type}
            }
        }
        
        # Link to Epic or Parent if provided
        if parent_key:
            if issue_type == "Story":
                payload["fields"]["customfield_10014"] = parent_key # Standard Jira Cloud Epic Link field
            else:
                payload["fields"]["parent"] = {"key": parent_key} # Subtasks/Tasks under a Story
                
        response = requests.post(url, json=payload, headers=self.headers, auth=self.auth) #[cite: 2]
        
        if response.status_code == 201: #[cite: 2]
            issue_key = response.json().get('key') #[cite: 2]
            print(f"✅ Created {issue_type}: {issue_key}")
            return issue_key
        else:
            print(f"🚨 [Jira Error] {response.text}") #[cite: 2]
            return None

    def _parse_prd(self, prd_text: str) -> Dict[str, str]:
        """Extracts the strictly formatted sections from the AI output."""
        parsed_data = {}
        
        # Regex to capture content between headers
        us_match = re.search(r'\*\*User Story:\*\*(.*?)(?=\*\*Acceptance Criteria:\*\*|$)', prd_text, re.DOTALL)
        ac_match = re.search(r'\*\*Acceptance Criteria:\*\*(.*?)(?=\*\*Engineering Task:\*\*|$)', prd_text, re.DOTALL)
        et_match = re.search(r'\*\*Engineering Task:\*\*(.*?)$', prd_text, re.DOTALL)
        
        parsed_data['user_story'] = us_match.group(1).strip() if us_match else "Fix identified issue."
        parsed_data['acceptance_criteria'] = ac_match.group(1).strip() if ac_match else "Ensure system stability."
        parsed_data['engineering_task'] = et_match.group(1).strip() if et_match else "Implement backend and frontend updates."
        
        return parsed_data

    async def execute_autonomous_pipeline(self, title: str, feedback_text: str, theme_data: dict, revenue_risk: int) -> Dict[str, Any]:
        """The main execution arm: Drafts the PRD and creates the entire Jira hierarchy."""
        print(f"🚀 [AgentOS] Triggering Auto-PRD Pipeline for: {title}")
        
        # Step 1: Agent drafts the PRD
        prd_text = await self._generate_prd_content(feedback_text, theme_data, revenue_risk)
        if not prd_text:
            return {"status": "error", "message": "PRD generation failed due to model error."}[cite: 1]
            
        # Step 2: Parse the structured output
        parsed_prd = self._parse_prd(prd_text)
        
        # Step 3: Create the Epic
        epic_desc = f"Autonomously generated Epic for {title}.\n\nContext:\n{feedback_text}"
        epic_key = self._create_jira_issue(
            summary=f"[AI Epic] {title}", 
            description=epic_desc, 
            issue_type="Epic"
        )
        
        if not epic_key:
            return {"status": "error", "message": "Failed to map Epic."}
            
        # Step 4: Create the User Story inside the Epic
        story_desc = f"{parsed_prd['user_story']}\n\n*Acceptance Criteria:*\n{parsed_prd['acceptance_criteria']}"
        story_key = self._create_jira_issue(
            summary=parsed_prd['user_story'][:100], 
            description=story_desc, 
            issue_type="Story", 
            parent_key=epic_key
        )
        
        # Step 5: Create the Engineering Task inside the Story
        if story_key:
            task_key = self._create_jira_issue(
                summary=f"Eng Task: {parsed_prd['engineering_task'][:100]}", 
                description=parsed_prd['engineering_task'], 
                issue_type="Task", # By default creating it as a Task #[cite: 2]
                parent_key=story_key
            )
            
        return {
            "status": "success",
            "hierarchy": {
                "epic": f"https://{self.domain}.atlassian.net/browse/{epic_key}", #[cite: 2]
                "story": f"https://{self.domain}.atlassian.net/browse/{story_key}" if story_key else None, #[cite: 2]
                "task": f"https://{self.domain}.atlassian.net/browse/{task_key}" if 'task_key' in locals() else None #[cite: 2]
            }
        }