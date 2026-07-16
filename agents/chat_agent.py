from .llm_router import call_cloud_llm

async def ask_executive_cpo(user_message: str, dashboard_context: list):
    print(f"💬 [Chat Agent] Analyzing executive query: '{user_message}'")
    
    # 1. Parse Dashboard Metrics (ARR & Severity)
    context_str = "CURRENT DASHBOARD METRICS (Source of Truth):\n"
    total_risk = 0
    
    if dashboard_context:
        for item in dashboard_context:
            title = item.get("originalText", "Unknown Issue")
            risk = item.get("revenue", {}).get("revenue_at_risk", 0)
            severity = item.get("analysis", {}).get("severity", "Unknown")
            total_risk += risk
            context_str += f"- Bug: {title} | Severity: {severity} | Revenue Risk: ${risk}\n"
    else:
        context_str += "- No active issues reported on the dashboard currently.\n"
        
    context_str += f"\nTOTAL REVENUE AT RISK: ${total_risk}\n\n"
    
    # 2. Executive CPO System Prompt (Optimized for Strategy)
    system_prompt = f"""You are AgentOS, the AI Chief Product Officer.
    You are speaking directly to the CEO. 
    Tone: Highly strategic, ruthless, data-driven, and extremely concise.
    
    KNOWLEDGE BASE:
    {context_str}
    
    RULES:
    1. Always base your answers on the KNOWLEDGE BASE provided above.
    2. Do not hallucinate metrics, bugs, or engineer names. If data is missing, state it clearly.
    3. If the user asks about revenue at risk, analyze it and provide a strategic recommendation.
    4. Keep answers under 4 sentences. Bullet points are encouraged for readability.
    """

    try:
        # 3. Call the ultra-fast Cloud LLM (Groq) via your LLM Router
        ai_reply = await call_cloud_llm(prompt=user_message, system_prompt=system_prompt)
        return {"status": "success", "reply": ai_reply.strip()}
    except Exception as e:
        print(f"🚨 [Chat Agent Error]: {e}")
        return {"status": "error", "reply": "System Error: Neural link severed."}