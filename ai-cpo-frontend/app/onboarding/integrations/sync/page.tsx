'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { CheckCircle2, CircleDashed, Loader2, Database, BrainCircuit, Network, AlertTriangle, TrendingDown, Lightbulb, Terminal } from 'lucide-react';

// Defines the strict enterprise stages of our AgentOS sync
type SyncStage = 'pending' | 'loading' | 'done' | 'error';

interface PipelineStep {
  id: string;
  label: string;
  status: SyncStage;
  details?: string;
}

interface EarlyInsight {
  id: string;
  type: 'risk' | 'bug' | 'feature' | 'info';
  text: string;
  value?: string;
  icon: any;
}

export default function BootstrappingEngineScreen() {
  const router = useRouter();
  const logsEndRef = useRef<HTMLDivElement>(null);
  
  const [pipeline, setPipeline] = useState<PipelineStep[]>([
    { id: 'workspace', label: 'Workspace Allocated & Secured', status: 'done' },
    { id: 'auth', label: 'OAuth Connections Verified', status: 'done' },
    { id: 'discovery', label: 'Discovering Repositories & Assets', status: 'loading' },
    { id: 'ingestion', label: 'Ingesting High-Priority Data', status: 'pending' },
    { id: 'ai', label: 'AI Theme & Revenue Analysis', status: 'pending' },
    { id: 'graph', label: 'Building Knowledge Graph', status: 'pending' }
  ]);

  const [logs, setLogs] = useState<string[]>(['> Initializing AgentOS Bootstrapping Engine...']);
  const [insights, setInsights] = useState<EarlyInsight[]>([]);
  const [isReady, setIsReady] = useState(false);

  // Auto-scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  useEffect(() => {
    // ⚡ REAL ENTERPRISE IMPLEMENTATION:
    // In production, replace this simulation with actual SSE (Server-Sent Events) or WebSocket
    // Example: 
    // const eventSource = new EventSource('/api/jobs/sync/events?workspace_id=' + workspaceId);
    // eventSource.onmessage = (e) => updatePipeline(JSON.parse(e.data));

    // --- SIMULATED SSE BACKEND EVENTS FOR UI DEMO ---
    const addLog = (msg: string) => setLogs(prev => [...prev, `> ${msg}`]);
    const updateStep = (id: string, status: SyncStage, details?: string) => {
      setPipeline(prev => prev.map(step => step.id === id ? { ...step, status, details } : step));
    };

    let timer = 0;
    
    // Stage 1: Discovery
    setTimeout(() => {
      addLog("GitHub: Found 42 repositories. Initiating metadata sync.");
      addLog("Jira: Found 3 active projects (ENG, PROD, DES).");
      updateStep('discovery', 'done', '42 Repos, 3 Projects discovered');
      updateStep('ingestion', 'loading');
    }, timer += 2500);

    // Stage 2: Ingestion & Live Insights
    setTimeout(() => {
      addLog("Ingesting latest 500 issues for baseline context.");
      updateStep('ingestion', 'done', 'Baseline data imported. Background sync started.');
      updateStep('ai', 'loading');
      
      // Reveal Early Insight 1
      setInsights(prev => [...prev, {
        id: 'i1', type: 'bug', text: 'Recurring Authentication Bugs Detected', value: '18 instances', icon: AlertTriangle
      }]);
    }, timer += 3000);

    // Stage 3: AI Analysis
    setTimeout(() => {
      addLog("AI: Correlating customer tickets with GitHub pull requests.");
      
      // Reveal Early Insight 2 & 3
      setInsights(prev => [...prev, 
        { id: 'i2', type: 'risk', text: 'Estimated Revenue at Risk', value: '$1.2M', icon: TrendingDown },
        { id: 'i3', type: 'feature', text: 'High-Priority Feature Requests', value: '14 identified', icon: Lightbulb }
      ]);
      
      updateStep('ai', 'done', 'Pain points and revenue risks calculated');
      updateStep('graph', 'loading');
    }, timer += 3500);

    // Stage 4: Knowledge Graph
    setTimeout(() => {
      addLog("Neo4j: Generating vector embeddings for cross-tool correlation.");
      addLog("System: Base context window ready. Delegating historical sync to background worker.");
      updateStep('graph', 'done', 'Vectors generated. AgentOS core online.');
      setIsReady(true);
    }, timer += 3500);

  }, []);

  const handleEnterDashboard = () => {
    // Navigates to the real dashboard while the background sync continues
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white p-6 md:p-12 font-sans flex flex-col items-center">
      
      {/* Header */}
      <div className="w-full max-w-5xl flex items-center justify-between mb-12">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-blue-900/30 border border-blue-500/50 rounded-xl flex items-center justify-center">
            <BrainCircuit className="text-blue-400" size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-bold uppercase tracking-wide">Bootstrapping Workspace</h1>
            <p className="text-gray-400 text-sm">Building unified intelligence graph from connected tools</p>
          </div>
        </div>
        
        {isReady && (
          <button 
            onClick={handleEnterDashboard}
            className="bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-8 rounded-lg shadow-[0_0_20px_rgba(37,99,235,0.3)] transition-all animate-fade-in flex items-center gap-2"
          >
            Open Executive Dashboard
          </button>
        )}
      </div>

      <div className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Left Column: The Pipeline */}
        <div className="bg-[#0a0a0a] border border-gray-800 rounded-2xl p-8 shadow-xl">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-widest mb-8">
            Execution Pipeline
          </h2>
          
          <div className="space-y-6">
            {pipeline.map((step, index) => (
              <div key={step.id} className="relative flex gap-4">
                {/* Connecting Line */}
                {index !== pipeline.length - 1 && (
                  <div className={`absolute left-[11px] top-8 bottom-[-24px] w-0.5 ${step.status === 'done' ? 'bg-green-500/30' : 'bg-gray-800'}`} />
                )}
                
                {/* Status Icon */}
                <div className="relative z-10 bg-[#0a0a0a] pt-1">
                  {step.status === 'done' && <CheckCircle2 className="text-green-500" size={24} />}
                  {step.status === 'loading' && <Loader2 className="text-blue-500 animate-spin" size={24} />}
                  {step.status === 'pending' && <CircleDashed className="text-gray-700" size={24} />}
                </div>

                {/* Content */}
                <div className="flex-1 pb-2">
                  <h3 className={`text-lg font-medium ${step.status === 'pending' ? 'text-gray-600' : 'text-gray-200'}`}>
                    {step.label}
                  </h3>
                  {step.details && (
                    <p className="text-sm text-gray-500 mt-1">{step.details}</p>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Terminal / Logger */}
          <div className="mt-10 bg-black border border-gray-800 rounded-xl p-4 h-48 overflow-y-auto font-mono text-xs text-gray-400">
            <div className="flex items-center gap-2 mb-3 border-b border-gray-800 pb-2 text-gray-600">
              <Terminal size={14} /> Live System Logs
            </div>
            {logs.map((log, i) => (
              <div key={i} className="mb-1 opacity-80 animate-fade-in">{log}</div>
            ))}
            <div ref={logsEndRef} />
          </div>
        </div>

        {/* Right Column: Early Insights */}
        <div className="flex flex-col gap-6">
          <div className="bg-gradient-to-br from-blue-900/10 to-purple-900/10 border border-blue-900/30 rounded-2xl p-8 shadow-xl flex-1">
            <h2 className="text-sm font-semibold text-blue-400 uppercase tracking-widest mb-2">
              Value Discovered
            </h2>
            <p className="text-gray-400 text-sm mb-8">
              AgentOS is extracting insights while background sync continues.
            </p>

            <div className="space-y-4">
              {insights.length === 0 ? (
                <div className="h-40 flex flex-col items-center justify-center text-gray-600 border border-dashed border-gray-800 rounded-xl">
                  <Network className="mb-2 opacity-50" size={24} />
                  <p className="text-sm">Awaiting correlation data...</p>
                </div>
              ) : (
                insights.map((insight) => {
                  const Icon = insight.icon;
                  return (
                    <div key={insight.id} className="bg-black/50 border border-gray-800 p-4 rounded-xl flex items-center gap-4 animate-fade-in">
                      <div className={`p-3 rounded-lg ${
                        insight.type === 'risk' ? 'bg-red-500/10 text-red-400' :
                        insight.type === 'bug' ? 'bg-orange-500/10 text-orange-400' :
                        'bg-green-500/10 text-green-400'
                      }`}>
                        <Icon size={20} />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm text-gray-400">{insight.text}</p>
                        <p className="text-xl font-bold text-white">{insight.value}</p>
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            {isReady && (
              <div className="mt-8 p-4 bg-green-500/10 border border-green-500/20 rounded-xl text-green-400 text-sm flex items-start gap-3 animate-fade-in">
                <CheckCircle2 size={18} className="shrink-0 mt-0.5" />
                <p>
                  <strong>Baseline established.</strong> You can now use the dashboard. AgentOS will continue syncing historical tickets and older repositories silently in the background.
                </p>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}