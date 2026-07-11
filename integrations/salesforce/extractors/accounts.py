from typing import List
from integrations.salesforce.models.account import SalesforceAccountModel

class SalesforceAccountExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_key_accounts(self) -> List[SalesforceAccountModel]:
        print("🏢 [Salesforce Extractor] Querying Enterprise Accounts & ARR...")
        # SOQL to get crucial revenue data
        soql = """
            SELECT Id, Name, Industry, AnnualRevenue, Type, CreatedDate, LastModifiedDate 
            FROM Account 
            WHERE Type = 'Customer' OR AnnualRevenue > 0
            ORDER BY AnnualRevenue DESC NULLS LAST
            LIMIT 200
        """
        try:
            raw_data = await self.client.query(soql)
            records = raw_data.get("records", [])
            
            # Map Salesforce fields to Pydantic Model (converting CamelCase to snake_case mapping implicitly/explicitly)
            accounts = []
            for r in records:
                accounts.append(SalesforceAccountModel(
                    id=r.get("Id"),
                    name=r.get("Name"),
                    industry=r.get("Industry"),
                    annual_revenue=r.get("AnnualRevenue"),
                    type=r.get("Type"),
                    created_date=r.get("CreatedDate"),
                    last_modified_date=r.get("LastModifiedDate")
                ))
            print(f"   ✅ Extracted {len(accounts)} Revenue Accounts.")
            return accounts
        except Exception as e:
            print(f"🚨 [Salesforce Extractor] Failed to fetch accounts: {e}")
            return []