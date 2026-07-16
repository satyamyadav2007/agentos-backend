import json
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import UniversalEventRecord

class VelocityEngine:
    """Module 11: Calculates Engineering Velocity & DORA Metrics."""

    def _parse_date(self, date_str: str):
        if not date_str:
            return None
        # GitHub standard date format handling
        try:
            return datetime.strptime(date_str.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S%z")
        except ValueError:
            return None

    def calculate_metrics(self, workspace_id: str, db: Session) -> dict:
        print(f"📊 [Velocity Engine] Calculating Engineering Metrics for {workspace_id}...")

        # Fetch PRs and Issues for this workspace
        prs = db.query(UniversalEventRecord).filter(
            UniversalEventRecord.workspace_id == workspace_id,
            UniversalEventRecord.entity_type == "pull_request"
        ).all()

        issues = db.query(UniversalEventRecord).filter(
            UniversalEventRecord.workspace_id == workspace_id,
            UniversalEventRecord.entity_type == "issue"
        ).all()

        total_review_time = 0
        merged_pr_count = 0
        total_cycle_time = 0
        closed_issue_count = 0

        # 1. Calculate PR Review & Merge Time
        for pr in prs:
            meta = pr.metadata_json if isinstance(pr.metadata_json, dict) else json.loads(pr.metadata_json or "{}")
            created_at = self._parse_date(meta.get("created_at"))
            merged_at = self._parse_date(meta.get("merged_at"))

            if created_at and merged_at:
                # Review Time = PR Merged Time - PR Created Time
                review_time_hours = (merged_at - created_at).total_seconds() / 3600
                total_review_time += review_time_hours
                merged_pr_count += 1

        # 2. Calculate Issue Cycle Time (Time to resolution)
        for issue in issues:
            meta = issue.metadata_json if isinstance(issue.metadata_json, dict) else json.loads(issue.metadata_json or "{}")
            created_at = self._parse_date(meta.get("created_at"))
            closed_at = self._parse_date(meta.get("closed_at"))

            if created_at and closed_at:
                # Cycle Time = Issue Closed Time - Issue Created Time
                cycle_time_hours = (closed_at - created_at).total_seconds() / 3600
                total_cycle_time += cycle_time_hours
                closed_issue_count += 1

        # Averages
        avg_review_time = round(total_review_time / merged_pr_count, 1) if merged_pr_count > 0 else 0
        avg_cycle_time = round(total_cycle_time / closed_issue_count, 1) if closed_issue_count > 0 else 0

        return {
            "status": "success",
            "workspace_id": workspace_id,
            "metrics": {
                "avg_review_time_hours": avg_review_time,
                "avg_cycle_time_hours": avg_cycle_time,
                "prs_merged": merged_pr_count,
                "issues_resolved": closed_issue_count,
                "engineering_health": "Excellent" if avg_review_time < 48 else "Needs Improvement"
            }
        }

# Global Instance
velocity_analytics = VelocityEngine()