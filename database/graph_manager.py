# database/graph_manager.py
from neo4j import AsyncGraphDatabase
import os

# Neo4j Local Instance Credentials (Ollama ki tarah local chalega)
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password123") # Apni password lagayein

class KnowledgeGraphManager:
    def __init__(self):
        self.driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    async def close(self):
        await self.driver.close()

    async def ingest_causal_data(self, email: str, company_arr: int, ticket_id: str, feedback_text: str, theme_data: dict, current_release: str = "v2.8"):
        """
        Ye function Customer, Ticket, Bug aur Release ko ek single transaction mein link karega.
        """
        domain = email.split("@")[-1].lower() if "@" in email else "unknown"
        category = theme_data.get("category", "Unclassified")
        severity = theme_data.get("severity", "Low")
        summary = theme_data.get("summary", "No summary")
        
        # Cypher Query jo nodes banayegi aur unhe aapas mein interconnect karega
        query = """
        // 1. Merge Customer Node
        MERGE (c:Customer {domain: $domain})
        ON CREATE SET c.name = $domain, c.arr = $company_arr, c.health_score = 100
        ON MATCH SET c.arr = $company_arr
        
        // 2. Create Ticket Node
        CREATE (t:Ticket {ticket_id: $ticket_id, text: $feedback_text})
        
        // 3. Merge active Release Node
        MERGE (r:Release {version: $current_release})
        
        // 4. Connect Customer to Ticket
        CREATE (c)-[:OPENED]->(t)
        
        // 5. Conditional execution: Agar Bug hai toh separate node banake release aur ticket dono se link karo
        FOREACH (_ IN CASE WHEN $category = 'Bug' THEN [1] ELSE [] END |
            MERGE (b:Bug {title: $summary})
            ON CREATE SET b.severity = $severity, b.status = 'Open'
            CREATE (t)-[:IDENTIFIED_AS]->(b)
            CREATE (r)-[:INTRODUCED]->(b)
        )
        """
        
        async with self.driver.session() as session:
            await session.run(
                query, 
                domain=domain, 
                company_arr=company_arr, 
                ticket_id=ticket_id, 
                feedback_text=feedback_text,
                category=category,
                severity=severity,
                summary=summary,
                current_release=current_release
            )
            print(f"[GraphDB] Successfully mapped causal connection for {domain} on release {current_release}")
    async def get_causal_summary(self):
        """
        Fetches the causal impact of bugs on company ARR from Neo4j.
        """
        query = """
        MATCH (r:Release {version: "v2.8"})-[:INTRODUCED]->(b:Bug)<-[:IDENTIFIED_AS]-(t:Ticket)<-[:OPENED]-(c:Customer)
        RETURN r.version AS FailedRelease, 
               b.title AS RootCauseBug, 
               COUNT(DISTINCT c) AS ImpactedCustomers, 
               SUM(c.arr) AS TotalARRDamaged
        ORDER BY TotalARRDamaged DESC
        LIMIT 5;
        """
        
        async with self.driver.session() as session:
            result = await session.run(query)
            # data() automatically formats the Neo4j records into a Python list of dictionaries
            records = await result.data() 
            return records        

# Singleton Instance for the system
graph_db = KnowledgeGraphManager()