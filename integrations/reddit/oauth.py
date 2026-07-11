import os
import httpx
import base64

class RedditOAuthManager:
    """Handles Reddit OAuth 2.0 flow."""
    
    def __init__(self):
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.redirect_uri = os.getenv("REDDIT_REDIRECT_URI", "https://agentos-frontend-azure.vercel.app/onboarding/integrations")

    async def authenticate(self, auth_code: str) -> str:
        """Exchanges the temporary code for a Reddit Access Token."""
        print("🔐 [Reddit Auth] Exchanging auth code for access token...")
        
        url = "https://www.reddit.com/api/v1/access_token"
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": self.redirect_uri
        }
        
        # Reddit requires Basic Auth for token exchange
        auth_string = f"{self.client_id}:{self.client_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "AgentOS Intelligence Engine/1.0.0"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data, headers=headers)
            token_data = response.json()
            
            if "error" in token_data:
                raise Exception(f"Reddit Auth Failed: {token_data.get('error_description', token_data.get('error'))}")
                
            print("✅ [Reddit Auth] Connection successful!")
            return token_data["access_token"]