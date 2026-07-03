from .llm_router import call_cloud_llm
from database.graph_manager import graph_db  # ⚡ DB connection imported

async def ask_executive_cpo(user_message: str, dashboard_context: list):
    print(f"[Chat Agent] Analyzing query via Cloud LLM: '{user_message}'")
    
    # 1. Dashboard Metrics (ARR & Severity)
    context_str = "CURRENT DASHBOARD METRICS:\n"
    total_risk = 0
    for item in dashboard_context:
        title = item.get("originalText", "Unknown Issue")
        risk = item.get("revenue", {}).get("revenue_at_risk", 0)
        severity = item.get("analysis", {}).get("severity", "Unknown")
        total_risk += risk
        context_str += f"- Bug: {title} | Severity: {severity} | Revenue Risk: ${risk}\n"
    context_str += f"\nTOTAL REVENUE AT RISK: ${total_risk}\n\n"
    
    # 2. ⚡ ROOT CAUSE TELEMETRY (Phase 28: Fetching from Neo4j)
    context_str += "DEEP ROOT CAUSE ANALYSIS (Neo4j Graph):\n"
    try:
        with graph_db.driver.session() as session:
            result = session.run("MATCH (e:Engineer)-[:AUTHORED]->(cm:Commit)-[:INTRODUCED]->(b:Bug) RETURN e.name AS eng, cm.hash AS commit, b.title AS bug")
            for record in result:
                context_str += f"- {record['eng']} introduced bug '{record['bug']}' via commit #{record['commit']}.\n"
    except Exception as e:
        print(f"[Graph Warning] Could not fetch graph context: {e}")
    
    # 3. YC-Level System Prompt (Phase 10: Prioritization Engine rules added)
    system_prompt = f"""You are AgentOS, the AI Chief Product Officer.
    You speak directly to the CEO. Tone: Highly strategic, ruthless, data-driven.
    
    KNOWLEDGE BASE:
    {context_str}
    
    RULES:
    1. If asked who caused a crash, strictly name the Engineer and Commit Hash from the Deep Root Cause Analysis section.
    2. Suggest a 'Priority Score' (0-100) based on Revenue at Risk.
    3. Keep answers under 4 sentences.
    """

    try:
        ai_reply = await call_cloud_llm(prompt=user_message, system_prompt=system_prompt)
        return {"status": "success", "reply": ai_reply.strip()}
    except Exception as e:
        return {"status": "error", "reply": "System Error: Neural link severed."}