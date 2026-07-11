import asyncio
from typing import List
from core.models.event import UniversalEvent
# 1. Tumhare existing Neo4j database ko import karo
from database.graph_manager import graph_db  # Assuming graph_db is your initialized instance

# 2. Tumhare existing agents ko unke folder se import karo
from agents.theme_agent import ThemeAgent
from agents.revenue_agent import RevenueAgent
from agents.prd_agent import PRDAgent
from agents.action_engine import ActionEngine

async def _route_to_agents(self, event: UniversalEvent):
    """Routes high-signal events using YOUR existing agents and database."""
    
    # Neo4j me event ingest karna (using your existing graph_manage.py logic)
    await graph_db.ingest_event(event) 
    
    if event.severity in ["Critical", "High"]:
        print(f"🧠 [AgentOS Brain] Waking up AI Pipeline for: {event.title}")
        
        # Theme Agent ko call karo
        theme_agent = ThemeAgent()
        analysis = await theme_agent.analyze_theme(event.text)
        
        # Revenue Agent ko call karo
        revenue_agent = RevenueAgent()
        rev_impact = await revenue_agent.calculate_impact(event, analysis)
        
        # PRD Agent ko call karo
        if analysis.get('category') in ["Feature Request", "Bug", "Escalation"]:
            prd_agent = PRDAgent()
            jira_spec = await prd_agent.generate_spec(analysis, event.title)
            
            # Action Engine ko call karo
            action_engine = ActionEngine()
            await action_engine.execute_workflow(
                event_title=event.title, 
                prd_draft=jira_spec, 
                revenue_data=rev_impact
            )

class UniversalEventBus:
    def __init__(self):
        self.event_queue = asyncio.Queue()
        self.is_running = False
        print("🚌 [Event Bus] Initialized and waiting for data streams...")

    async def publish(self, events: List[UniversalEvent]):
        for event in events:
            await self.event_queue.put(event)
        print(f"📥 [Event Bus] Received {len(events)} new events. Queue size: {self.event_queue.qsize()}")

    async def _route_to_neo4j(self, event: UniversalEvent):
        # Neo4j Graph DB logic yahan aayega baad me
        pass

    async def _route_to_agents(self, event: UniversalEvent):
        if event.severity in ["Critical", "High"] or (event.engagement_score and event.engagement_score > 50):
            print(f"🧠 [AgentOS Brain] Waking up AI for critical {event.source} event: {event.title}")
            pass

    async def _process_events(self):
        self.is_running = True
        while self.is_running:
            try:
                event: UniversalEvent = await self.event_queue.get()
                await asyncio.gather(
                    self._route_to_neo4j(event),
                    self._route_to_agents(event)
                )
                self.event_queue.task_done()
            except Exception as e:
                print(f"🚨 [Event Bus Error] Failed to process event: {e}")

    async def start(self):
        asyncio.create_task(self._process_events())
        print("🟢 [Event Bus] Processor started!")

    async def stop(self):
        self.is_running = False
        await self.event_queue.join()
        print("🛑 [Event Bus] Processor stopped.")

event_bus = UniversalEventBus()