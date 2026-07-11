import os
import jwt
import time
import requests

class GitHubAuthManager:
    def __init__(self):
        self.app_id = os.getenv("GITHUB_APP_ID")
        self.client_id = os.getenv("GITHUB_CLIENT_ID")
        self.client_secret = os.getenv("GITHUB_CLIENT_SECRET")
        self.key_path = os.getenv("GITHUB_PRIVATE_KEY_PATH", "./github_key.pem")
        
        try:
            with open(self.key_path, 'r') as f:
                self.private_key = f.read()
        except FileNotFoundError:
            print("⚠️ [GitHub] Private key file not found. Auth will fail.")
            self.private_key = None

    def generate_app_jwt(self) -> str:
        """Generates a JWT to authenticate as the GitHub App itself."""
        payload = {
            'iat': int(time.time()) - 60,      # Issued at time
            'exp': int(time.time()) + (10 * 60), # JWT expiration time (10 minute max)
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
        
        response = requests.post(url, headers=headers)
        if response.status_code != 201:
            raise Exception(f"Failed to get installation token: {response.text}")
            
        return response.json()["token"]