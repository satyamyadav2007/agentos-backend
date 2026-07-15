import os
import httpx

class ZendeskAuthManager:
    """Handles Zendesk OAuth 2.0 flow."""
    
    def __init__(self):
        self.client_id = os.getenv("ZENDESK_CLIENT_ID")
        self.client_secret = os.getenv("ZENDESK_CLIENT_SECRET")
        self.redirect_uri = os.getenv("ZENDESK_REDIRECT_URI", "https://agentos-frontend-azure.vercel.app/onboarding/integrations")

    async def authenticate(self, auth_code: str, subdomain: str) -> str:
        """Exchanges the temporary code for an Access Token."""
        print(f"🔐 [Zendesk Auth] Exchanging token for subdomain: {subdomain}.zendesk.com...")
        
        url = f"https://{subdomain}.zendesk.com/oauth/tokens"
        payload = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "scope": "read write"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            data = response.json()
            
            if "error" in data:
                raise Exception(f"Zendesk Auth Failed: {data.get('error_description', data.get('error'))}")
                
            print("✅ [Zendesk Auth] Connection successful!")
            return data["access_token"]