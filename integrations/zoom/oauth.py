import os
import httpx
import base64

class ZoomAuthManager:
    """Handles Zoom Server-to-Server OAuth flow for Enterprise accounts."""
    
    def __init__(self):
        self.client_id = os.getenv("ZOOM_CLIENT_ID")
        self.client_secret = os.getenv("ZOOM_CLIENT_SECRET")
        self.account_id = os.getenv("ZOOM_ACCOUNT_ID")

    async def get_access_token(self) -> str:
        """Generates a Zoom access token using Server-to-Server credentials."""
        print("🔐 [Zoom Auth] Requesting Server-to-Server OAuth token...")
        
        url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={self.account_id}"
        
        # Zoom requires Basic Auth header with base64 encoded client_id:client_secret
        auth_string = f"{self.client_id}:{self.client_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers)
            data = response.json()
            
            if "access_token" not in data:
                raise Exception(f"Zoom Auth Failed: {data.get('reason', 'Unknown Error')}")
                
            print("✅ [Zoom Auth] Token generated successfully!")
            return data["access_token"]