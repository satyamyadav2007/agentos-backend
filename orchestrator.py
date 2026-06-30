# orchestrator.py
from agents.cleaner_agent import clean_text
from agents.theme_agent import extract_theme
from agents.revenue_agent import calculate_revenue_risk
from agents.prd_agent import generate_prd # Naya import
import asyncio
from database.graph_manager import graph_db
import uuid

async def run_orchestrator(text: str, source: str, user_email: str):
    print(f"[Orchestrator] Processing data from: {user_email}")
    
    cleaned_data = await clean_text(text)
    theme_data = await extract_theme(cleaned_data)
    revenue_data = await calculate_revenue_risk(theme_data, user_email)
    
    prd_draft = None
    
    # Smart Routing: Sirf important tasks ke liye PRD banegi!
    severity = theme_data.get("severity", "").lower()
    if severity == "high" or revenue_data["revenue_at_risk"] > 10000:
        prd_draft = await generate_prd(
            text=cleaned_data, 
            theme_data=theme_data, 
            revenue_risk=revenue_data["revenue_at_risk"]
        )
        print("[Orchestrator] PRD generated successfully.")
    else:
        prd_draft = "Skipped PRD generation (Low severity / Low risk)."
async def run_orchestrator(text: str, source: str, user_email: str):
    print(f"[Orchestrator] Processing data from: {user_email}")
    
    cleaned_data = await clean_text(text)
    theme_data = await extract_theme(cleaned_data)
    revenue_data = await calculate_revenue_risk(theme_data, user_email)
    
    prd_draft = None
    
    # Smart Routing: Sirf important tasks ke liye PRD banegi!
    severity = theme_data.get("severity", "").lower()
    if severity == "high" or revenue_data["revenue_at_risk"] > 10000:
        prd_draft = await generate_prd(
            text=cleaned_data, 
            theme_data=theme_data, 
            revenue_risk=revenue_data["revenue_at_risk"]
        )
        print("[Orchestrator] PRD generated successfully.")
    else:
        prd_draft = "Skipped PRD generation (Low severity / Low risk)."
        
    # Generate unique ticket ID for the transaction
    ticket_id = f"TKT-{uuid.uuid4().hex[:6].upper()}"
    
    # 🚨 GRACEFUL DEGRADATION BLOCK
    try:
        # Push data dynamically into Company Memory Graph
        await graph_db.ingest_causal_data(
            email=user_email,
            company_arr=revenue_data["total_company_arr"],
            ticket_id=ticket_id,
            feedback_text=cleaned_data,
            theme_data=theme_data,
            current_release="v2.8"
        )
    except Exception as e:
        print(f"[Warning] Neo4j Database is offline. Skipping Graph Ingestion. Error: {e}")
    
    return {
        "original_source": source,
        "user_email": user_email,
        "analysis": theme_data,
        "revenue_impact": revenue_data,
        "prd_draft": prd_draft
    }