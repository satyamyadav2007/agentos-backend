import os
import httpx

class HubSpotOAuthManager:
    """Handles HubSpot OAuth 2.0 flow."""
    
    def __init__(self):
        self.client_id = os.getenv("HUBSPOT_CLIENT_ID")
        self.client_secret = os.getenv("HUBSPOT_CLIENT_SECRET")
        self.redirect_uri = os.getenv("HUBSPOT_REDIRECT_URI", "https://agentos-frontend-azure.vercel.app/onboarding/integrations")

    async def authenticate(self, auth_code: str) -> str:
        """Exchanges the temporary code for a HubSpot Access Token."""
        print("🔐 [HubSpot Auth] Exchanging auth code for access token...")
        
        url = "https://api.hubapi.com/oauth/v1/token"
        payload = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": auth_code
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload, headers=headers)
            data = response.json()
            
            if "status" in data and data["status"] == "error":
                raise Exception(f"HubSpot Auth Failed: {data.get('message')}")
                
            print("✅ [HubSpot Auth] Connection successful!")
            return data["access_token"]