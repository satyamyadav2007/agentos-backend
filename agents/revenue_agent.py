# agents/revenue_agent.py

# Ek dummy CRM (Customer Relationship Management) database for MVP
MOCK_CRM = {
    "enterprise.com": 150000, # $150k ARR
    "netflix.com": 500000,    # $500k ARR
    "startup.io": 12000,      # $12k ARR
    "gmail.com": 0            # Free users (Zero ARR)
}

async def calculate_revenue_risk(theme_data: dict, user_email: str) -> dict:
    # Extract domain from email (e.g., satya@netflix.com -> netflix.com)
    domain = user_email.split("@")[-1].lower() if "@" in user_email else "unknown"
    
    # Get company ARR from our Mock CRM (default to $1000 if company not found)
    company_arr = MOCK_CRM.get(domain, 1000)
    
    category = theme_data.get("category", "").lower()
    severity = theme_data.get("severity", "").lower()
    
    risk_percentage = 0.0
    
    # AI-driven Revenue Risk Logic
    if category == "churn risk" or (category == "bug" and severity == "high"):
        risk_percentage = 1.0  # 100% ARR at risk
    elif category == "bug" and severity == "medium":
        risk_percentage = 0.5  # 50% ARR at risk
    elif category == "feature request" and severity == "high":
        risk_percentage = 0.2  # 20% ARR at risk (competitor might steal them)
    elif category == "pricing":
        risk_percentage = 0.3  # 30% ARR at risk
        
    revenue_at_risk = int(company_arr * risk_percentage)
    
    return {
        "company_domain": domain,
        "total_company_arr": company_arr,
        "risk_percentage": risk_percentage * 100,
        "revenue_at_risk": revenue_at_risk
    }