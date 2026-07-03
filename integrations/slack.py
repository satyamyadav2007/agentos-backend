import requests
from .base import BaseIntegration

class SlackIntegration(BaseIntegration):
    def __init__(self, webhook_url: str = None):
        # Asli app me yeh URL .env file se aayega
        self.webhook_url = webhook_url

    def fetch_data(self, **kwargs):
        # Abhi hum Slack se messages padh nahi rahe hain, sirf bhej rahe hain.
        pass

    def send_action(self, message: str):
        print(f"[Integration] Routing message to Slack...")
        
        if not self.webhook_url or self.webhook_url == "mock_url_here":
            # Agar URL nahi hai, toh terminal me mock message print karo
            print(f"🤖 [Slack Message Mock]:\n{message}\n-------------------------")
            return True
            
        payload = {"text": message}
        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code == 200:
                print("[Slack] Alert sent successfully!")
                return True
            else:
                print(f"[Slack Error] Failed to send: {response.text}")
                return False
        except Exception as e:
            print(f"[Slack Exception] {e}")
            return False