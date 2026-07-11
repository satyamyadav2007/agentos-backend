import os
import httpx

class IntercomOAuthManager:
    """Handles Intercom OAuth 2.0 flow."""
    
    def __init__(self):
        self.client_id = os.getenv("INTERCOM_CLIENT_ID")
        self.client_secret = os.getenv("INTERCOM_CLIENT_SECRET")

    async def authenticate(self, auth_code: str) -> str:
        """Exchanges the temporary code for an Intercom Access Token."""
        print("🔐 [Intercom Auth] Exchanging auth code for access token...")
        
        url = "https://api.intercom.io/auth/eagle/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": auth_code
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            data = response.json()
            
            if "token" not in data:
                raise Exception(f"Intercom Auth Failed: {data.get('error_message', 'Unknown Error')}")
                
            print("✅ [Intercom Auth] Connection successful!")
            return data["token"]