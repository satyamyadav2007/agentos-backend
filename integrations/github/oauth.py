import os
import jwt
import time
import requests

class GitHubAuthManager:
    def __init__(self):
        self.app_id = os.getenv("GITHUB_APP_ID")
        self.client_id = os.getenv("GITHUB_CLIENT_ID")
        self.client_secret = os.getenv("GITHUB_CLIENT_SECRET")
        
        # ✅ BUG 1 FIX: Render environment variable se direct PEM key uthana
        raw_key = os.getenv("GITHUB_PRIVATE_KEY")
        if raw_key:
            # ✅ Format Fix: Render ke literal \n ko actual newlines me convert karna
            self.private_key = raw_key.replace("\\n", "\n")
        else:
            print("🚨 [GitHub] GITHUB_PRIVATE_KEY environment variable missing!")
            self.private_key = None

    def generate_app_jwt(self) -> str:
        """Generates a JWT to authenticate as the GitHub App itself."""
        if not self.private_key:
            raise Exception("Cannot generate JWT: Private key is missing. Check Render Env Vars.")
            
        payload = {
            'iat': int(time.time()) - 60,      
            'exp': int(time.time()) + (10 * 60), 
            'iss': self.app_id
        }
        return jwt.encode(payload, self.private_key, algorithm='RS256')

    def get_installation_token(self, installation_id: str) -> str:
        """Exchanges the App JWT for a temporary Installation Access Token."""
        app_jwt = self.generate_app_jwt()
        headers = {
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github.v3+json"
        }
        url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
        
        # ✅ BUG 3 FIX: requests.post me 30 seconds ka timeout add kiya
        response = requests.post(url, headers=headers, timeout=30)
        
        # ✅ BUG 4 FIX: 401/403 aane par exact text print karna taaki debug asaan ho
        if response.status_code != 201:
            print(f"🚨 [GitHub API Error]: {response.status_code} - {response.text}")
            raise Exception(f"Failed to get installation token: {response.text}")
            
        return response.json()["token"]