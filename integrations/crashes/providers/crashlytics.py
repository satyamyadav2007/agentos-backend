import httpx
from datetime import datetime
from typing import List, Dict, Any
from .base import BaseCrashProvider
from ..models.crash import CrashModel

class CrashlyticsProvider(BaseCrashProvider):
    """Firebase Crashlytics implementation of the unified crash engine."""
    
    def __init__(self, api_key: str, organization_slug: str, project_slug: str):
        # For Crashlytics: api_key = GCP Bearer Token/Service Key, project_slug = Firebase App ID
        super().__init__(api_key, organization_slug, project_slug)
        self.firebase_app_id = project_slug
        self.base_url = f"https://firebasecrashlytics.googleapis.com/v1beta1/projects/{organization_slug}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    async def fetch_unresolved_crashes(self, limit: int = 50) -> List[CrashModel]:
        print(f"🔥 [Crashlytics Provider] Fetching fatal Android/iOS crashes...")
        # Endpoint to list fatal/non-fatal issues for a specific app
        url = f"{self.base_url}/apps/{self.firebase_app_id}/issues"
        
        # Filtering for open/unresolved issues
        params = {"filter": "issueState = OPEN", "pageSize": limit}
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                raw_issues = response.json().get("issues", [])
                
                standardized_crashes = []
                for issue in raw_issues:
                    standardized_crashes.append(
                        CrashModel(
                            id=issue.get("name").split("/")[-1], # Extracts ID from "projects/x/apps/y/issues/ID"
                            provider="crashlytics",
                            project_id=self.firebase_app_id,
                            title=issue.get("issueTitle", "App Crash"),
                            culprit=issue.get("subtitle", "Unknown File"),
                            release_version=issue.get("appVersion", "latest"),
                            user_count=int(issue.get("distinctUsers", 0)),
                            event_count=int(issue.get("crashCount", 0)),
                            first_seen=datetime.fromisoformat(issue.get("firstCrashTime", "").replace('Z', '+00:00')),
                            last_seen=datetime.fromisoformat(issue.get("lastCrashTime", "").replace('Z', '+00:00')),
                            metadata={"fatal": issue.get("fatal", True), "platform": issue.get("platform")}
                        )
                    )
                print(f"   ✅ Standardized {len(standardized_crashes)} Crashlytics issues.")
                return standardized_crashes
            except Exception as e:
                print(f"🚨 [Crashlytics Provider] Failed to fetch crashes. Ensure GCP permissions are correct. Error: {e}")
                return []

    async def fetch_crash_events(self, issue_id: str) -> Dict[str, Any]:
        pass