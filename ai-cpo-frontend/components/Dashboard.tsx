import React, { useState, useEffect } from 'react';
import { useTheme } from 'next-themes';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Search, Filter, Moon, Sun, Bell, MessageSquare, Share2, AlertTriangle, TrendingUp, DollarSign, PlusCircle, X, Send } from 'lucide-react';
import { UserButton } from "@clerk/nextjs";
const trendData = [
  { name: 'Week 1', risk: 4000 },
  { name: 'Week 2', risk: 12000 },
  { name: 'Week 3', risk: 8000 },
  { name: 'Week 4', risk: 20000 },
];

export default function AgentOSDashboard({ issues = [] }: { issues: any[] }) {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const [searchTerm, setSearchTerm] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('All');
  const [userRole, setUserRole] = useState('CEO'); 
  
  // ⚡ NEW: Chat State
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'ai', text: "Hello! I'm your AI Chief Product Officer. Ask me about the current sprint, revenue risks, or PRD statuses." }
  ]);
  const [isChatLoading, setIsChatLoading] = useState(false);

  // ⚡ NEW: Ingestion Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [ingestSource, setIngestSource] = useState('Zendesk');
  const [ingestText, setIngestText] = useState('');
  const [isIngesting, setIsIngesting] = useState(false);

  const filteredIssues = issues?.filter(issue => {
    const issueText = issue.originalText || "System Alert"; 
    const matchesSearch = issueText.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSeverity = filterSeverity === 'All' || issue.analysis?.severity === filterSeverity;
    return matchesSearch && matchesSeverity;
  });

  // ⚡ ACTION: Handle Jira Export
  const handleJiraExport = async (issue: any) => {
    try {
      alert("AI is drafting and pushing to Jira...");
      const response = await fetch('http://localhost:8000/export-jira', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: issue.originalText || "AgentOS Issue",
          prd_content: issue.prd_draft || "Auto-generated PRD"
        })
      });
      const data = await response.json();
      alert(data.status === 'success' ? "✅ " + data.message : "❌ Failed: " + data.message);
    } catch (error) {
      alert("🚨 Backend is offline.");
    }
  };

  // ⚡ ACTION: Handle Chat Send
  // ⚡ THE FIX: Catching 'data.reply' instead of crashing
  const handleChat = async () => {
    if (!chatInput.trim()) return;
    const userMessage = chatInput;
    setChatHistory(prev => [...prev, { role: 'user', text: userMessage }]);
    setChatInput('');
    setIsChatLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          context_data: issues
        })
      });
      const data = await response.json();
      
      // ⚡ YAHAN THA BUG: Ab hum data.reply ko safely extract kar rahe hain
      const aiText = data.reply || data.response || (typeof data === 'string' ? data : JSON.stringify(data));
      setChatHistory(prev => [...prev, { role: 'ai', text: aiText }]);
      
    } catch (error) {
      setChatHistory(prev => [...prev, { role: 'ai', text: "🚨 Connection error with AI Kernel." }]);
    } finally {
      setIsChatLoading(false);
    }
  };

  // ⚡ ACTION: Simulate Incoming Webhook
  const handleSimulateWebhook = async () => {
    if (!ingestText.trim()) return;
    setIsIngesting(true);
    try {
      // Directing to our support processing route
      await fetch('http://localhost:8000/process-support', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticket_text: ingestText,
          user_email: "user_email"
        })
      });
      alert(`✅ ${ingestSource} data sent to AgentOS Kernel! Waiting for WebSocket to process...`);
      setIsModalOpen(false);
      setIngestText('');
    } catch (error) {
      alert("🚨 Failed to connect to Backend.");
    } finally {
      setIsIngesting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-8 transition-colors duration-200">
      
      {/* 1. TOP NAVIGATION */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
          AgentOS {userRole === 'CEO' ? 'Executive' : userRole === 'Manager' ? 'Ops' : 'Dev'} Workspace
        </h1>
        
        <div className="flex space-x-4 items-center">
          
          {/* ⚡ NEW: Simulate Webhook Button for Demo purposes */}
          <button 
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-bold transition-all shadow-md"
          >
            <PlusCircle className="h-5 w-5" /> Simulate Ingestion
          </button>

          <div className="bg-gradient-to-r from-indigo-500 to-purple-600 p-[1px] rounded-lg">
            <select 
              className="px-4 py-2 rounded-lg bg-white dark:bg-gray-900 font-semibold cursor-pointer outline-none"
              value={userRole}
              onChange={(e) => setUserRole(e.target.value)}
            >
              <option value="CEO">👑 CEO View</option>
              <option value="Manager">📊 Eng Manager View</option>
              <option value="Developer">💻 Developer View</option>
            </select>
          </div>
          
          <div className="flex space-x-4 items-center">
          
          {/* Simulate Webhook Button... */}
          
          <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} className="p-2 rounded-lg bg-gray-200 dark:bg-gray-800">
            {mounted ? (theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />) : <div className="h-5 w-5" />}
          </button>

          {/* ⚡ NEW: User Profile & Logout Button */}
          <div className="ml-4 pl-4 border-l border-gray-300 dark:border-gray-700">
            <UserButton />
          </div>
        </div>
      </div>
    </div>

      {/* INGESTION MODAL (Vercel Demo Fix) */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-2xl w-[500px] border dark:border-gray-700 relative">
            <button onClick={() => setIsModalOpen(false)} className="absolute top-4 right-4 text-gray-500 hover:text-red-500"><X /></button>
            <h2 className="text-xl font-bold mb-4">Simulate Incoming Data</h2>
            <p className="text-sm text-gray-500 mb-4">In production, AgentOS listens to Webhooks automatically. For this demo, simulate incoming data here.</p>
            
            <label className="block text-sm font-semibold mb-2">Source Integration</label>
            <select 
              className="w-full p-2 mb-4 rounded border dark:border-gray-600 dark:bg-gray-700 outline-none"
              value={ingestSource}
              onChange={(e) => setIngestSource(e.target.value)}
            >
              <option value="Zendesk">Zendesk Customer Email</option>
              <option value="GitHub">GitHub Issue Webhook</option>
              <option value="Slack">Slack Escalation</option>
            </select>

            <label className="block text-sm font-semibold mb-2">Raw Payload / Issue Text</label>
            <textarea 
              rows={4} 
              className="w-full p-3 rounded border dark:border-gray-600 dark:bg-gray-700 outline-none mb-4"
              placeholder="E.g., The app is freezing when I try to process my credit card..."
              value={ingestText}
              onChange={(e) => setIngestText(e.target.value)}
            />

            <button 
              onClick={handleSimulateWebhook}
              disabled={isIngesting || !ingestText}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg disabled:opacity-50 transition-colors"
            >
              {isIngesting ? "Routing through OS Kernel..." : "Fire Webhook"}
            </button>
          </div>
        </div>
      )}

      {/* 2. EXECUTIVE RISK DASHBOARD */}
      {(userRole === 'CEO' || userRole === 'Manager') && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700 flex items-center gap-4">
            <div className="p-4 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-full"><DollarSign /></div>
            <div>
              <p className="text-sm text-gray-500 font-semibold">Total Revenue at Risk</p>
              <h2 className="text-2xl font-bold">$1,250,000</h2>
            </div>
          </div>
          <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700 flex items-center gap-4">
            <div className="p-4 bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 rounded-full"><AlertTriangle /></div>
            <div>
              <p className="text-sm text-gray-500 font-semibold">Critical Bugs Detected</p>
              <h2 className="text-2xl font-bold">{issues.length || 3}</h2>
            </div>
          </div>
          <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700 flex items-center gap-4">
            <div className="p-4 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full"><TrendingUp /></div>
            <div>
              <p className="text-sm text-gray-500 font-semibold">AI Automated Fixes</p>
              <h2 className="text-2xl font-bold">84%</h2>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* LEFT COLUMN: Issues & Pipeline */}
        <div className="lg:col-span-2 space-y-6">
          
          {(userRole === 'CEO' || userRole === 'Manager') && (
            <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700">
              <h3 className="text-lg font-semibold mb-4">Revenue Risk Trend (30 Days)</h3>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="name" stroke="#9CA3AF" />
                    <YAxis stroke="#9CA3AF" />
                    <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', color: '#fff' }} />
                    <Line type="monotone" dataKey="risk" stroke="#EF4444" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Issue Cards */}
          {filteredIssues?.map((issue, idx) => (
            <div key={idx} className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700 flex flex-col gap-4">
              <div className="flex justify-between items-start">
                <h3 className="text-xl font-bold">{issue.originalText || "System Alert"}</h3>
                {userRole !== 'Developer' && issue.revenue?.revenue_at_risk > 0 && (
                  <span className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-bold">
                    Risk: ${issue.revenue.revenue_at_risk.toLocaleString()}
                  </span>
                )}
              </div>

              <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg mt-2 flex justify-between items-center">
                 <div>
                   <h4 className="font-semibold text-sm mb-2 text-gray-500">AI Sprint Allocation</h4>
                   <div className="flex gap-4">
                     <div className="text-blue-500 font-medium text-sm">Points: {issue.sprint_plan?.points || '8'}</div>
                     <div className="text-purple-500 font-medium text-sm">Target: {issue.sprint_plan?.sprint || 'Current'}</div>
                   </div>
                 </div>
                 {/* LIVE EXPORT BUTTON */}
                 <button onClick={() => handleJiraExport(issue)} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors">
                   {issue.jira_ticket_url ? "View in Jira ↗" : "Export to Jira"}
                 </button>
              </div>

              <div className="mt-4 pt-4 border-t dark:border-gray-700">
                <div className="flex items-center gap-8 text-sm">
                  <div className="flex items-center gap-2 text-green-500"><div className="h-2 w-2 bg-green-500 rounded-full"></div> Ingested</div>
                  <div className="flex items-center gap-2 text-blue-500"><div className="h-2 w-2 bg-blue-500 rounded-full"></div> RAG Checked</div>
                  <div className="flex items-center gap-2 text-purple-500"><div className="h-2 w-2 bg-purple-500 rounded-full"></div> PRD Drafted</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* RIGHT COLUMN: Causal Insights & AI Chat */}
        <div className="space-y-6">
          
          <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Share2 className="text-blue-500" /> Causal Insights (Graph)
            </h3>
            <div className="space-y-4 text-sm">
              <div className="p-3 bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900 rounded-lg">
                <span className="font-bold text-red-600 dark:text-red-400">Root Cause:</span> Redis Timeout in Auth Module (Commit #4829)
              </div>
              <div className="p-3 bg-blue-50 dark:bg-blue-900/10 border border-blue-100 dark:border-blue-900 rounded-lg">
                <span className="font-bold text-blue-600 dark:text-blue-400">Impact Radius:</span> 4 Frontend Components, 12,000 Active Sessions
              </div>
            </div>
          </div>

          {/* ⚡ LIVE AI CPO CHAT BOX */}
          <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700 h-[400px] flex flex-col">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <MessageSquare className="text-purple-500" /> Ask AI CPO
            </h3>
            
            {/* Chat History Area */}
            <div className="flex-1 bg-gray-50 dark:bg-gray-900 rounded-lg p-4 mb-4 overflow-y-auto text-sm space-y-4 border dark:border-gray-700">
              {chatHistory.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`p-3 rounded-lg max-w-[85%] ${msg.role === 'user' ? 'bg-purple-600 text-white' : 'bg-gray-200 dark:bg-gray-800'}`}>
                    {msg.text}
                  </div>
                </div>
              ))}
              {isChatLoading && (
                <div className="flex justify-start">
                  <div className="p-3 rounded-lg bg-gray-200 dark:bg-gray-800 animate-pulse">Thinking...</div>
                </div>
              )}
            </div>

            {/* Chat Input Area */}
            <div className="flex gap-2">
              <input 
                type="text" 
                placeholder="Who caused the risk?..." 
                className="flex-1 px-3 py-2 border dark:border-gray-700 rounded-lg dark:bg-gray-900 text-sm outline-none focus:border-purple-500" 
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleChat()}
              />
              <button 
                onClick={handleChat} 
                disabled={isChatLoading || !chatInput.trim()}
                className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white p-2 rounded-lg transition-colors"
              >
                <Send className="h-5 w-5" />
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}