import os
import httpx

class DiscordOAuthManager:
    """Handles Discord OAuth 2.0 flow."""
    
    def __init__(self):
        self.client_id = os.getenv("DISCORD_CLIENT_ID")
        self.client_secret = os.getenv("DISCORD_CLIENT_SECRET")
        self.redirect_uri = os.getenv("DISCORD_REDIRECT_URI", "https://agentos-frontend-azure.vercel.app/onboarding/integrations")

    async def authenticate(self, auth_code: str) -> str:
        """Exchanges auth code for a Discord Access Token."""
        print("🔐 [Discord Auth] Exchanging auth code for access token...")
        
        url = "https://discord.com/api/oauth2/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": self.redirect_uri
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data, headers=headers)
            token_data = response.json()
            
            if "error" in token_data:
                raise Exception(f"Discord Auth Failed: {token_data.get('error_description', 'Unknown Error')}")
                
            print("✅ [Discord Auth] Connection successful!")
            return token_data["access_token"]