import os
import httpx
import traceback
from typing import Optional

# Future DB import
# from database.graph_manager import graph_db


class CRMAggregator:  # ⚡ FIX: Renamed from CRMEngine to match orchestrator.py
    """
    AgentOS CRM Aggregator

    Priority

    1. Nango Connected CRM
    2. Native HubSpot
    3. Workspace Database
    4. Return 0
    """

    def __init__(self):

        # ---------- Nango ----------
        self.nango_secret = os.getenv("NANGO_SECRET_KEY")
        self.nango_base_url = "https://api.nango.dev"

        # ---------- Native HubSpot ----------
        self.hubspot_token = os.getenv("HUBSPOT_ACCESS_TOKEN")
        self.hubspot_company_api = (
            "https://api.hubapi.com/crm/v3/objects/companies"
        )

        # ---------- Timeout ----------
        self.timeout = httpx.Timeout(20.0)

    ###########################################################################
    # PUBLIC METHOD
    ###########################################################################

    async def fetch_company_revenue_risk(self, user_email: str) -> int:

        print(f"\n🔍 [CRM] Lookup Started : {user_email}")

        if not user_email:
            return 0

        # ==============================================================
        # 1. NANGO (PRIMARY)
        # ==============================================================
        arr = await self._fetch_from_nango(user_email)

        if arr is not None:
            print(f"✅ [CRM] Revenue received from Nango: ${arr}")
            return arr

        # ==============================================================
        # 2. HUBSPOT DIRECT (OPTIONAL FALLBACK)
        # ==============================================================
        arr = await self._fetch_from_hubspot(user_email)

        if arr is not None:
            print(f"✅ [CRM] Revenue received from Native HubSpot: ${arr}")
            return arr

        # ==============================================================
        # 3. DATABASE
        # ==============================================================
        arr = await self._fetch_from_database(user_email)

        if arr is not None:
            print(f"✅ [CRM] Revenue received from Workspace DB: ${arr}")
            return arr

        # ==============================================================
        # 4. NOTHING FOUND
        # ==============================================================
        print("⚠️ [CRM] No CRM Connected. Defaulting to 0 ARR.")
        return 0


    ###########################################################################
    # NANGO (COMPLETED PROXY IMPLEMENTATION)
    ###########################################################################

    async def _fetch_from_nango(
        self,
        user_email: str,
    ) -> Optional[int]:

        if not self.nango_secret:
            return None

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                
                # 1. Check which CRM is connected
                # ⚡ NOTE: Verify if Nango API requires '/connections' or '/connection'
                conn_response = await client.get(
                    f"{self.nango_base_url}/connection",
                    params={"connection_id": user_email},
                    headers={"Authorization": f"Bearer {self.nango_secret}"},
                )

                if conn_response.status_code != 200:
                    return None

                connection = conn_response.json()
                provider = connection.get("provider_config_key")
                print(f"🔗 [Nango] Connected CRM Provider: {provider}")

                domain = user_email.split("@")[-1]

                # ==============================================================
                # 2A. PROXY TO HUBSPOT
                # ==============================================================
                if provider == "hubspot":
                    print(f"🔄 [Nango] Proxying request to HubSpot for domain: {domain}")
                    hubspot_proxy_res = await client.get(
                        f"{self.nango_base_url}/proxy/hubspot/crm/v3/objects/companies",
                        headers={
                            "Authorization": f"Bearer {self.nango_secret}",
                            "Nango-Connection-Id": user_email
                        },
                        params={
                            "domain": domain,
                            "properties": "annualrevenue,total_revenue"
                        }
                    )
                    
                    if hubspot_proxy_res.status_code == 200:
                        companies = hubspot_proxy_res.json().get("results", [])
                        if companies:
                            props = companies[0].get("properties", {})
                            revenue = props.get("annualrevenue") or props.get("total_revenue")
                            if revenue:
                                return int(float(revenue))

                # ==============================================================
                # 2B. PROXY TO SALESFORCE
                # ==============================================================
                elif provider == "salesforce":
                    print(f"🔄 [Nango] Proxying request to Salesforce for domain: {domain}")
                    # SOQL Query to find the Account by domain/website
                    query = f"SELECT AnnualRevenue FROM Account WHERE Website LIKE '%{domain}%' LIMIT 1"
                    
                    sf_proxy_res = await client.get(
                        f"{self.nango_base_url}/proxy/salesforce/services/data/v58.0/query/",
                        headers={
                            "Authorization": f"Bearer {self.nango_secret}",
                            "Nango-Connection-Id": user_email
                        },
                        params={"q": query}
                    )
                    
                    if sf_proxy_res.status_code == 200:
                        records = sf_proxy_res.json().get("records", [])
                        if records:
                            revenue = records[0].get("AnnualRevenue")
                            if revenue:
                                return int(float(revenue))

                # ==============================================================
                # 2C. UNMAPPED PROVIDER
                # ==============================================================
                else:
                    print(f"⚠️ [Nango] Provider '{provider}' revenue logic not mapped yet.")
                    return None

        except Exception as e:
            print(f"🚨 [Nango Engine Error]: {str(e)}")
            traceback.print_exc()

        return None
        

    ###########################################################################
    # HUBSPOT
    ###########################################################################

    async def _fetch_from_hubspot(
        self,
        user_email: str,
    ) -> Optional[int]:

        if not self.hubspot_token:
            return None

        try:
            domain = user_email.split("@")[-1]
            headers = {
                "Authorization": f"Bearer {self.hubspot_token}"
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.hubspot_company_api,
                    headers=headers,
                    params={
                        "domain": domain
                    },
                )

                if response.status_code != 200:
                    return None

                data = response.json()
                companies = data.get("results", [])

                if not companies:
                    return None

                properties = companies[0].get("properties", {})
                revenue = (
                    properties.get("annualrevenue")
                    or properties.get("total_revenue")
                )

                if revenue:
                    return int(float(revenue))

        except Exception:
            traceback.print_exc()

        return None

    ###########################################################################
    # DATABASE
    ###########################################################################

    async def _fetch_from_database(
        self,
        user_email: str,
    ) -> Optional[int]:

        try:
            # ############################################################
            # Replace with Neo4j / Postgres
            #
            # workspace = graph_db.get_workspace(user_email)
            #
            # ############################################################

            workspace = None

            if not workspace:
                return None

            revenue = workspace.get("stated_arr")

            if revenue:
                return int(revenue)

        except Exception:
            traceback.print_exc()

        return None

# ⚡ FIX: Global instance name updated to match the class and standard usage
crm_engine = CRMAggregator()