from typing import Dict, Any, List

class JiraAnalysisService:
    """
    AgentOS AI Brain: Analyzes normalized Jira data to generate actionable intelligence.
    Acts as the preprocessing engine before handing data to the LLM.
    """

    def __init__(self):
        print("🧠 [Analysis Service] Initializing Jira Intelligence Modules...")

    def detect_bottlenecks(self, normalized_issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Module 9: Engineering Bottleneck Detection.
        Identifies workflow jams (e.g., too many tickets in 'Code Review').
        """
        print("🔍 [AgentOS Brain] Analyzing workflows for bottlenecks...")
        bottlenecks = []
        
        # Tally issues by their current status
        status_counts = {}
        for issue in normalized_issues:
            # Safely fetch status from the normalized metadata
            status = issue.get("metadata", {}).get("status", "Unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        # Heuristic: If more than 5 issues are stuck in Review/QA, it's a bottleneck
        jam_threshold = 5 
        jam_statuses = ["in review", "code review", "qa", "testing", "blocked"]

        for status, count in status_counts.items():
            if status.lower() in jam_statuses and count >= jam_threshold:
                bottlenecks.append({
                    "type": "workflow_jam",
                    "severity": "High" if count > (jam_threshold * 2) else "Medium",
                    "location": status,
                    "impact": f"{count} tickets are currently piling up in '{status}'.",
                    "suggested_action": f"Temporarily reassign engineers to clear the '{status}' queue."
                })
                
        return bottlenecks

    def predict_sprint_risk(self, normalized_sprints: List[Dict[str, Any]], normalized_issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Module 16: Sprint Failure Risk Prediction.
        Calculates the probability of missing the sprint deadline.
        """
        print("⚠️ [AgentOS Brain] Calculating active Sprint Risk Scores...")
        
        active_sprints = [s for s in normalized_sprints if s.get("metadata", {}).get("status") == "active"]
        
        if not active_sprints:
            return {"status": "safe", "risk_score": 0, "reason": "No active sprints detected."}

        # For MVP, we calculate risk based on the density of Critical/High severity bugs vs standard stories
        critical_issues = [i for i in normalized_issues if i.get("severity") == "Critical"]
        high_issues = [i for i in normalized_issues if i.get("severity") == "High"]
        
        # Basic Risk Algorithm (Can be upgraded with ML later)
        # 15% risk per critical issue, 5% per high issue
        risk_score = min((len(critical_issues) * 15) + (len(high_issues) * 5), 100) 

        return {
            "sprint_title": active_sprints[0].get("title"),
            "risk_score_percent": risk_score,
            "status": "High Risk" if risk_score > 60 else "Moderate" if risk_score > 30 else "On Track",
            "critical_blockers": len(critical_issues),
            "recommendation": "Halt new feature development and swarm critical bugs immediately." if risk_score > 60 else "Sprint is proceeding normally."
        }

    def generate_executive_summary(self, normalized_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Module 19: Executive Dashboard Compiler.
        Combines all analysis into a single unified JSON for the frontend/LLM.
        """
        issues = [e for e in normalized_events if e.get("entity_type") in ["task", "bug", "story"]]
        sprints = [e for e in normalized_events if e.get("entity_type") == "sprint"]
        epics = [e for e in normalized_events if e.get("entity_type") == "epic"]

        bottlenecks = self.detect_bottlenecks(issues)
        sprint_risk = self.predict_sprint_risk(sprints, issues)

        summary = {
            "health_metrics": {
                "total_active_epics": len(epics),
                "open_issues": len(issues),
                "completion_probability": f"{100 - sprint_risk.get('risk_score_percent', 0)}%"
            },
            "sprint_intelligence": sprint_risk,
            "detected_bottlenecks": bottlenecks
        }
        
        print("📈 [AgentOS Brain] Executive Summary generated successfully.")
        return summary