from typing import Dict, Any, List
from datetime import datetime, timezone
import dateutil.parser

class JiraWorkflowIntelligence:
    """
    AgentOS Workflow & Engineering Intelligence Service.
    Detects process bottlenecks, slow review queues, and QA delays.
    """

    @staticmethod
    def analyze_workflow_bottlenecks(issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Module 7: Workflow Intelligence
        Analyzes issue distribution across statuses to find where the flow is choking.
        """
        print("🔄 [AgentOS AI] Mapping Workflow Bottlenecks...")
        
        status_counts = {}
        for issue in issues:
            status = issue.get("metadata", {}).get("status", "Unknown").title()
            status_counts[status] = status_counts.get(status, 0) + 1
            
        # Identify the biggest bottleneck (excluding 'Done' or 'Closed' or 'To Do')
        active_statuses = {k: v for k, v in status_counts.items() if k not in ["Done", "Closed", "Resolved", "To Do", "Backlog"]}
        
        bottleneck_stage = "None"
        max_issues = 0
        recommendation = "Workflow is smooth."
        
        if active_statuses:
            bottleneck_stage = max(active_statuses, key=active_statuses.get)
            max_issues = active_statuses[bottleneck_stage]
            
            # Smart Recommendations based on the choked stage
            if "Review" in bottleneck_stage or "PR" in bottleneck_stage:
                recommendation = "Increase Code Review capacity or assign dedicated reviewers."
            elif "Test" in bottleneck_stage or "QA" in bottleneck_stage:
                recommendation = "Increase QA Capacity or automate regression testing."
            elif "Progress" in bottleneck_stage:
                recommendation = "Limit WIP (Work In Progress) to avoid context switching."

        return {
            "module": "workflow_intelligence",
            "current_status_distribution": status_counts,
            "detected_bottleneck": {
                "stage": bottleneck_stage,
                "stuck_issues_count": max_issues,
                "recommendation": recommendation
            }
        }

    @staticmethod
    def detect_engineering_bottlenecks(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Module 9: Engineering Bottleneck Detection
        Measures simulated 'Average Delay' and provides actionable insights.
        """
        print("🚧 [AgentOS AI] Detecting Engineering Bottlenecks...")
        
        bottlenecks = []
        now = datetime.now(timezone.utc)
        
        # We will look for issues that are currently 'In Progress' or 'Review' and check their age
        delayed_issues = []
        for issue in issues:
            status = issue.get("metadata", {}).get("status", "").lower()
            if status in ["done", "closed", "resolved", "to do", "backlog"]:
                continue
                
            updated_at_str = issue.get("timestamp") # Fallback to created_at if updated_at is missing
            if not updated_at_str:
                continue
                
            try:
                # Parse timestamp and calculate days since last update
                updated_dt = dateutil.parser.isoparse(updated_at_str)
                if updated_dt.tzinfo is None:
                    updated_dt = updated_dt.replace(tzinfo=timezone.utc)
                    
                days_stuck = (now - updated_dt).days
                if days_stuck > 3: # Anything untouched for > 3 days is a potential delay
                    delayed_issues.append({"issue": issue, "days": days_stuck, "status": status})
            except Exception:
                pass
                
        # Group by status to identify team-level delays
        if delayed_issues:
            qa_delays = [d for d in delayed_issues if "test" in d["status"] or "qa" in d["status"]]
            review_delays = [d for d in delayed_issues if "review" in d["status"]]
            
            if review_delays:
                avg_delay = sum(d["days"] for d in review_delays) / len(review_delays)
                bottlenecks.append({
                    "team": "Backend/Frontend",
                    "average_delay": f"{int(avg_delay)} Days",
                    "reason": "Review Queue is piling up",
                    "suggested_action": "Assign Additional Reviewer immediately."
                })
                
            if qa_delays:
                avg_delay = sum(d["days"] for d in qa_delays) / len(qa_delays)
                bottlenecks.append({
                    "team": "QA Team",
                    "average_delay": f"{int(avg_delay)} Days",
                    "reason": "Testing backlog",
                    "suggested_action": "Automate critical flows or shift QA left."
                })

        # Fallback if no specific delays are found but we have generic stuck issues
        if not bottlenecks and delayed_issues:
             bottlenecks.append({
                 "team": "General Engineering",
                 "average_delay": f"{int(delayed_issues[0]['days'])} Days",
                 "reason": "Tasks untouched in active sprint",
                 "suggested_action": "Run a standup check-in to clear blockers."
             })

        return bottlenecks