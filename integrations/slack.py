import requests
from .base import BaseConnector


class SlackIntegration(BaseConnector):
    def __init__(self, webhook_url: str = None):
        # Production me .env se aayega
        self.webhook_url = webhook_url

    # =====================================================
    # Required BaseConnector Methods
    # =====================================================

    def connect(self):
        print("[Slack] Connecting...")
        return True

    def disconnect(self):
        print("[Slack] Disconnecting...")
        return True

    def normalize(self, data):
        """
        Normalize Slack payload into AgentOS format.
        """
        return data

    def sync(self, **kwargs):
        """
        Future:
        - Fetch Channels
        - Fetch Messages
        - Fetch Threads
        """
        print("[Slack] Sync started...")
        return []

    def webhook(self, payload):
        """
        Handle incoming Slack webhook events.
        """
        print("[Slack] Webhook received.")
        return {
            "status": "received",
            "payload": payload,
        }

    # =====================================================
    # Existing Methods
    # =====================================================

    def fetch_data(self, **kwargs):
        """
        Future implementation:
        Read Slack messages.
        """
        return []

    def send_action(self, message: str):
        print("[Integration] Routing message to Slack...")

        # ---------------- MOCK MODE ----------------
        if (
            not self.webhook_url
            or self.webhook_url == "mock_url_here"
        ):
            print(
                f"""
🤖 [Slack Mock Message]

{message}

------------------------------------
"""
            )
            return True

        payload = {
            "text": message
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10,
            )

            if response.status_code == 200:
                print("[Slack] Alert sent successfully!")
                return True

            print(f"[Slack Error] {response.text}")
            return False

        except Exception as e:
            print(f"[Slack Exception] {e}")
            return False