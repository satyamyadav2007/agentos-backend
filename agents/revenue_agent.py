from typing import Dict, Any

class RevenueAgent:
    def __init__(self):
        print("🧠 [Revenue Agent] Initialized. Ready to calculate financial impact.")

    async def calculate_revenue_risk(self, event_data: Dict[str, Any], total_arr: int) -> Dict[str, Any]:
        """
        Calculates the ARR at risk based on the event (issue/PR) severity and the company's total ARR.
        No direct CRM calls here - Orchestrator provides the 'total_arr' to keep architecture clean.
        """
        # 1. Extract context from the UniversalEvent (GitHub Issue, Zendesk Ticket, etc.)
        severity = event_data.get("severity", "Low").lower()
        title = event_data.get("title", "").lower()
        description = event_data.get("description", "").lower()

        # 2. Baseline risk multipliers based on severity
        # (This is where your AI model or static rules decide the base risk)
        risk_multipliers = {
            "critical": 0.40,  # 40% of ARR at risk (e.g., major system outage)
            "high": 0.15,      # 15% of ARR at risk
            "medium": 0.05,    # 5% of ARR at risk
            "low": 0.01,
            "unknown": 0.00
        }

        multiplier = risk_multipliers.get(severity, 0.00)

        # 3. Contextual Keyword Adjustments (AI Logic Proxy)
        # Check if the issue title/description mentions revenue-critical paths
        text_to_analyze = f"{title} {description}"
        
        if any(word in text_to_analyze for word in ["billing", "payment", "checkout", "stripe", "invoice"]):
            multiplier += 0.20  # Additional 20% risk for payment gateways down
        elif any(word in text_to_analyze for word in ["login", "auth", "sso", "password"]):
            multiplier += 0.10  # Customers can't access the app
        elif any(word in text_to_analyze for word in ["data loss", "gdpr", "security", "leak"]):
            multiplier += 0.30  # High churn risk due to trust loss

        # 4. Cap the multiplier at 100% (Can't lose more than 100% ARR)
        multiplier = min(multiplier, 1.0)

        # 5. Calculate actual dollar amounts
        calculated_risk_amount = int(total_arr * multiplier)

        # Determine risk tier for dashboard color coding (Red, Yellow, Green)
        if multiplier >= 0.30:
            risk_tier = "CRITICAL"
        elif multiplier >= 0.10:
            risk_tier = "HIGH"
        elif multiplier > 0:
            risk_tier = "MEDIUM"
        else:
            risk_tier = "LOW"

        # Return the clean, calculated insight to the Orchestrator
        return {
            "total_company_arr": total_arr,
            "revenue_at_risk": calculated_risk_amount,
            "risk_percentage": round(multiplier * 100, 2),
            "risk_tier": risk_tier,
            "reasoning": f"Calculated based on {severity.upper()} severity and contextual keywords."
        }

# Global instance for orchestrator to import
revenue_agent = RevenueAgent()