import os
import httpx
import traceback
from typing import List, Dict, Any

class NangoEngine:
    """
    AgentOS Unified Integration Gateway (powered by Nango).
    Fetches real, normalized data (Tickets, Contacts, etc.) from dozens of SaaS apps instantly.
    """
    def __init__(self):
        # 1. Load Real Secret Key
        self.secret_key = os.environ.get("NANGO_SECRET_KEY")
        self.base_url = "https://api.nango.dev"
        self.timeout = httpx.Timeout(20.0)

    # =========================================================================
    # THE REAL UNIFIED RECORDS INGESTION
    # =========================================================================
    
    async def fetch_unified_records(self, provider: str, connection_id: str, model: str = "ticket") -> List[Dict[str, Any]]:
        print(f"🔄 [Nango Engine] Fetching unified '{model}' records from {provider} (Connection: {connection_id})...")

        if not self.secret_key:
            print("⚠️ [Nango Engine] NANGO_SECRET_KEY missing in .env! Returning empty data.")
            return []

        try:
            # 2. Hitting the Nango Sync / Records API
            # This endpoint returns data that Nango has already normalized into a standard schema
            url = f"{self.base_url}/records/{model}"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    params={
                        "connection_id": connection_id,
                        "provider_config_key": provider
                    },
                    headers={
                        "Authorization": f"Bearer {self.secret_key}",
                        "Content-Type": "application/json"
                    }
                )

                if response.status_code == 200:
                    records = response.json().get("records", [])
                    print(f"✅ [Nango Engine] Successfully fetched {len(records)} live {model}(s)!")
                    
                    # 3. Future-proofing: We can do additional AgentOS normalization here if needed
                    # but Nango usually keeps it very clean.
                    return records
                else:
                    print(f"🚨 [Nango Engine] API Error {response.status_code}: {response.text}")
                    return []

        except Exception as e:
            print(f"🚨 [Nango Engine] Exception during Nango Network Call: {e}")
            traceback.print_exc()
            return []

# Initialize a singleton instance for main.py to use
nango_connector = NangoEngine()