'use client'
import { useState } from 'react';
import { CheckCircle2, Clock, Database, Settings } from 'lucide-react';

interface IntegrationProps {
  name: string;
  logoUrl: string;
  isConnected: boolean;
  capabilities: string[];
  permissions: string[];
  workspaceId?: string; 
  setConnectedTools?: React.Dispatch<React.SetStateAction<string[]>>;
  syncStats?: {
    lastSync: string;
    recordsImported: number;
    issues: number;
    prs: number;
  };
}

export default function IntegrationCard({ name, logoUrl, isConnected, capabilities, workspaceId = "default", permissions, syncStats, setConnectedTools }: IntegrationProps) {
  const [loading, setLoading] = useState(false);
  const [isConnecting, setIsConnecting] = useState<string | null>(null);

  const handleConnect = async () => {
    setIsConnecting(name);
    setLoading(true);

    // ==========================================
    // 1. OAUTH 2.0 FLOWS (REDIRECTS)
    // ==========================================
    if (name === "GitHub") {
      window.location.href = "https://github.com/apps/agentos-ai-cpo/installations/new";
      return;
    } 
    else if (name === "Jira") {
      const clientId = "zjaxoFFVOp1dhVrcWsoKqqrAfnMADIfq"; 
      const redirectUri = encodeURIComponent("https://agentos-frontend-azure.vercel.app/onboarding/integrations");
      window.location.href = `https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id=${clientId}&scope=read%3Ajira-work%20write%3Ajira-work%20read%3Ajira-user&redirect_uri=${redirectUri}&state=jira_auth&response_type=code&prompt=consent`;
      return;
    } 
    else if (name === 'Slack') {
      const clientId = "11490498949286.11534438119542"; 
      const redirectUri = encodeURIComponent("https://agentos-frontend-azure.vercel.app/onboarding/integrations");
      const scopes = "channels:history,channels:read,chat:write,groups:history,users:read";
      window.location.href = `https://slack.com/oauth/v2/authorize?client_id=${clientId}&scope=${scopes}&redirect_uri=${redirectUri}&state=slack_auth`;
      return;
    }
    else if (name === "Zendesk") {
      const subdomain = window.prompt("Enter your Zendesk subdomain (e.g., acme):");
      if (subdomain) {
        localStorage.setItem('temp_zendesk_subdomain', subdomain);
        const clientId = "YOUR_ZENDESK_CLIENT_ID";
        const redirectUri = encodeURIComponent("https://agentos-frontend-azure.vercel.app/onboarding/integrations");
        window.location.href = `https://${subdomain}.zendesk.com/oauth/authorizations/new?response_type=code&client_id=${clientId}&redirect_uri=${redirectUri}&scope=read%20write`;
      } else {
        setLoading(false);
      }
      return;
    }
    if (name === 'GitLab') {
      const clientId = process.env.NEXT_PUBLIC_GITLAB_CLIENT_ID || "YOUR_GITLAB_CLIENT_ID";
      const redirectUri = encodeURIComponent("https://agentos-frontend-azure.vercel.app/onboarding/integrations");
      // Redirects to GitLab authorization page
      window.location.href = `https://gitlab.com/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&state=gitlab_auth&scope=api`;
      return;
    }  
    else if (name === 'Salesforce') {
      const clientId = process.env.NEXT_PUBLIC_SALESFORCE_CLIENT_ID || "TUMHARA_SALESFORCE_CLIENT_ID";
      const redirectUri = encodeURIComponent("https://agentos-frontend-azure.vercel.app/onboarding/integrations");
      window.location.href = `https://login.salesforce.com/services/oauth2/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code`;
      return;
    }
    else if (name === 'HubSpot') {
      const clientId = process.env.NEXT_PUBLIC_HUBSPOT_CLIENT_ID || "YOUR_HUBSPOT_CLIENT_ID";
      const redirectUri = encodeURIComponent("https://agentos-frontend-azure.vercel.app/onboarding/integrations");
      const scopes = encodeURIComponent("crm.objects.contacts.read crm.objects.deals.read");
      window.location.href = `https://app.hubspot.com/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scopes}&state=hubspot_auth`;
      return;
    }
    else if (name === 'Intercom') {
      const clientId = process.env.NEXT_PUBLIC_INTERCOM_CLIENT_ID || "YOUR_INTERCOM_CLIENT_ID";
      window.location.href = `https://app.intercom.com/oauth?client_id=${clientId}&state=intercom_auth`;
      return;
    }
    else if (name === 'Discord') {
      const clientId = process.env.NEXT_PUBLIC_DISCORD_CLIENT_ID || "YOUR_DISCORD_CLIENT_ID";
      const redirectUri = encodeURIComponent("https://agentos-frontend-azure.vercel.app/onboarding/integrations");
      const scopes = encodeURIComponent("identify bot");
      window.location.href = `https://discord.com/api/oauth2/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scopes}&state=discord_auth`;
      return;
    }
    else if (name === 'Reddit') {
      const clientId = process.env.NEXT_PUBLIC_REDDIT_CLIENT_ID || "YOUR_REDDIT_CLIENT_ID";
      const redirectUri = encodeURIComponent("https://agentos-frontend-azure.vercel.app/onboarding/integrations");
      const scopes = encodeURIComponent("read identity");
      window.location.href = `https://www.reddit.com/api/v1/authorize?client_id=${clientId}&response_type=code&state=reddit_auth&redirect_uri=${redirectUri}&duration=temporary&scope=${scopes}`;
      return;
    }

    // ==========================================
    // 2. DIRECT API FLOWS (NO REDIRECTS)
    // ==========================================
    
    // Analytics
    const analyticsTools = ['PostHog', 'Mixpanel', 'Amplitude'];
    if (analyticsTools.includes(name)) {
      const apiKey = window.prompt(`Enter your ${name} API Key / Token:`);
      if (!apiKey) { setLoading(false); setIsConnecting(null); return; }
      const projectId = window.prompt(`Enter your ${name} Project ID:`);
      if (!projectId) { setLoading(false); setIsConnecting(null); return; }

      fetch('https://agentos-api-5suh.onrender.com/api/integrations/analytics/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: name.toLowerCase(), api_key: apiKey, project_id: projectId, workspace_id: workspaceId })
      }).then(res => res.json()).then(data => {
        if (data.status === 'connected' && setConnectedTools) setConnectedTools(prev => prev.includes(name) ? prev : [...prev, name]);
      }).finally(() => { setLoading(false); setIsConnecting(null); });
      return;
    }

    // Crashes
    const crashTools = ['Sentry', 'Crashlytics'];
    if (crashTools.includes(name)) {
      const apiKey = window.prompt(`Enter your ${name} API Token:`);
      const orgSlug = window.prompt(`Enter your ${name} Organization Slug:`);
      const projectSlug = window.prompt(`Enter your ${name} Project Slug:`);
      if (!apiKey || !orgSlug || !projectSlug) { setLoading(false); return; }

      fetch('https://agentos-api-5suh.onrender.com/api/integrations/crashes/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: name.toLowerCase(), api_key: apiKey, org_slug: orgSlug, project_slug: projectSlug, workspace_id: workspaceId })
      }).then(res => res.json()).then(data => {
        if (data.status === 'connected' && setConnectedTools) setConnectedTools(prev => [...prev, name]);
      }).finally(() => setLoading(false));
      return;
    }

    // Knowledge
    const knowledgeTools = ['Notion', 'Confluence', 'Google Docs'];
    if (knowledgeTools.includes(name)) {
      const providerMap: Record<string, string> = { 'Notion': 'notion', 'Confluence': 'confluence', 'Google Docs': 'google_docs' };
      const token = window.prompt(`Enter your ${name} API Token:`);
      if (!token) { setLoading(false); return; }

      fetch('https://agentos-api-5suh.onrender.com/api/integrations/knowledge/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: providerMap[name], token: token, workspace_id: workspaceId })
      }).then(res => res.json()).then(data => {
        if (data.status === 'connected' && setConnectedTools) setConnectedTools(prev => [...prev, name]);
      }).finally(() => setLoading(false));
      return;
    }

    // Emails
    if (name === 'Gmail' || name === 'Outlook') {
      const token = window.prompt(`Enter your ${name} Access Token:`);
      if (!token) { setLoading(false); return; }
      fetch('https://agentos-api-5suh.onrender.com/api/integrations/email/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: name.toLowerCase(), access_token: token, workspace_id: workspaceId })
      }).then(res => res.json()).then(data => {
        if (data.status === 'connected' && setConnectedTools) setConnectedTools(prev => [...prev, name]);
      }).finally(() => setLoading(false));
      return;
    }

    // Specific Tools
    if (name === 'YouTube') {
      const apiKey = window.prompt(`Enter your YouTube Data API v3 Key:`);
      if (!apiKey) { setLoading(false); return; }
      fetch('https://agentos-api-5suh.onrender.com/api/integrations/youtube/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey, workspace_id: workspaceId })
      }).then(res => res.json()).then(data => {
        if (data.status === 'connected' && setConnectedTools) setConnectedTools(prev => [...prev, name]);
      }).finally(() => setLoading(false));
      return;
    }

    if (name === 'Zoom') {
      fetch('https://agentos-api-5suh.onrender.com/api/integrations/zoom/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workspace_id: workspaceId })
      }).then(res => res.json()).then(data => {
        if (data.status === 'connected' && setConnectedTools) setConnectedTools(prev => [...prev, name]);
      }).finally(() => setLoading(false));
      return;
    }

    if (name === 'Bitbucket') {
      const token = window.prompt(`Enter your Bitbucket App Password:`);
      const username = window.prompt(`Enter your Bitbucket Username:`);
      if (!token) { setLoading(false); return; }
      fetch('https://agentos-api-5suh.onrender.com/api/integrations/bitbucket/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: token, username: username || null, workspace_id: workspaceId })
      }).then(res => res.json()).then(data => {
        if (data.status === 'connected' && setConnectedTools) setConnectedTools(prev => [...prev, name]);
      }).finally(() => setLoading(false));
      return;
    }

    if (name === 'Linear') {
      const apiKey = window.prompt(`Enter your Linear Personal API Key:`);
      if (!apiKey) { setLoading(false); return; }
      fetch('https://agentos-api-5suh.onrender.com/api/integrations/linear/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey, workspace_id: workspaceId })
      }).then(res => res.json()).then(data => {
        if (data.status === 'connected' && setConnectedTools) setConnectedTools(prev => [...prev, name]);
      }).finally(() => setLoading(false));
      return;
    }

    if (name === 'Freshdesk') {
      const domain = window.prompt(`Enter your Freshdesk Domain:`);
      const apiKey = window.prompt(`Enter your Freshdesk API Key:`);
      if (!domain || !apiKey) { setLoading(false); return; }
      fetch('https://agentos-api-5suh.onrender.com/api/integrations/freshdesk/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey, domain: domain, workspace_id: workspaceId })
      }).then(res => res.json()).then(data => {
        if (data.status === 'connected' && setConnectedTools) setConnectedTools(prev => [...prev, name]);
      }).finally(() => setLoading(false));
      return;
    }

    if (name === 'Twitter') {
      const trackingQuery = window.prompt(`Enter the brand/product name you want to track:`);
      const bearerToken = window.prompt(`Enter your Twitter/X Bearer Token:`);
      if (!trackingQuery || !bearerToken) { setLoading(false); return; }
      fetch('https://agentos-api-5suh.onrender.com/api/integrations/twitter/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bearer_token: bearerToken, tracking_query: trackingQuery, workspace_id: workspaceId })
      }).then(res => res.json()).then(data => {
        if (data.status === 'connected' && setConnectedTools) setConnectedTools(prev => [...prev, name]);
      }).finally(() => setLoading(false));
      return;
    }

    if (name === 'Community') {
      const domain = window.prompt(`Enter your Forum Domain:`);
      const apiKey = window.prompt(`Enter your Community API Key:`);
      if (!domain || !apiKey) { setLoading(false); return; }
      fetch('https://agentos-api-5suh.onrender.com/api/integrations/community/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey, domain: domain, workspace_id: workspaceId })
      }).then(res => res.json()).then(data => {
        if (data.status === 'connected' && setConnectedTools) setConnectedTools(prev => [...prev, name]);
      }).finally(() => setLoading(false));
      return;
    }

    if (name === 'GA4') {
      const propertyId = window.prompt(`Enter your GA4 Property ID:`);
      if (!propertyId) { setLoading(false); return; }
      fetch('https://agentos-api-5suh.onrender.com/api/integrations/ga4/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ property_id: propertyId, service_account_json: "mock_json", workspace_id: workspaceId })
      }).then(res => res.json()).then(data => {
        if (data.status === 'connected' && setConnectedTools) setConnectedTools(prev => [...prev, name]);
      }).finally(() => setLoading(false));
      return;
    }

    if (name === 'Datadog') {
      const site = window.prompt(`Enter your Datadog Site:`) || "datadoghq.com";
      const apiKey = window.prompt(`Enter your Datadog API Key:`);
      const appKey = window.prompt(`Enter your Datadog Application Key:`);
      if (!apiKey || !appKey) { setLoading(false); return; }
      fetch('https://agentos-api-5suh.onrender.com/api/integrations/datadog/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey, app_key: appKey, site: site, workspace_id: workspaceId })
      }).then(res => res.json()).then(data => {
        if (data.status === 'connected' && setConnectedTools) setConnectedTools(prev => [...prev, name]);
      }).finally(() => setLoading(false));
      return;
    }

    if (name === 'Google Meet') {
      const accessToken = window.prompt(`Enter your Google Workspace OAuth Access Token:`);
      if (!accessToken) { setLoading(false); return; }
      fetch('https://agentos-api-5suh.onrender.com/api/integrations/google_meet/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ access_token: accessToken, workspace_id: workspaceId })
      }).then(res => res.json()).then(data => {
        if (data.status === 'connected' && setConnectedTools) setConnectedTools(prev => [...prev, name]);
      }).finally(() => setLoading(false));
      return;
    }

    console.log(`Connecting ${name} logic is pending...`);
    setLoading(false);
    setIsConnecting(null);
  };

  return (
    <div className={`border rounded-2xl p-6 transition-all ${isConnected ? 'bg-[#0a101a] border-blue-500/30' : 'bg-[#111] border-gray-800'}`}>
      
      {/* HEADER */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-gray-900 rounded-xl flex items-center justify-center border border-gray-700">
             <span className="text-xl font-bold">{name.charAt(0)}</span>
          </div>
          <div>
            <h3 className="text-xl font-bold text-white">{name}</h3>
            {isConnected ? (
              <span className="flex items-center gap-1.5 text-xs text-green-400 mt-1 bg-green-400/10 px-2 py-0.5 rounded-full w-fit">
                <CheckCircle2 size={12} /> Connected
              </span>
            ) : (
              <span className="text-xs text-gray-500 mt-1 block">Not Connected</span>
            )}
          </div>
        </div>
      </div>

      {/* BODY - DYNAMIC RENDER BASED ON STATUS */}
      {!isConnected ? (
        <div className="space-y-5 text-sm">
          <div>
            <h4 className="text-gray-400 font-medium mb-2 uppercase tracking-wider text-[10px]">Capabilities</h4>
            <div className="grid grid-cols-2 gap-2">
              {capabilities.map(cap => (
                <div key={cap} className="flex items-center gap-2 text-gray-300">
                  <CheckCircle2 size={14} className="text-blue-500" /> {cap}
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="text-gray-400 font-medium mb-2 uppercase tracking-wider text-[10px]">Permissions Required</h4>
            <ul className="text-gray-400 space-y-1 list-disc list-inside opacity-70">
              {permissions.map(perm => <li key={perm}>{perm}</li>)}
            </ul>
          </div>

          <button onClick={handleConnect} disabled={loading} className="w-full mt-4 bg-white text-black font-bold py-2.5 rounded-lg hover:bg-gray-200 transition-all">
            {loading ? 'Initiating...' : 'Connect Workspace'}
          </button>
        </div>
      ) : (
        <div className="space-y-4 text-sm bg-black/20 p-4 rounded-xl border border-gray-800/50">
          <div className="flex justify-between items-center text-gray-300 pb-3 border-b border-gray-800">
            <span className="flex items-center gap-2"><Clock size={14} className="text-blue-400"/> Last Sync</span>
            <span className="font-medium">{syncStats?.lastSync}</span>
          </div>
          <div className="flex justify-between items-center text-gray-300 pb-3 border-b border-gray-800">
             <span className="flex items-center gap-2"><Database size={14} className="text-purple-400"/> Total Records</span>
             <span className="font-mono">{syncStats?.recordsImported?.toLocaleString() || 0}</span>
          </div>
          <div className="flex gap-2 mt-4">
             <button className="flex-1 bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2 rounded-lg transition-all text-xs">
               Sync Now
             </button>
             <button className="px-3 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-all">
               <Settings size={16} />
             </button>
          </div>
        </div>
      )}
    </div>
  );
}