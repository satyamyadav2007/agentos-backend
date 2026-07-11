import httpx
from typing import Dict, Any

class AnalyticsAuthManager:
    """Validates API Keys/Tokens for different Analytics Providers."""
    
    async def validate_posthog(self, api_key: str, project_id: str, host: str = "https://app.posthog.com") -> bool:
        print("🔐 [Analytics Auth] Validating PostHog credentials...")
        url = f"{host}/api/projects/{project_id}/"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            return response.status_code == 200
    async def validate_mixpanel(self, api_key: str, project_id: str) -> bool:
        print("🔐 [Analytics Auth] Validating Mixpanel credentials...")
        import base64
        auth_string = f"{api_key}:"
        headers = {"Authorization": f"Basic {base64.b64encode(auth_string.encode()).decode()}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get("https://mixpanel.com/api/app/me", headers=headers)
            return response.status_code == 200

    async def validate_amplitude(self, api_key: str, project_id: str) -> bool:
        print("🔐 [Analytics Auth] Validating Amplitude credentials...")
        import base64
        headers = {"Authorization": f"Basic {base64.b64encode(api_key.encode()).decode()}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get("https://amplitude.com/api/2/projects", headers=headers)
            return response.status_code == 200

    async def validate_credentials(self, provider: str, api_key: str, project_id: str, **kwargs) -> bool:
        if provider == "posthog":
            return await self.validate_posthog(api_key, project_id)
        elif provider == "mixpanel":
            return await self.validate_mixpanel(api_key, project_id)
        elif provider == "amplitude":
            return await self.validate_amplitude(api_key, project_id)
        else:
            raise ValueError(f"Unsupported Analytics Provider: {provider}")        

    async def validate_credentials(self, provider: str, api_key: str, project_id: str, **kwargs) -> bool:
        if provider == "posthog":
            return await self.validate_posthog(api_key, project_id, kwargs.get("host", "https://app.posthog.com"))
        elif provider == "mixpanel":
            # Add Mixpanel validation logic later
            return True
        elif provider == "amplitude":
            # Add Amplitude validation logic later
            return True
        else:
            raise ValueError(f"Unsupported Analytics Provider: {provider}")