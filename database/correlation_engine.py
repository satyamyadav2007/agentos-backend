from typing import List, Dict, Any

class CrossToolCorrelationEngine:
    """
    Module 17: Cross-Tool Correlation (The Killer Feature)
    Wires together Jira, GitHub, Zendesk, and Slack into a single unified graph.
    """

    @staticmethod
    def get_correlation_cypher_queries() -> List[str]:
        """
        Returns the Cypher queries needed to link distinct tools in Neo4j automatically.
        Run these queries after every major sync or via a cron job.
        """
        return [
            # 🔗 1. GitHub PR -> Jira Issue
            # Matches Jira Key (e.g., ENG-123) inside the PR Title or Branch Name
            """
            MATCH (i:Issue {source: 'jira'}), (p:PullRequest {source: 'github'})
            WHERE p.title CONTAINS i.metadata.key 
               OR p.metadata.branch CONTAINS i.metadata.key
            MERGE (p)-[r:RESOLVES]->(i)
            SET r.correlated_at = timestamp()
            """,
            
            # 🔗 2. GitHub Commit -> Jira Issue
            # Matches Jira Key inside the Commit Message
            """
            MATCH (i:Issue {source: 'jira'}), (c:Commit {source: 'github'})
            WHERE c.description CONTAINS i.metadata.key
            MERGE (c)-[r:IMPLEMENTS]->(i)
            SET r.correlated_at = timestamp()
            """,

            # 🔗 3. Zendesk Ticket -> Jira Issue
            # Matches Jira keys mentioned in support tickets, or links the same Customer
            """
            MATCH (t:Ticket {source: 'zendesk'}), (i:Issue {source: 'jira'})
            WHERE t.description CONTAINS i.metadata.key 
               OR i.description CONTAINS t.id
            MERGE (t)-[r:ESCALATED_TO]->(i)
            SET r.correlated_at = timestamp()
            """,

            # 🔗 4. Slack Discussion -> GitHub/Jira
            # Links Slack threads to PRs or Issues based on URLs shared in chat
            """
            MATCH (s:Discussion {source: 'slack'}), (e)
            WHERE e.source IN ['jira', 'github'] AND s.description CONTAINS e.id
            MERGE (s)-[r:DISCUSSES]->(e)
            SET r.correlated_at = timestamp()
            """
        ]

    @staticmethod
    def query_unified_impact(neo4j_driver, jira_issue_key: str) -> Dict[str, Any]:
        """
        The Executive Dashboard Query: 
        Finds the exact blast radius of a single Jira Issue across all tools.
        """
        print(f"🕸️ [AgentOS Graph] Running Cross-Tool Impact Analysis for {jira_issue_key}...")
        
        query = """
        MATCH path = (t:Ticket {source: 'zendesk'})-[:ESCALATED_TO]->(i:Issue {key: $issue_key})<-[:RESOLVES]-(p:PullRequest {source: 'github'})
        OPTIONAL MATCH (p)<-[:DISCUSSES]-(s:Discussion {source: 'slack'})
        RETURN 
            t.title AS zendesk_complaint, 
            t.author AS customer, 
            p.title AS pr_title, 
            p.author AS developer,
            s.title AS slack_thread
        """
        
        with neo4j_driver.session() as session:
            result = session.run(query, issue_key=jira_issue_key)
            records = [record.data() for record in result]
            
        if not records:
            return {"status": "isolated", "message": "No cross-tool correlation found yet."}
            
        return {
            "status": "correlated",
            "issue_key": jira_issue_key,
            "blast_radius": {
                "customers_affected": len(set(r.get("customer") for r in records if r.get("customer"))),
                "active_developers": len(set(r.get("developer") for r in records if r.get("developer"))),
                "support_tickets_linked": len([r for r in records if r.get("zendesk_complaint")]),
                "slack_threads_active": len([r for r in records if r.get("slack_thread")])
            },
            "raw_paths": records
        }