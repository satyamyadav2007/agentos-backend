# agents/prd_agent.py
from ollama import AsyncClient

async def generate_prd(text: str, theme_data: dict, revenue_risk: int):
    print("[PRD Agent] Drafting automated PRD...")
    
    # Prompt engineering specifically designed for actionable dev tasks
    system_prompt = f"""
    You are an expert AI Product Manager. 
    A user reported the following feedback: "{text}"
    AI Analysis identified this as: {theme_data.get('category')} (Severity: {theme_data.get('severity')}).
    Revenue at Risk: ${revenue_risk}
    
    Draft a concise, actionable PRD (Product Requirements Document) snippet for the engineering team.
    Format your response cleanly using these exact headings:
    
    **User Story:** [1 sentence]
    **Acceptance Criteria:** [2-3 bullet points]
    **Engineering Task:** [1 brief sentence on what to fix/build]
    
    Keep the total response under 100 words. Do not add any introductory or concluding text.
    """
    
    try:
        response = await AsyncClient().chat(
            model='llama3',
            messages=[{'role': 'system', 'content': system_prompt}],
            options={"temperature": 0.3} # slightly creative but focused
        )
        return response['message']['content'].strip()
    except Exception as e:
        print(f"[Error] PRD Agent failed: {e}")
        return "PRD generation failed due to model error."