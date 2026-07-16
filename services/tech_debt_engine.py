import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from database.models import UniversalEventRecord

class TechDebtEngine:
    """Module 12: Analyzes system for Technical Debt (Old Bugs, Risk Areas)."""

    def _parse_date(self, date_str: str):
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S%z")
        except ValueError:
            return None

    def analyze_debt(self, workspace_id: str, db: Session) -> dict:
        print(f"🧹 [Tech Debt Engine] Scanning for technical debt in {workspace_id}...")

        # 1. Fetch Issues to find Stagnant/Old Bugs
        issues = db.query(UniversalEventRecord).filter(
            UniversalEventRecord.workspace_id == workspace_id,
            UniversalEventRecord.entity_type == "issue"
        ).all()

        old_bugs = []
        now = datetime.now(timezone.utc)

        for issue in issues:
            meta = issue.metadata_json if isinstance(issue.metadata_json, dict) else json.loads(issue.metadata_json or "{}")
            state = meta.get("state", "open")
            
            # Agar issue open hai, toh uski age check karo
            if state == "open":
                created_at = self._parse_date(meta.get("created_at"))
                if created_at:
                    age_in_days = (now - created_at).days
                    if age_in_days > 90: # 3 mahine se zyada purana bug
                        old_bugs.append({
                            "title": issue.title,
                            "age_days": age_in_days,
                            "severity": issue.severity,
                            "repository": issue.repository
                        })

        # Sort bugs by age (sabse purane bugs top par)
        old_bugs = sorted(old_bugs, key=lambda x: x["age_days"], reverse=True)

        # 2. Tech Debt Score Calculation (Heuristic AI Rule)
        # Maan lo har old bug 5 points ka tech debt create karta hai
        debt_score = min(100, len(old_bugs) * 5) 
        
        health_status = "Critical" if debt_score > 70 else "Warning" if debt_score > 30 else "Healthy"

        return {
            "status": "success",
            "workspace_id": workspace_id,
            "metrics": {
                "tech_debt_score": debt_score,
                "health_status": health_status,
                "stagnant_bugs_count": len(old_bugs),
                "oldest_bugs": old_bugs[:5] # Frontend dashboard ke liye top 5 oldest bugs
            }
        }

# Global Instance
tech_debt_engine = TechDebtEngine()