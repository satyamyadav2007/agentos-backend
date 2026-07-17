'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@clerk/nextjs'; // ⚡ CLERK IMPORT
import { 
  CheckCircle2, Loader2, Server, Database, BrainCircuit, 
  Activity, AlertCircle, ArrowRight, Network, GitPullRequest, 
  Terminal, ShieldCheck, Zap 
} from 'lucide-react';

export default function MissionControlSync() {
  const router = useRouter();
  const logsEndRef = useRef<HTMLDivElement>(null);
  const { getToken } = useAuth(); // ⚡ GET TOKEN FUNCTION

  // 🧠 THE UNIVERSAL SYNC ENGINE STATE (Single Source of Truth)
  const [engineState, setEngineState] = useState({
    overallProgress: 0,
    eta: "Estimating...",
    isCoreComplete: false,
    apps: [] as {name: string, status: string, progress: number, items: string}[],
    agents: [] as {name: string, status: string}[], // ⚡ AGENTS AB SIRF YAHAN HAIN
    metrics: { repos: 0, issues: 0, prs: 0, commits: 0 },
    dataQuality: { collected: 0, normalized: 0, embedded: 0, graphNodes: 0, relationships: 0 },
    earlyFindings: [] as {label: string, value: string}[],
    logs: [] as {time: string, source: string, msg: string}[]
  });

  // Extract variables for UI
  const { overallProgress, eta, isCoreComplete, apps,  metrics, dataQuality, earlyFindings, logs } = engineState;

  // ⚡ MASTER PIPELINE: Fetch Status -> Fetch Agents -> Trigger Sync (ALL AUTHENTICATED)
  useEffect(() => {
    const initializeMissionControl = async () => {
      try {
        const workspaceId = localStorage.getItem('agentos_workspace_id');
        if (!workspaceId) return;

        const token = await getToken(); // ⚡ FETCH FRESH TOKEN
        const headers = {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` // ⚡ INJECT TOKEN
        };

        console.log("🔍 Fetching connected tools and active agents...");
        
        // 1. Fetch Connected Apps
        const statusRes = await fetch(`https://agentos-api-5suh.onrender.com/api/integrations/status?workspace_id=${workspaceId}`, { headers });
        const statusData = await statusRes.json();
        
        const connectedTools = (statusData.connected_tools && statusData.connected_tools.length > 0) 
          ? statusData.connected_tools 
          : ["github"];

        const dynamicApps = connectedTools.map((toolName: string) => ({
          name: toolName.charAt(0).toUpperCase() + toolName.slice(1),
          status: 'waiting',
          progress: 0,
          items: 'Waiting'
        }));

        // 2. Fetch Active Agents
        const agentsRes = await fetch(`https://agentos-api-5suh.onrender.com/api/agents/active?workspace_id=${workspaceId}`, { headers });
        const agentsData = await agentsRes.json();
        
        const activeAgents = (agentsData.active_agents && agentsData.active_agents.length > 0)
          ? agentsData.active_agents
          : ["Data Normalizer Agent", "Knowledge Graph Builder", "AI CPO Analytics"]; // Fallbacks

        const dynamicAgents = activeAgents.map((agentName: string) => ({
          name: agentName,
          status: 'waiting'
        }));

        // Update UI State Once
        setEngineState(prev => ({ ...prev, apps: dynamicApps, agents: dynamicAgents }));

        // 3. 🚀 TRIGGER THE BACKEND SYNC (NO MORE 401!)
        console.log("🚀 Firing Authorized Sync Request...");
        await fetch('https://agentos-api-5suh.onrender.com/api/sync/start', {
          method: 'POST',
          headers: headers,
          body: JSON.stringify({ 
            workspace_id: workspaceId,
            integrations: connectedTools
          })
        });

      } catch (error) {
        console.error("🚨 Mission Control Initialization Failed:", error);
      }
    };

    initializeMissionControl();
  }, []);

  // Auto-scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  
  
  // ✅ 1. Agents state ko empty array se initialize karo
  const [agents, setAgents] = useState<{name: string, status: string}[]>([]);

  // ✅ 2. Backend se active agents fetch karne wala block
  useEffect(() => {
    const fetchActiveAgents = async () => {
      try {
        const workspaceId = typeof window !== 'undefined' ? localStorage.getItem('agentos_workspace_id') : null;
        if (!workspaceId) return;

        // Backend endpoint call (Example: /api/agents/active)
        const res = await fetch(`https://agentos-api-5suh.onrender.com/api/agents/active?workspace_id=${workspaceId}`);
        const data = await res.json();

        // Backend se list aayegi: ["Cleaner Agent", "Theme Agent", "Sentiment Agent", "Forecast Agent"]
        if (data.active_agents && data.active_agents.length > 0) {
          const dynamicAgents = data.active_agents.map((agentName: string) => ({
            name: agentName,
            status: 'waiting' // Initial default status
          }));
          setAgents(dynamicAgents);
        }
      } catch (error) {
        console.error("🚨 Failed to fetch active agents:", error);
      }
    };

    fetchActiveAgents();
  }, []);
  
  // Auto-scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  // ==========================================
  // 🚀 WEBSOCKET SIMULATOR (Replace with real WS later)
  // ==========================================
  useEffect(() => {
    // Render URL ko WSS (WebSocket Secure) protocol me convert kar rahe hain
    const wsUrl = 'wss://agentos-api-5suh.onrender.com/ws';
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log("🟢 WebSocket Connected to AgentOS Engine");
      setEngineState(prev => ({
        ...prev,
        logs: [
          ...prev.logs, 
          {
            time: new Date().toLocaleTimeString('en-US', { hour12: false }),
            source: 'System',
            msg: 'Connected to AgentOS Universal Sync Engine...'
          }
        ]
      }));
    };

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        
        // ⚡ UNIVERSAL SYNC: Backend ab seedha poora state object bhejega!
        if (payload.type === 'UNIVERSAL_STATE_UPDATE') {
           setEngineState(payload.data);
        }
        
      } catch (error) {
        console.error("🚨 WebSocket Payload Parse Error:", error);
      }
    };
    ws.onerror = (error) => {
      console.error("🚨 WebSocket Error:", error);
    };

    ws.onclose = () => {
      console.log("🔴 WebSocket Disconnected");
    };

    // Cleanup when user leaves the page
    return () => {
      ws.close();
    };
  }, []);

  // ==========================================
  // 🎨 UI COMPONENTS
  // ==========================================
  const getStatusColor = (status: string) => {
    if (status === 'done') return 'text-green-400';
    if (status === 'syncing' || status === 'running') return 'text-blue-400 animate-pulse';
    if (status === 'error') return 'text-red-400';
    return 'text-gray-500';
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white p-6 md:p-10 font-sans selection:bg-blue-500/30">
      
      {/* HEADER */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 border-b border-gray-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Server className="text-blue-500" /> Mission Control
          </h1>
          <p className="text-gray-400 mt-1">AgentOS Enterprise Initialization Sequence</p>
        </div>
        <div className="mt-4 md:mt-0 text-right">
          <div className="text-sm text-gray-400">Estimated Remaining</div>
          <div className="text-2xl font-mono text-blue-400">{eta}</div>
        </div>
      </div>

      {/* MAIN OVERALL PROGRESS */}
      <div className="mb-10">
        <div className="flex justify-between mb-2 text-sm font-bold">
          <span>Overall Pipeline Progress</span>
          <span className="text-blue-400">{overallProgress}%</span>
        </div>
        <div className="w-full bg-gray-900 h-2 rounded-full overflow-hidden border border-gray-800">
          <div 
            className="bg-blue-500 h-full transition-all duration-500 ease-out shadow-[0_0_15px_rgba(59,130,246,0.6)]"
            style={{ width: `${overallProgress}%` }}
          />
        </div>
      </div>

      {/* GRID LAYOUT */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* COLUMN 1: INTEGRATIONS & QUEUE */}
        <div className="space-y-6">
          <div className="bg-[#0a0a0a] border border-gray-800 rounded-xl p-5">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Network className="w-5 h-5 text-gray-400" /> Integration Queue
            </h2>
            <div className="space-y-4">
              {apps.map((app, i) => (
                <div key={i} className="bg-black border border-gray-800 rounded-lg p-3">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-semibold">{app.name}</span>
                    <span className={`text-xs uppercase font-bold ${getStatusColor(app.status)}`}>
                      {app.status === 'done' ? <CheckCircle2 className="w-4 h-4 inline mr-1" /> : null}
                      {app.status}
                    </span>
                  </div>
                  {app.status !== 'disconnected' && (
                    <>
                      <div className="w-full bg-gray-900 h-1.5 rounded-full overflow-hidden mb-1">
                        <div className={`h-full transition-all duration-300 ${app.status === 'done' ? 'bg-green-500' : 'bg-blue-500'}`} style={{ width: `${app.progress}%` }} />
                      </div>
                      <div className="text-xs text-gray-500 text-right">{app.items}</div>
                    </>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="bg-[#0a0a0a] border border-gray-800 rounded-xl p-5">
             <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Database className="w-5 h-5 text-gray-400" /> Real-time Metrics
            </h2>
            <div className="grid grid-cols-2 gap-4">
               {Object.entries(metrics).map(([key, val]) => (
                 <div key={key} className="bg-black p-3 border border-gray-800 rounded text-center">
                   <div className="text-2xl font-mono text-white">{val.toLocaleString()}</div>
                   <div className="text-xs text-gray-500 uppercase">{key}</div>
                 </div>
               ))}
            </div>
          </div>
        </div>

        {/* COLUMN 2: AI AGENTS & INSIGHTS */}
        <div className="space-y-6">
          <div className="bg-[#0a0a0a] border border-gray-800 rounded-xl p-5 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-2"><BrainCircuit className="w-20 h-20 text-gray-800 opacity-20" /></div>
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2 relative z-10">
              <Activity className="w-5 h-5 text-gray-400" /> AI CPO Live Thinking
            </h2>
            <div className="space-y-3 relative z-10">
              {agents.map((agent, i) => (
                <div key={i} className="flex items-center gap-3 text-sm">
                  {agent.status === 'running' ? <Loader2 className="w-4 h-4 text-blue-400 animate-spin" /> : 
                   agent.status === 'done' ? <CheckCircle2 className="w-4 h-4 text-green-500" /> : 
                   <div className="w-4 h-4 rounded-full border border-gray-600" />}
                  <span className={agent.status === 'waiting' ? 'text-gray-500' : 'text-gray-200'}>
                    {agent.name}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-[#0a0a0a] border border-gray-800 rounded-xl p-5">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Network className="w-5 h-5 text-gray-400" /> Graph Knowledge Build
            </h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between border-b border-gray-800 pb-2"><span className="text-gray-400">Raw Data Collected</span> <span className="font-mono text-gray-300">{dataQuality.collected.toLocaleString()}</span></div>
              <div className="flex justify-between border-b border-gray-800 py-2"><span className="text-gray-400">Signals Normalized</span> <span className="font-mono text-blue-400">{dataQuality.normalized.toLocaleString()}</span></div>
              <div className="flex justify-between border-b border-gray-800 py-2"><span className="text-gray-400">Vectors Embedded</span> <span className="font-mono text-purple-400">{dataQuality.embedded.toLocaleString()}</span></div>
              <div className="flex justify-between border-b border-gray-800 py-2"><span className="text-gray-400">Neo4j Nodes Created</span> <span className="font-mono text-emerald-400">{dataQuality.graphNodes.toLocaleString()}</span></div>
              <div className="flex justify-between pt-2"><span className="text-emerald-500 font-bold">Graph Relationships</span> <span className="font-mono text-emerald-500">{dataQuality.relationships.toLocaleString()}</span></div>
            </div>
          </div>

          {earlyFindings.length > 0 && (
            <div className="bg-blue-900/10 border border-blue-900/30 rounded-xl p-5">
              <h2 className="text-lg font-bold text-blue-400 mb-3 flex items-center gap-2">
                <Zap className="w-5 h-5" /> Early AI Findings
              </h2>
              {earlyFindings.map((finding, i) => (
                <div key={i} className="mb-2 last:mb-0">
                  <div className="text-xs text-gray-400">{finding.label}</div>
                  <div className="text-sm font-semibold">{finding.value}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* COLUMN 3: LIVE TERMINAL & LAUNCH */}
        {/* LIVE TERMINAL BOX */}
        <div className="space-y-6 flex flex-col h-full">
          <div className="bg-[#050505] border border-gray-800 rounded-xl overflow-hidden flex-1 flex flex-col shadow-lg shadow-black/50">
            
            {/* Terminal Header */}
            <div className="bg-[#111] px-4 py-2 border-b border-gray-800 flex items-center gap-2 text-xs font-mono text-gray-400">
              <Terminal className="w-4 h-4 text-gray-500" /> root@agentos-core ~
            </div>
            
            {/* Terminal Body (Live Logs) */}
            <div className="p-4 font-mono text-xs overflow-y-auto max-h-[400px] flex-1 space-y-2">
              
              {/* Agar logs khali hain toh waiting state */}
              {logs.length === 0 ? (
                <div className="text-gray-600 animate-pulse">Waiting for backend connection...</div>
              ) : (
                /* Asli live logs backend se */
                logs.map((log, i) => (
                  <div key={i} className="leading-relaxed">
                    <span className="text-gray-600">[{log.time}]</span>{' '}
                    <span className="text-purple-400">[{log.source}]</span>{' '}
                    <span className="text-green-400">{log.msg}</span>
                  </div>
                ))
              )}
              
              {/* Auto-scroll anchor */}
              <div ref={logsEndRef} />
            </div>
          </div>

          {/* BACKGROUND SYNC & DASHBOARD BUTTON */}
          <div className={`transition-all duration-500 ${isCoreComplete ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10 pointer-events-none'}`}>
            <div className="bg-green-900/10 border border-green-900/30 rounded-xl p-5 text-center">
              <CheckCircle2 className="w-10 h-10 text-green-500 mx-auto mb-3" />
              <h3 className="font-bold text-lg mb-1">Core Sync Complete</h3>
              <p className="text-sm text-gray-400 mb-4">AgentOS has built the initial knowledge graph. Deep historical sync will continue in the background (32%).</p>
              <button 
                onClick={() => router.push('/dashboard')}
                className="w-full bg-white text-black hover:bg-gray-200 font-bold py-3 px-4 rounded flex justify-center items-center gap-2 transition-colors"
              >
                Open Executive Dashboard <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}