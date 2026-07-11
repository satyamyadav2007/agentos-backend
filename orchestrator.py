import asyncio
from agents.theme_agent import ThemeAgent
from agents.revenue_agent import revenue_agent 
from agents.prd_agent import PRDAgent  # ⚡ FIX: Class import kiya
from memory.vector_store import vector_memory
from integrations.manager import IntegrationManager
from database.graph_manager import graph_db
from agents.jira_agent import create_jira_ticket
from agents.action_engine import action_engine
from adapters.crm_aggregator import CRMAggregator

crm_tool = CRMAggregator()

# ⚡ FIX: Classes ko yahan initialize kar liya taaki functions mein asani se call ho sakein
theme_agent = ThemeAgent()
prd_agent = PRDAgent()

async def process_single_issue(issue_data: dict, user_email: str):
    issue_id = str(issue_data.get("metadata", {}).get("github_id", "unknown_id"))
    issue_text = issue_data.get("body", "") or issue_data.get("title", "")
    issue_title = issue_data.get("title", "Unknown")
    
    print(f"\n[Orchestrator] Processing Issue {issue_id}: {issue_title}")
    
    # ⚡ FIX 2: Naya CRM method use kiya aur dict extraction ko hata diya
    arr = await crm_tool.fetch_company_revenue_risk(user_email)
    base_revenue = {
        "revenue_at_risk": arr, 
        "total_company_arr": arr
    }

    # 1. DUPLICATE CHECK (Vector Memory)
    dup_check = vector_memory.check_duplicate(issue_text)
    graph_db.ingest_root_cause_node(
        bug_title=issue_title,
        user_email=user_email,
        arr_impact=arr # ⚡ FIX 3: Naya arr variable pass kiya
    )
    
    if dup_check.get("is_duplicate"):
        print(f"🔄 [Vector DB] Duplicate Alert! Matches existing root issue.")
        return {
            "status": "duplicate",
            "originalText": issue_text,
            "email": user_email,
            "analysis": {"category": "Duplicate (Aggregated)", "severity": "High", "summary": "Merged with Root Issue. Impact escalated!"},
            "revenue": base_revenue, 
            "prd_draft": "Skipped PRD generation (Duplicate issue). Escalating Root Issue priority.",
            "requires_prd": False,
            "jira_ticket_url": None,
            "auto_prd": None
        }

    print("✨ [Vector DB] Novel issue detected. Adding to memory...")
    vector_memory.add_issue(issue_id=issue_id, text=issue_text, metadata={"client": user_email})
    
    # 2. PARALLEL EXECUTION (Theme & Revenue)
    # ⚡ FIX: ThemeAgent object ka method call kiya
    theme_task = theme_agent.analyze_theme(issue_text)
    
    # ⚡ FIX 4: Revenue Agent ko correct format mein parameters pass kiye (event_data, total_arr)
    revenue_task = revenue_agent.calculate_revenue_risk(event_data=issue_data, total_arr=arr)
    
    theme_data, revenue_data = await asyncio.gather(theme_task, revenue_task)
    
    # 3. GENERATE PRD & CREATE REAL JIRA TICKET
    requires_prd = False
    jira_url = None
    auto_prd = None 
    action_result = {} # Safety init to prevent UnboundLocalError
    
    # Trigger Slack Alert for High Severity
    from agents.slack_agent import trigger_slack_alert
    await trigger_slack_alert(issue_title, base_revenue["revenue_at_risk"], revenue_data.get("risk_tier", "MEDIUM"))
    
    # Merge Predictive Oracle data into the revenue payload
    try:
        from agents.revenue_agent import enrich_predictive_risk
        advanced_revenue_data = await enrich_predictive_risk(base_revenue["total_company_arr"], revenue_data.get("severity", ""))
        revenue_data.update(advanced_revenue_data)
    except ImportError:
        pass # Handle gracefully agar predictive logic move hui ho
        
    if revenue_data.get("severity", "").lower() == "high":
        requires_prd = True
        
        # ⚡ FIX: PRDAgent class object ka method call kiya aur correct arguments pass kiye
        prd_draft = await prd_agent.generate_prd(
            text=issue_text,
            theme_data=theme_data,
            revenue_risk=revenue_data.get("revenue_at_risk", 0)
        )
        auto_prd = prd_draft

        print(f"🚀 [Orchestrator] Handing off to Execution Arm...")
        try:
            # Using the Universal Action Engine instead of hardcoded Jira
            action_result = await action_engine.execute_ticket_creation(
                issue_title=issue_title,
                prd_text=prd_draft,
                severity=revenue_data.get("severity", "")
            )
            jira_url = action_result.get("ticket_url")
            print(f"✅ [Orchestrator] Engineering pipeline complete.")
        except Exception as e:
            print(f"🚨 [Action Engine Error] Could not create ticket. Error: {str(e)[:100]}")
    else:
        prd_draft = "Skipped PRD generation (Low severity / Low risk)."
        
    # Safer extraction without relying on locals()
    story_points = action_result.get("story_points") if requires_prd else None
    target_sprint = action_result.get("sprint") if requires_prd else None

    return {
        "status": "processed",
        "originalText": issue_text,
        "email": user_email,
        "analysis": theme_data,
        "revenue": revenue_data,
        "prd_draft": prd_draft,
        "requires_prd": requires_prd,
        "jira_ticket_url": jira_url,
        "auto_prd": auto_prd,
        # Sending Sprint Planning data to the Next.js Frontend
        "sprint_plan": {
            "points": story_points,
            "sprint": target_sprint
        }
    }

from core.event_bus import event_bus
from core.models.event import UniversalEvent
from typing import List, Dict, Any

async def run_orchestrator(github_issues: List[Dict[str, Any]], user_email: str):
    """
    All 11 integrations pass their data here. (Note: keeping the parameter name as github_issues 
    so your existing connectors don't break, but it handles all data now).
    """
    print(f"\n⚙️ [Orchestrator] Formatting data from integrations for Event Bus...")
    
    events = []
    for raw_event in github_issues:
        try:
            event = UniversalEvent(**raw_event)
            events.append(event)
        except Exception as e:
            print(f"⚠️ [Orchestrator] Skipping malformed event: {e}")
            
    # Data ko Event Bus me push karo
    await event_bus.publish(events)
    
    print("✅ [Orchestrator] Data successfully handed off to the Event Bus!")