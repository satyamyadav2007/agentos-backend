from typing import Dict, Any, List

class JiraAdvancedIntelligence:
    """
    AgentOS Advanced AI Service.
    Handles Backlog Clustering, Multi-dimensional Prioritization, and Blocker Detection.
    """

    @staticmethod
    def group_backlog(issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Module 5: Backlog Intelligence
        Instead of showing 500 tickets, AI groups them by strategic themes.
        """
        print("🧠 [AgentOS AI] Clustering backlog into strategic themes...")
        
        themes = {
            "Authentication & Security": 0,
            "Payments & Revenue": 0,
            "Performance & Core": 0,
            "UI/UX & Frontend": 0,
            "Uncategorized": 0
        }

        for issue in issues:
            # Combine title and description for semantic scanning
            text = (issue.get("title", "") + " " + issue.get("description", "")).lower()
            
            if any(k in text for k in ["auth", "login", "oauth", "security", "token"]):
                themes["Authentication & Security"] += 1
            elif any(k in text for k in ["pay", "stripe", "checkout", "billing", "revenue"]):
                themes["Payments & Revenue"] += 1
            elif any(k in text for k in ["slow", "memory", "optimize", "speed", "crash", "db"]):
                themes["Performance & Core"] += 1
            elif any(k in text for k in ["ui", "design", "css", "frontend", "layout"]):
                themes["UI/UX & Frontend"] += 1
            else:
                themes["Uncategorized"] += 1

        return {"module": "backlog_intelligence", "clusters": themes}

    @staticmethod
    def calculate_ai_priorities(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Module 12: AI Prioritization
        Translates raw Jira priority into Business, Engineering, and Customer Pain priorities.
        """
        print("⚖️ [AgentOS AI] Calculating Multi-dimensional Priorities...")
        prioritized_issues = []
        
        for issue in issues:
            severity = issue.get("severity", "Medium")
            text = issue.get("title", "").lower()
            
            # Heuristics for MVP (To be upgraded with LLM embeddings later)
            biz_priority = "High" if severity in ["Critical", "High"] else "Medium"
            eng_priority = "High" if any(k in text for k in ["api", "db", "architecture", "refactor"]) else "Medium"
            customer_pain = "High" if severity == "Critical" or "bug" in issue.get("entity_type", "") else "Low"

            prioritized_issues.append({
                "issue_id": issue["id"],
                "title": issue["title"],
                "ai_priority": {
                    "business_priority": biz_priority,
                    "engineering_priority": eng_priority,
                    "customer_pain_priority": customer_pain
                }
            })
            
        return prioritized_issues

    @staticmethod
    def detect_blockers(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Module 14: Blocker Detection
        Highlights tasks that are actively blocked and predicts ETA/Action.
        """
        print("🚧 [AgentOS AI] Scanning for active blockers...")
        blockers = []
        
        for issue in issues:
            status = issue.get("metadata", {}).get("status", "").lower()
            title = issue.get("title", "").lower()

            # Detect if blocked via status, tags, or explicit title mentions
            is_blocked = "block" in status or "waiting" in status or "[blocked]" in title

            if is_blocked:
                blockers.append({
                    "issue_id": issue["id"],
                    "title": issue["title"],
                    "current_status": status,
                    "owner": issue.get("author", "Unassigned"),
                    "impact": "High" if issue.get("severity") in ["High", "Critical"] else "Medium",
                    "recommended_action": f"Swarm: Unblock {issue.get('author', 'the team')} to prevent sprint delay."
                })
                
        return blockers

    @staticmethod
    def run_intelligence_suite(normalized_issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Runs all Advanced Jira Intelligence modules at once."""
        return {
            "backlog_clusters": JiraAdvancedIntelligence.group_backlog(normalized_issues),
            "ai_prioritization": JiraAdvancedIntelligence.calculate_ai_priorities(normalized_issues),
            "active_blockers": JiraAdvancedIntelligence.detect_blockers(normalized_issues)
        }