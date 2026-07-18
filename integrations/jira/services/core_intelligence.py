from typing import Dict, Any, List

class JiraCoreIntelligence:
    """
    AgentOS Core AI Service for Jira.
    Handles Issue Insights, Epic Summarization, and Sprint Risk Prediction.
    """

    @staticmethod
    def analyze_issue_intelligence(issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Module 3: Issue Intelligence ⭐⭐⭐⭐⭐
        Calculates Business Impact, Revenue Risk, and Engineering Complexity.
        """
        title = issue.get("title", "").lower()
        desc = issue.get("description", "").lower()
        labels = issue.get("metadata", {}).get("labels", [])
        
        text_payload = title + " " + desc
        
        # Base Heuristics (To be augmented by LLM later)
        business_impact = "Low"
        revenue_risk = "Low"
        eng_complexity = "Medium"
        
        if any(w in text_payload for w in ["pay", "stripe", "checkout", "billing", "cart", "subscription"]):
            revenue_risk = "High"
            business_impact = "Critical"
            
        if any(w in text_payload for w in ["auth", "security", "breach", "downtime", "crash", "p0"]):
            business_impact = "Critical"
            
        if any(w in text_payload for w in ["refactor", "migrate", "architecture", "database", "infrastructure"]):
            eng_complexity = "High"

        return {
            "issue_id": issue.get("id"),
            "key": issue.get("metadata", {}).get("key", "UNKNOWN"),
            "ai_insights": {
                "business_impact": business_impact,
                "revenue_risk": revenue_risk,
                "engineering_complexity": eng_complexity,
                "recommended_priority": "Highest" if business_impact == "Critical" else "Medium",
                "duplicate_risk": "Low" # MVP placeholder
            }
        }

    @staticmethod
    def summarize_epics(epics: List[Dict[str, Any]], stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Module 6: Epic Intelligence
        Summarizes Epic progress, identifies blockers, and estimates revenue opportunity.
        """
        print("📈 [AgentOS AI] Summarizing Epic Intelligence...")
        epic_summaries = []
        
        for epic in epics:
            epic_id = epic.get("id")
            
            # Find stories belonging to this Epic
            child_stories = [s for s in stories if s.get("metadata", {}).get("epic_id") == epic_id]
            total_stories = len(child_stories)
            done_stories = len([s for s in child_stories if s.get("metadata", {}).get("status", "").lower() in ["done", "completed", "closed"]])
            blocked_stories = [s.get("title") for s in child_stories if "block" in s.get("metadata", {}).get("status", "").lower()]
            
            progress = (done_stories / total_stories * 100) if total_stories > 0 else 0
            
            # Simulated Revenue Opportunity based on Keywords (MVP)
            rev_opp = "$0"
            if any(w in epic.get("title", "").lower() for w in ["checkout", "payment", "pro", "enterprise", "conversion"]):
                rev_opp = "$1.2M"
            elif any(w in epic.get("title", "").lower() for w in ["retention", "onboarding", "churn"]):
                rev_opp = "$450K"

            epic_summaries.append({
                "epic_id": epic_id,
                "title": epic.get("title"),
                "progress": f"{int(progress)}%",
                "blocked_by": blocked_stories[:2] if blocked_stories else "None", # Show top 2 blockers
                "revenue_opportunity": rev_opp
            })
            
        return epic_summaries

    @staticmethod
    def predict_sprint_risk(sprint_issues: List[Dict[str, Any]], average_velocity: int = 20) -> Dict[str, Any]:
        """
        Module 16: Risk Prediction ⭐⭐⭐⭐⭐
        Formula: High Story Points + Low Velocity + Many Bugs = Sprint Failure Risk.
        """
        print("⚠️ [AgentOS AI] Calculating Sprint Failure Risk...")
        
        # 1. Calculate Load
        # MVP: Assume each issue is roughly 3 points if not defined
        total_points_planned = len(sprint_issues) * 3 
        
        # 2. Count Bugs
        bug_count = len([i for i in sprint_issues if i.get("entity_type") == "bug" or "bug" in i.get("title", "").lower()])
        
        # 3. Calculate Risk Score (Out of 100)
        risk_score = 10 # Base risk
        
        # Penalty for over-committing against velocity
        if total_points_planned > average_velocity:
            overload_ratio = (total_points_planned - average_velocity) / average_velocity
            risk_score += (overload_ratio * 50) 
            
        # Penalty for technical debt/bugs
        risk_score += (bug_count * 8)
        
        risk_score = min(int(risk_score), 99) # Cap at 99%
        
        reasons = []
        if total_points_planned > average_velocity:
            reasons.append(f"Planned points ({total_points_planned}) exceed average velocity ({average_velocity}).")
        if bug_count > 2:
            reasons.append(f"High bug count ({bug_count}) threatens feature delivery.")
            
        return {
            "module": "risk_prediction",
            "sprint_failure_risk": f"{risk_score}%",
            "risk_factors": reasons if reasons else ["Sprint looks stable and well-planned."],
            "is_high_risk": risk_score > 70
        }