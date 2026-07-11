import httpx
from typing import Dict, Any

class CrashesAuthManager:
    """Validates API Keys for Crash Monitoring Providers."""
    
    async def validate_sentry(self, api_key: str, org_slug: str, project_slug: str) -> bool:
        print("🔐 [Crashes Auth] Validating Sentry credentials...")
        url = f"https://sentry.io/api/0/projects/{org_slug}/{project_slug}/"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            return response.status_code == 200

    async def validate_crashlytics(self, api_key: str, org_slug: str, app_id: str) -> bool:
        print("🔐 [Crashes Auth] Validating Firebase Crashlytics credentials...")
        # A simple check to ensure the token has access to the Firebase App
        url = f"https://firebasecrashlytics.googleapis.com/v1beta1/projects/{org_slug}/apps/{app_id}/issues?pageSize=1"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            return response.status_code == 200

    async def validate_credentials(self, provider: str, api_key: str, org_slug: str, project_slug: str) -> bool:
        if provider == "sentry":
            return await self.validate_sentry(api_key, org_slug, project_slug)
        elif provider == "crashlytics":
            return await self.validate_crashlytics(api_key, org_slug, project_slug)
        else:
            raise ValueError(f"Unsupported Crash Provider: {provider}")