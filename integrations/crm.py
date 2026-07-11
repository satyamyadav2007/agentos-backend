import traceback
from adapters.crm_aggregator import crm_engine


class CRMIntegration:
    """
    AgentOS Enterprise CRM Integration

    Single Source of Truth:
        crm_aggregator.py
    """

    def __init__(self):
        print("🟢 [CRM Integration] Enterprise Mode Initialized.")

    async def get_revenue(self, user_email: str) -> int:
        """
        Returns the real ARR for the authenticated Clerk user.
        """

        if not user_email:
            print("⚠️ Missing authenticated user email.")
            return 0

        try:
            return await crm_engine.fetch_company_revenue_risk(user_email)

        except Exception as e:
            print(f"🚨 CRM Integration Error: {e}")
            traceback.print_exc()
            return 0

    # Backward compatibility
    async def get_client_arr(self, user_email: str) -> dict:
        """
        Legacy wrapper used by older modules.
        """

        arr = await self.get_revenue(user_email)

        return {
            "arr": arr,
            "tier": "Unknown" if arr == 0 else "Connected"
        }


crm_integration = CRMIntegration()