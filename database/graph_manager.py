import os
import certifi
from neo4j import GraphDatabase
from dotenv import load_dotenv

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

    async def ingest_event(self, event):
        """
        [THE REAL ENGINE]
        Takes a UniversalEvent from EventBus and maps it dynamically into Neo4j.
        No hardcoded names, no simulations. 100% Real Data.
        """
        # Graph query: Create an Event node and link it to its Source
        query = """
        MERGE (s:Source {name: $source})
        MERGE (e:Event {title: $title})
        SET e.text = $text,
            e.severity = $severity,
            e.sentiment = $sentiment,
            e.url = $url,
            e.ingested_at = timestamp()
            
        MERGE (s)-[:GENERATED]->(e)
        """
        
        # event object directly use hoga
        with self.driver.session() as session:
            try:
                session.run(
                    query, 
                    source=event.source.lower(),
                    title=event.title,
                    text=event.text,
                    severity=event.severity,
                    sentiment=event.sentiment,
                    url=event.url
                )
                print(f"🕸️ [GraphDB] Real Event Mapped: {event.source} -> {event.title[:30]}...")
            except Exception as e:
                print(f"🚨 [GraphDB Error] Failed to ingest real event: {e}")

    def get_active_issues(self, user_email: str, limit: int = 5):
        """
        Fetches REAL active engineering/product issues directly from the Graph.
        """
        # Ye query real events pull karegi jo GitHub, Jira ya Zendesk se aaye hain
        query = """
        MATCH (e:Event)
        WHERE e.severity IN ['High', 'Critical', 'Medium']
        RETURN e.title AS title, e.severity AS severity, e.source AS source
        ORDER BY e.ingested_at DESC
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
                
                print(f"🔍 [GraphDB] Retrieved {len(real_issues)} real issues from Neo4j.")
                return real_issues

        except Exception as e:
            print(f"🚨 [GraphDB Error] Query failed: {e}")
            return []

    def get_causal_insights(self):
        # Purana logic waisa hi rahega jab tak hum Revenue Agent ko fully connect na kar lein
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

# Single Global Instance
graph_db = Neo4jConnection()