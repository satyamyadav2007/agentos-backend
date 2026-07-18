import os
import certifi
from neo4j import GraphDatabase
from dotenv import load_dotenv
from typing import List, Dict, Any

# Neo4j connection se pehle env variables load karna zaroori hai
load_dotenv() 

os.environ["SSL_CERT_FILE"] = certifi.where()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

class Neo4jConnection:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )

        try:
            self.driver.verify_connectivity()
            print("✅ [GraphDB] Neo4j Enterprise Graph Connected Successfully")
        except Exception as e:
            print("❌ [GraphDB] Connectivity Error:", repr(e))
            raise

    def close(self):
        self.driver.close()
        
    def process_events_for_graph(self, events):
        valid_events = []
        for event in events:
            # 👇 SAFETY CHECK: Ignore events without a valid ID 👇
            event_id = event.get("id") or getattr(event, "id", None)
            if not event_id or event_id == "unknown":
                print(f"⚠️ [GraphDB] Skipping event with null/unknown ID: {event.get('title')}")
                continue
                
            valid_events.append(event)

    async def build_knowledge_graph(self, workspace_id: str, records: List[Dict[str, Any]]):
        """
        [SPRINT 3 ENGINE]
        Takes normalized Universal Events and builds a connected Knowledge Graph.
        Maps: Engineer -> PR -> Commit -> Issue -> Repository
        """
        print(f"🕸️ [GraphDB] Building Knowledge Graph for {len(records)} records...")
        
        # Categorize records
        issues = [r for r in records if r.get("entity_type") == "issue"]
        prs = [r for r in records if r.get("entity_type") == "pull_request"]
        commits = [r for r in records if r.get("entity_type") == "commit"]

        with self.driver.session() as session:
            try:
                # 1. Ingest Issues & Link to Repository and Engineer
                if issues:
                    session.run("""
                    UNWIND $records AS rec
                    MERGE (w:Workspace {id: $workspace_id})
                    MERGE (repo:Repository {name: rec.repository})
                    MERGE (w)-[:OWNS]->(repo)
                    MERGE (user:Engineer {name: rec.author})
                    MERGE (issue:Issue {id: rec.metadata_json.github_id})
                    SET issue.title = rec.title, 
                        issue.severity = rec.severity, 
                        issue.state = rec.metadata_json.state,
                        issue.number = rec.metadata_json.number
                    MERGE (user)-[:REPORTED]->(issue)
                    MERGE (issue)-[:BELONGS_TO]->(repo)
                    """, records=issues, workspace_id=workspace_id)

                # 2. Ingest Pull Requests & Link
                if prs:
                    session.run("""
                    UNWIND $records AS rec
                    MERGE (repo:Repository {name: rec.repository})
                    MERGE (user:Engineer {name: rec.author})
                    MERGE (pr:PullRequest {id: rec.metadata_json.github_id})
                    SET pr.title = rec.title, 
                        pr.state = rec.metadata_json.state,
                        pr.number = rec.metadata_json.number
                    MERGE (user)-[:OPENED_PR]->(pr)
                    MERGE (pr)-[:TARGETS]->(repo)
                    """, records=prs)

                # 3. Ingest Commits & Link
                if commits:
                    session.run("""
                    UNWIND $records AS rec
                    MERGE (repo:Repository {name: rec.repository})
                    MERGE (user:Engineer {name: rec.author})
                    MERGE (commit:Commit {sha: rec.metadata_json.sha})
                    SET commit.message = rec.title,
                        commit.url = rec.metadata_json.url
                    MERGE (user)-[:COMMITTED]->(commit)
                    MERGE (commit)-[:APPLIED_TO]->(repo)
                    """, records=commits)

                # 4. The Magic AI Cross-Linking (Connecting PRs to Issues if mentioned in title/body)
                # This uses Neo4j's string matching to automatically map "Fixes #123" logic.
                session.run("""
                MATCH (pr:PullRequest), (issue:Issue)
                WHERE pr.title CONTAINS toString(issue.number) OR pr.state = 'merged'
                MERGE (pr)-[:RESOLVES]->(issue)
                """)

                print("✅ [GraphDB] Knowledge Graph mapping complete!")

            except Exception as e:
                print(f"🚨 [GraphDB Error] Failed to build graph: {e}")

    def get_active_issues(self, user_email: str, limit: int = 5):
        """
        Fetches REAL active engineering/product issues directly from the Graph.
        """
        query = """
        MATCH (e:Issue)
        WHERE e.severity IN ['High', 'Critical'] AND e.state = 'open'
        RETURN e.title AS title, e.severity AS severity, 'github' AS source
        LIMIT $limit
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, limit=limit)
                
                real_issues = []
                for record in result:
                    real_issues.append({
                        "title": record["title"],
                        "severity": record["severity"],
                        "source": record["source"]
                    })
                return real_issues

        except Exception as e:
            print(f"🚨 [GraphDB Error] Query failed: {e}")
            return []

    def get_causal_insights(self):
        query = """
        MATCH (e:Event)-[:AFFECTS]->(c:Client)
        RETURN e.title AS RootCauseBug, 
               "Current" AS FailedRelease, 
               count(c) AS ImpactedCustomers, 
               sum(c.arr) AS TotalARRDamaged
        ORDER BY TotalARRDamaged DESC LIMIT 2
        """
        with self.driver.session() as session:
            try:
                result = session.run(query)
                return [{"RootCauseBug": r["RootCauseBug"], "FailedRelease": r["FailedRelease"], 
                         "ImpactedCustomers": r["ImpactedCustomers"], "TotalARRDamaged": r["TotalARRDamaged"]} 
                        for r in result]
            except Exception as e:
                return []
    def get_root_cause_context(self, keyword: str):
        """
        [SPRINT 4] Searches the Knowledge Graph for a specific issue and traces it 
        back to the Pull Request and Engineer.
        """
        # Cypher query to trace: Issue <-[RESOLVES]- PullRequest <-[OPENED_PR]- Engineer
        query = """
        MATCH (issue:Issue)
        WHERE toLower(issue.title) CONTAINS toLower($keyword)
        OPTIONAL MATCH (pr:PullRequest)-[:RESOLVES]->(issue)
        OPTIONAL MATCH (eng:Engineer)-[:OPENED_PR]->(pr)
        RETURN issue.title AS Bug_Title, 
               issue.severity AS Severity, 
               issue.state AS Issue_State,
               pr.title AS Fixing_PR, 
               pr.state AS PR_State, 
               eng.name AS Responsible_Engineer
        LIMIT 5
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, keyword=keyword)
                context_data = []
                for record in result:
                    context_data.append(dict(record))
                
                print(f"🔍 [GraphDB] Found {len(context_data)} related nodes for keyword: '{keyword}'")
                return context_data

        except Exception as e:
            print(f"🚨 [GraphDB Error] Root Cause Query failed: {e}")
            return []            

# Single Global Instance
graph_db = Neo4jConnection()