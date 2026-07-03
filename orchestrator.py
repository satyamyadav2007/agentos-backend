import asyncio
from agents.theme_agent import analyze_theme
from agents.revenue_agent import calculate_revenue_risk
from agents.prd_agent import generate_prd
from memory.vector_store import vector_memory
# Ensure CRM is imported to fetch quick ARR without heavy LLM logic
from integrations.manager import IntegrationManager
from database.graph_manager import graph_db



# Initialize CRM quickly
integration_manager = IntegrationManager()
crm_tool = integration_manager.crm

async def process_single_issue(issue_data: dict, user_email: str):
    issue_id = str(issue_data.get("id", issue_data.get("number", "unknown_id")))
    issue_text = issue_data.get("body", "") or issue_data.get("title", "")
    
    print(f"\n[Orchestrator] Processing Issue {issue_id}: {issue_data.get('title', 'Unknown')}")
    
    # ⚡ NEW: Sabse pehle Client ka Real ARR fetch karo (Fast, no LLM cost)
    client_data = await crm_tool.get_client_arr(user_email)
    base_revenue = {
        "revenue_at_risk": client_data.get("arr", 0), 
        "total_company_arr": client_data.get("arr", 0)
    }

    # 1. DUPLICATE CHECK (Vector Memory)
    dup_check = vector_memory.check_duplicate(issue_text)
    graph_db.ingest_root_cause_node(
        bug_title=issue_data.get("title", "Unknown Bug"),
        client_email=user_email,
        arr_impact=client_data.get("arr", 0)
    )
    
    if dup_check["is_duplicate"]:
        print(f"🔄 [Vector DB] Duplicate Alert! Matches existing root issue: {dup_check['matched_id']}")
        return {
            "status": "duplicate",
            "originalText": issue_text,
            "email": user_email,
            "analysis": {"category": "Duplicate (Aggregated)", "severity": "High", "summary": f"Merged with Root Issue {dup_check['matched_id']}. Impact escalated!"},
            "revenue": base_revenue, # ⚡ Yahan $0 ki jagah real ARR aayega
            "prd_draft": "Skipped PRD generation (Duplicate issue). Escalating Root Issue priority."
        }

    print("✨ [Vector DB] Novel issue detected. Adding to memory...")
    vector_memory.add_issue(issue_id=issue_id, text=issue_text, metadata={"client": user_email})
    
    # 2. PARALLEL EXECUTION (Theme & Revenue)
    theme_task = analyze_theme(issue_text)
    revenue_task = calculate_revenue_risk(issue_data, client_id=user_email)
    
    theme_data, revenue_data = await asyncio.gather(theme_task, revenue_task)
    
    # 3. GENERATE PRD
    if revenue_data.get("severity") == "High":
        prd_draft = await generate_prd(theme_data, revenue_data)
    else:
        prd_draft = "Skipped PRD generation (Low severity / Low risk)."
        
    return {
        "status": "processed",
        "originalText": issue_text,
        "email": user_email,
        "analysis": theme_data,
        "revenue": revenue_data,
        "prd_draft": prd_draft
    }

async def run_orchestrator(github_issues: list, user_email: str):
    processed_issues = []
    total_risk = 0

    for issue in github_issues:
        result = await process_single_issue(issue, user_email)
        processed_issues.append(result)
        
        # Ab duplicate ka ARR bhi total board revenue risk me count hoga!
        if result.get("revenue"):
            risk_amount = result["revenue"].get("revenue_at_risk", 0)
            if isinstance(risk_amount, (int, float)):
                total_risk += risk_amount
                
    return {
        "issues": processed_issues,
        "total_risk": total_risk
    }