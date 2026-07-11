from typing import Dict, Any
from .models.crash import CrashModel

class CrashNormalizer:
    
    @staticmethod
    def normalize_crash(crash: CrashModel) -> Dict[str, Any]:
        """Converts ANY crash event (Sentry/Crashlytics) into an AgentOS UniversalEvent."""
        
        # Determine severity based on AI Heuristics
        severity = "Critical" if crash.is_critical else "Medium"

        return {
            "source": "crashes",
            "provider": crash.provider,
            "entity_type": "crash",
            "repository": crash.project_id, 
            "title": f"Crash: {crash.title}",
            "description": f"Culprit: {crash.culprit} | Release: {crash.release_version} | Affected Events: {crash.event_count}",
            "author": "System_Monitor",
            "severity": severity,
            "timestamp": crash.last_seen.isoformat(),
            "metadata": {
                "crash_id": crash.id,
                "affected_users_approx": crash.user_count,
                "environment": crash.environment
            },
            # THIS IS THE MOAT: Neo4j will map this release_version to a GitHub Commit & Jira Sprint!
            "linked_entities": [] 
        }