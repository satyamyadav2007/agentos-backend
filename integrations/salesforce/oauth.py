import os
import httpx

class SalesforceOAuthManager:
    """Handles Salesforce OAuth 2.0 flow for Connected Apps."""
    
    def __init__(self):
        self.client_id = os.getenv("SALESFORCE_CLIENT_ID")
        self.client_secret = os.getenv("SALESFORCE_CLIENT_SECRET")
        # Ensure this matches your Vercel URL exactly
        self.redirect_uri = os.getenv("SALESFORCE_REDIRECT_URI", "https://agentos-frontend-azure.vercel.app/onboarding/integrations")

    async def authenticate(self, auth_code: str) -> tuple[str, str]:
        """Exchanges the temporary code for an Access Token and Instance URL."""
        print("🔐 [Salesforce Auth] Exchanging auth code for access token...")
        
        # Defaulting to production/developer login. For sandboxes, it would be test.salesforce.com
        url = "https://login.salesforce.com/services/oauth2/token"
        payload = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload)
            data = response.json()
            
            if "error" in data:
                raise Exception(f"Salesforce Auth Failed: {data.get('error_description', data.get('error'))}")
                
            print(f"✅ [Salesforce Auth] Connected to instance: {data['instance_url']}")
            return data["access_token"], data["instance_url"]