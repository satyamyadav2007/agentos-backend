import os
import httpx

class SlackOAuthManager:
    def __init__(self):
        self.client_id = os.getenv("SLACK_CLIENT_ID")
        self.client_secret = os.getenv("SLACK_CLIENT_SECRET")
        self.callback_url = os.getenv("SLACK_CALLBACK_URL")

    async def authenticate(self, auth_code: str) -> str:
        """Exchanges the temporary code for a permanent Bot Token."""
        print("🔐 [Slack Auth] Starting token exchange...")
        url = "https://slack.com/api/oauth.v2.access"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": auth_code,
            "redirect_uri": self.callback_url
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload)
            data = response.json()
            
            if not data.get("ok"):
                raise Exception(f"Slack Auth Failed: {data.get('error')}")
                
            bot_token = data["access_token"]
            team_name = data["team"]["name"]
            print(f"✅ [Slack Auth] Connected to Slack Workspace: {team_name}")
            
            return bot_token