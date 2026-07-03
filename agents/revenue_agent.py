from integrations.manager import integration_manager

async def calculate_revenue_risk(issue_data: dict, client_id: str = "CLIENT_002"):
    """
    Analyzes bug severity and fetches real ARR from CRM to calculate revenue at risk.
    """
    print("[Revenue Agent] Calculating business impact...")
    
    # 1. CRM se asli data fetch karo
    crm_tool = integration_manager.get_integration("crm")
    client_info = await crm_tool.get_client_arr(client_id)
    
    actual_arr = client_info.get("arr", 0)
    client_name = client_info.get("name", "Unknown Client")
    
    # 2. Risk calculation logic
    severity = issue_data.get("severity", "Low")
    
    if severity.lower() in ["high", "critical"]:
        risk_amount = actual_arr
    elif severity.lower() == "medium":
        risk_amount = actual_arr * 0.5
    else:
        risk_amount = actual_arr * 0.1
        
    return {
        "client_name": client_name,
        "total_arr": actual_arr,
        "revenue_at_risk": risk_amount
    }