from .llm_router import call_cloud_llm

async def generate_prd(text: str, theme_data: dict, revenue_risk: int):
    print("[PRD Agent] Drafting automated PRD via Cloud LLM...")
    
    system_prompt = """
    You are an expert AI Product Manager. 
    Draft a concise, actionable PRD (Product Requirements Document) snippet for the engineering team based on the context provided.
    Format your response cleanly using these exact headings:
    
    **User Story:** [1 sentence]
    **Acceptance Criteria:** [2-3 bullet points]
    **Engineering Task:** [1 brief sentence on what to fix/build]
    
    Keep the total response under 100 words. Do not add any introductory or concluding text.
    """
    
    user_prompt = f"""
    User Feedback: "{text}"
    AI Analysis: {theme_data.get('category')} (Severity: {theme_data.get('severity')}).
    Revenue at Risk: ${revenue_risk}
    """
    
    try:
        # ⚡ Calling Cloud LLM via router
        prd_draft = await call_cloud_llm(prompt=user_prompt, system_prompt=system_prompt)
        return prd_draft.strip()
    except Exception as e:
        print(f"[Error] PRD Agent failed: {e}")
        return "PRD generation failed due to model error."