from .llm_router import call_cloud_llm
from integrations.knowledge_gateway import knowledge_gateway

class PRDAgent:
    async def generate_prd(self, text: str, theme_data: dict, revenue_risk: int):
        print("📝 [PRD Agent] Drafting Autonomous Engineering Ticket...")

        # ⚡ RAG: Fetch internal company architecture/docs
        issue_topic = (
            theme_data.get("summary")
            or theme_data.get("category")
            or "general bug"
        )

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
                prompt=user_prompt,
                system_prompt=system_prompt
            )

            return prd_draft.strip()

        except Exception as e:
            print(f"[Error] PRD Agent failed: {e}")
            return "PRD generation failed due to model error."


# Global Instance
prd_engine = PRDAgent()            