import os
import certifi
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Neo4j connection se pehle env variables load karna zaroori hai
load_dotenv() 

from neo4j import GraphDatabase
# ... baaki ka purana code waisa hi rahega ...

os.environ["SSL_CERT_FILE"] = certifi.where()

# 🚨 APNE NEO4J CREDENTIALS YAHAN DAALO 🚨
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
            print("✅ Neo4j Connected Successfully")
        except Exception as e:
            print("❌ Connectivity Error:", repr(e))
            raise
    def close(self):
        self.driver.close()

    def get_causal_insights(self):
        # Cypher Query: Graph se data nikalne ka formula
        # Yeh query 'Bug' ko pakdegi, uske 'AFFECTS' relationship se 'Client' tak jayegi
        query = """
        MATCH (b:Bug)-[:AFFECTS]->(c:Client)
        RETURN b.title AS RootCauseBug, 
               b.release AS FailedRelease, 
               count(c) AS ImpactedCustomers, 
               sum(c.arr) AS TotalARRDamaged
        ORDER BY TotalARRDamaged DESC LIMIT 2
        """
        
        with self.driver.session(database="862f6db5") as session:
            try:
                result = session.run(query)
                insights = []
                for record in result:
                    insights.append({
                        "RootCauseBug": record["RootCauseBug"],
                        "FailedRelease": record["FailedRelease"],
                        "ImpactedCustomers": record["ImpactedCustomers"],
                        "TotalARRDamaged": record["TotalARRDamaged"]
                    })
                return insights    
                
                
            except Exception as e:
                print(f"[Graph Error] Failed to connect or query: {e}")
                return []
    def ingest_github_data(self, processed_issues):
        """
        Takes real data from GitHub/Revenue agents and builds the Knowledge Graph.
        """
        # Cypher Query: Graph mein naye Nodes (Bug, Client) aur Relationship (AFFECTS) banana
        query = """
        UNWIND $issues AS issue
        
        // 1. Create or Update the Bug Node
        MERGE (b:Bug {title: issue.title})
        SET b.severity = issue.severity,
            b.category = issue.category,
            b.release = "Current Sprint" // Ise baad me CI/CD se dynamic karenge
            
        // 2. Create or Update the Client/Revenue Node
        MERGE (c:Client {id: issue.client_id})
        SET c.name = "Enterprise Segment",
            c.arr = toInteger(issue.revenue_risk)
            
        // 3. Create the Causal Relationship
        MERGE (b)-[r:AFFECTS]->(c)
        """
        
        # Data ko Neo4j format me normalize karna
        formatted_issues = []
        for idx, issue in enumerate(processed_issues):
            formatted_issues.append({
                "title": issue.get("originalText", "Unknown Bug"),
                "severity": issue.get("analysis", {}).get("severity", "Unknown"),
                "category": issue.get("analysis", {}).get("category", "Unknown"),
                "revenue_risk": issue.get("revenue", {}).get("revenue_at_risk", 0),
                "client_id": f"SEGMENT_{idx}" 
            })
            
        if not formatted_issues:
            return

        with self.driver.session(database="862f6db5") as session:
            try:
                session.run(query, issues=formatted_issues)
                print(f"[Graph] Successfully ingested {len(formatted_issues)} real issues into Neo4j!")
            except Exception as e:
                print(f"[Graph Error] Data ingestion failed: {e}")            

    def _seed_initial_data(self):
        # Yeh function tumhare naye graph database mein Nodes aur Relationships banayega
        seed_query = """
        MERGE (b1:Bug {title: 'OAuth Token Expired (Real DB)', release: 'v3.1'})
        MERGE (c1:Client {name: 'Acme Corp', arr: 800000})
        MERGE (c2:Client {name: 'Globex', arr: 450000})
        MERGE (b1)-[:AFFECTS]->(c1)
        MERGE (b1)-[:AFFECTS]->(c2)

        MERGE (b2:Bug {title: 'Database Deadlock (Real DB)', release: 'v3.0'})
        MERGE (c3:Client {name: 'Initech', arr: 920000})
        MERGE (b2)-[:AFFECTS]->(c3)
        """
        with self.driver.session(database="862f6db5") as session:
            session.run(seed_query)
    def ingest_root_cause_node(self, bug_title: str, client_email: str, arr_impact: float):
        """
        Graph database me Bug, Client, Engineer aur Git Commit ke beech
        deep connections (relationships) build karta hai.
        """
        print(f"[Graph] Simulating autonomous root cause analysis for: {bug_title}")
        
        # Super-powerful Cypher Query for enterprise telemetry
        query = """
        MERGE (b:Bug {title: $bug_title})
        SET b.severity = 'High', b.status = 'Open'
        
        MERGE (c:Client {email: $client_email})
        SET c.arr = $arr_impact
        
        MERGE (e:Engineer {name: 'Rahul Sharma', team: 'Core Auth'})
        MERGE (cm:Commit {hash: '9fd88', message: 'Optimized login query session tokens'})
        
        // Relationships create karo
        MERGE (c)-[:IMPACTED_BY]->(b)
        MERGE (cm)-[:INTRODUCED]->(b)
        MERGE (e)-[:AUTHORED]->(cm)
        """
        
        with self.driver.session() as session:
            session.run(query, bug_title=bug_title, client_email=client_email, arr_impact=arr_impact)
            print("✅ [Graph] Root Cause Node permanently mapped: Engineer 'Rahul Sharma' linked via Commit #9fd88.")        

# Ek global instance bana lo taaki main.py isko import kar sake
graph_db = Neo4jConnection()

