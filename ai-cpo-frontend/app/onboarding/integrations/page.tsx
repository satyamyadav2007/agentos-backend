'use client';

import { useAuth } from '@clerk/nextjs';
import { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter,  } from 'next/navigation';
import { ArrowRight, CheckCircle2, Link as LinkIcon, Database, Ticket, Hash } from 'lucide-react';

function IntegrationsContent() {
  const [connectedTools, setConnectedTools] = useState<string[]>([]);
  const [isConnecting, setIsConnecting] = useState<string | null>(null);
  const searchParams = useSearchParams();
  const router = useRouter();
  const { getToken } = useAuth(); 

  // 👉 YEH NAYA BLOCK ADD KARO (Load from LocalStorage)
  useEffect(() => {
    const savedTools = localStorage.getItem("connected_tools");
    if (savedTools) {
      setConnectedTools(JSON.parse(savedTools));
    }
  

  // 👉 YEH HELPER FUNCTION ADD KARO (Save to LocalStorage)
    const markToolAsConnected = (toolName: string) => {
      setConnectedTools(prev => {
        if (prev.includes(toolName)) return prev; // Agar pehle se hai toh ignore
        const updated = [...prev, toolName];
        localStorage.setItem("connected_tools", JSON.stringify(updated));
        return updated;
      });
    };






    const oauthToolMap: Record<string, string> = {
      'jira_auth': 'Jira',
      'slack_auth': 'Slack',
      'hubspot_auth': 'HubSpot',
      'intercom_auth': 'Intercom',
      'discord_auth': 'Discord',
      'reddit_auth': 'Reddit',
      'gitlab_auth': 'GitLab',
      'teams_auth': 'Teams',
      'linkedin_auth': 'LinkedIn',
      'gong_auth': 'Gong',
      'linear_auth': 'Linear',
      'notion_auth': 'Notion',
      'confluence_auth': 'Confluence',
      'zoom_auth': 'Zoom'
    };

    const workspaceId = typeof window !== 'undefined' ? localStorage.getItem('agentos_workspace_id') : null;
    const authCode = searchParams.get('code');
    const state = searchParams.get('state');
    const installationId = searchParams.get('installation_id');

    // Agar URL me callback data nahi hai, toh aage mat bado
    if (!installationId && !authCode) return;

    if (!workspaceId || workspaceId === 'default_workspace') {
      console.error("🚨 Invalid Workspace ID found in localStorage:", workspaceId);
      return;
    }

    // ⚡ MASTER CALLBACK HANDLER (Handles ALL OAuth connections securely)
    const processIntegrations = async () => {
      try {
        const token = await getToken();
        if (!token) throw new Error("Authentication token missing!");

        let fetchUrl = '';
        let fetchBody: any = {};
        let currentToolName = '';

        // 1. GITHUB FLOW
        if (installationId) {
          fetchUrl = `https://agentos-api-5suh.onrender.com/api/integrations/github/connect`;
          fetchBody = { installation_id: installationId, workspace_id: workspaceId };
          currentToolName = 'GitHub';
        } 
        // 2. GOOGLE FLOW
        else if (state === 'google_auth') {
          const targetTool = localStorage.getItem('google_target_tool') || 'Google';
          fetchUrl = `https://agentos-api-5suh.onrender.com/api/integrations/google/connect`;
          fetchBody = { auth_code: authCode, workspace_id: workspaceId, target: targetTool };
          currentToolName = targetTool;
        }
        // 3. FRESHDESK FLOW
        else if (state === 'freshdesk_auth') {
          const freshdeskSubdomain = localStorage.getItem('temp_freshdesk_subdomain');
          fetchUrl = `https://agentos-api-5suh.onrender.com/api/integrations/freshdesk/connect`;
          fetchBody = { auth_code: authCode, workspace_id: workspaceId, subdomain: freshdeskSubdomain };
          currentToolName = 'Freshdesk';
        }
        // 4. UNIVERSAL OAUTH FLOW
        else if (state && oauthToolMap[state]) {
          currentToolName = oauthToolMap[state];
          const endpoint = currentToolName.toLowerCase();
          fetchUrl = `https://agentos-api-5suh.onrender.com/api/integrations/${endpoint}/connect`;
          fetchBody = { auth_code: authCode, workspace_id: workspaceId };
        }
        // 5. ZENDESK FLOW (No state, uses subdomain flag)
        else if (!state && localStorage.getItem('temp_zendesk_subdomain')) {
          const zendeskSubdomain = localStorage.getItem('temp_zendesk_subdomain');
          fetchUrl = `https://agentos-api-5suh.onrender.com/api/integrations/zendesk/connect`;
          fetchBody = { auth_code: authCode, workspace_id: workspaceId, subdomain: zendeskSubdomain };
          currentToolName = 'Zendesk';
        }
        // 6. SALESFORCE FLOW (No state, no zendesk subdomain)
        else if (!state && !localStorage.getItem('temp_zendesk_subdomain')) {
          fetchUrl = `https://agentos-api-5suh.onrender.com/api/integrations/salesforce/connect`;
          fetchBody = { auth_code: authCode, workspace_id: workspaceId };
          currentToolName = 'Salesforce';
        }

        // Execute API Call if a valid flow was matched
        if (fetchUrl && currentToolName) {
          console.log(`🔗 Sending ${currentToolName} Auth Code to backend...`);
          
          const response = await fetch(fetchUrl, {
            method: 'POST',
            headers: { 
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}` // ✅ ALL flows are now secured
            },
            body: JSON.stringify(fetchBody)
          });

          const data = await response.json();

          if (response.ok && data.status === 'connected') {
            console.log(`✅ ${currentToolName} Connected Successfully!`);
            setConnectedTools(prev => prev.includes(currentToolName) ? prev : [...prev, currentToolName]);
            
            // Clean up temporary local storage items
            localStorage.removeItem('google_target_tool');
            localStorage.removeItem('temp_freshdesk_subdomain');
            localStorage.removeItem('temp_zendesk_subdomain');
          } else {
            console.error(`🚨 Backend rejected ${currentToolName}:`, data);
          }
        }

      } catch (error) {
        console.error("🚨 Auth Processing Crash:", error);
      } finally {
        // ✅ ALWAYS clean URL to prevent infinite re-fetching
        window.history.replaceState({}, document.title, "/onboarding/integrations");
      }
    };

    processIntegrations();

  }, [searchParams, getToken]);


  const handleConnect = async (tool: string) => {
    setIsConnecting(tool);
    const workspaceId = typeof window !== 'undefined' ? localStorage.getItem('agentos_workspace_id') : "default_workspace";
    const redirectUri = encodeURIComponent("https://agentos-frontend-azure.vercel.app/onboarding/integrations");

    // ==========================================
    // 1. 1-CLICK OAUTH 2.0 FLOWS (Enterprise)
    // ==========================================
    if (['GA4', 'Google Docs', 'Google Meet', 'YouTube'].includes(tool)) {
      localStorage.setItem('google_target_tool', tool);
      const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "YOUR_GOOGLE_CLIENT_ID";
      const scopes = encodeURIComponent("https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/analytics.readonly https://www.googleapis.com/auth/documents.readonly https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/youtube.readonly");
      window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scopes}&access_type=offline&prompt=consent&state=google_auth`;
      return;
    }

    if (tool === 'GitHub') { window.location.href = "https://github.com/apps/agentos-ai-cpo/installations/new"; return; }
    if (tool === 'GitLab') { const clientId = process.env.NEXT_PUBLIC_GITLAB_CLIENT_ID || "YOUR_GITLAB_CLIENT_ID"; window.location.href = `https://gitlab.com/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&state=gitlab_auth&scope=api`; return; }
    if (tool === 'Bitbucket') { const clientId = process.env.NEXT_PUBLIC_BITBUCKET_CLIENT_ID || "rsciGqcURXdJuSOljGHw0TJLdSwQYZD1"; window.location.href = `https://bitbucket.org/site/oauth2/authorize?client_id=${clientId}&response_type=code`; return; }
    if (tool === 'Jira') { const clientId = "zjaxoFFVOp1dhVrcWsoKqqrAfnMADIfq"; window.location.href = `https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id=${clientId}&scope=read%3Ajira-work%20write%3Ajira-work%20read%3Ajira-user&redirect_uri=${redirectUri}&state=jira_auth&response_type=code&prompt=consent`; return; }
    if (tool === 'Confluence') { const clientId = process.env.NEXT_PUBLIC_ATLASSIAN_CLIENT_ID || "YOUR_ATLASSIAN_CLIENT_ID"; window.location.href = `https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id=${clientId}&scope=read%3Aconfluence-content.summary%20read%3Aconfluence-space.summary&redirect_uri=${redirectUri}&state=confluence_auth&response_type=code&prompt=consent`; return; }
    if (tool === 'Slack') { const clientId = "11490498949286.11534438119542"; const scopes = "channels:history,channels:read,chat:write,groups:history,users:read"; window.location.href = `https://slack.com/oauth/v2/authorize?client_id=${clientId}&scope=${scopes}&redirect_uri=${redirectUri}&state=slack_auth`; return; }
    if (tool === 'Teams') { const clientId = process.env.NEXT_PUBLIC_TEAMS_CLIENT_ID || "YOUR_TEAMS_CLIENT_ID"; window.location.href = `https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=${clientId}&response_type=code&redirect_uri=${redirectUri}&response_mode=query&scope=offline_access%20Team.ReadBasic.All%20ChannelMessage.Read.All&state=teams_auth`; return; }
    if (tool === 'Zendesk') { const subdomain = window.prompt("Enter your Zendesk subdomain (e.g., if your URL is 'acme.zendesk.com', enter 'acme'):"); if (subdomain) { localStorage.setItem('temp_zendesk_subdomain', subdomain); const clientId = process.env.NEXT_PUBLIC_ZENDESK_CLIENT_ID || "YOUR_ZENDESK_CLIENT_ID"; window.location.href = `https://${subdomain}.zendesk.com/oauth/authorizations/new?response_type=code&client_id=${clientId}&redirect_uri=${redirectUri}&scope=read%20write`; } else { setIsConnecting(null); } return; }
    if (tool === 'Freshdesk') { const subdomain = window.prompt("Enter your Freshdesk subdomain (e.g., acme):"); if (subdomain) { localStorage.setItem('temp_freshdesk_subdomain', subdomain); const clientId = process.env.NEXT_PUBLIC_FRESHDESK_CLIENT_ID || "YOUR_FRESHDESK_CLIENT_ID"; window.location.href = `https://${subdomain}.freshdesk.com/oauth/authorize?client_id=${clientId}&response_type=code&redirect_uri=${redirectUri}&state=freshdesk_auth`; } else { setIsConnecting(null); } return; }
    if (tool === 'Salesforce' || tool === 'Salesforce Cases') { const clientId = process.env.NEXT_PUBLIC_SALESFORCE_CLIENT_ID || "YOUR_SALESFORCE_CLIENT_ID"; window.location.href = `https://login.salesforce.com/services/oauth2/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code`; return; }
    if (tool === 'HubSpot') { const clientId = process.env.NEXT_PUBLIC_HUBSPOT_CLIENT_ID || "YOUR_HUBSPOT_CLIENT_ID"; const scopes = encodeURIComponent("crm.objects.contacts.read crm.objects.deals.read"); window.location.href = `https://app.hubspot.com/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scopes}&state=hubspot_auth`; return; }
    if (tool === 'Intercom') { const clientId = process.env.NEXT_PUBLIC_INTERCOM_CLIENT_ID || "YOUR_INTERCOM_CLIENT_ID"; window.location.href = `https://app.intercom.com/oauth?client_id=${clientId}&state=intercom_auth`; return; }
    if (tool === 'Discord') { const clientId = process.env.NEXT_PUBLIC_DISCORD_CLIENT_ID || "YOUR_DISCORD_CLIENT_ID"; const scopes = encodeURIComponent("identify bot"); window.location.href = `https://discord.com/api/oauth2/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scopes}&state=discord_auth`; return; }
    if (tool === 'Reddit') { const clientId = process.env.NEXT_PUBLIC_REDDIT_CLIENT_ID || "YOUR_REDDIT_CLIENT_ID"; const scopes = encodeURIComponent("read identity"); window.location.href = `https://www.reddit.com/api/v1/authorize?client_id=${clientId}&response_type=code&state=reddit_auth&redirect_uri=${redirectUri}&duration=temporary&scope=${scopes}`; return; }
    if (tool === 'LinkedIn') { const clientId = process.env.NEXT_PUBLIC_LINKEDIN_CLIENT_ID || "YOUR_LINKEDIN_CLIENT_ID"; window.location.href = `https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=${clientId}&redirect_uri=${redirectUri}&state=linkedin_auth&scope=r_liteprofile%20r_emailaddress`; return; }
    if (tool === 'Gong') { const clientId = process.env.NEXT_PUBLIC_GONG_CLIENT_ID || "YOUR_GONG_CLIENT_ID"; window.location.href = `https://app.gong.io/oauth2/authorize?client_id=${clientId}&response_type=code&redirect_uri=${redirectUri}&state=gong_auth`; return; }
    if (tool === 'Linear') { const clientId = process.env.NEXT_PUBLIC_LINEAR_CLIENT_ID || "YOUR_LINEAR_CLIENT_ID"; window.location.href = `https://linear.app/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&state=linear_auth&scope=read`; return; }
    if (tool === 'Notion') { const clientId = process.env.NEXT_PUBLIC_NOTION_CLIENT_ID || "YOUR_NOTION_CLIENT_ID"; window.location.href = `https://api.notion.com/v1/oauth/authorize?client_id=${clientId}&response_type=code&owner=user&redirect_uri=${redirectUri}&state=notion_auth`; return; }
    if (tool === 'Zoom') { const clientId = process.env.NEXT_PUBLIC_ZOOM_CLIENT_ID || "YOUR_ZOOM_CLIENT_ID"; window.location.href = `https://zoom.us/oauth/authorize?response_type=code&client_id=${clientId}&redirect_uri=${redirectUri}&state=zoom_auth`; return; }

    // ==========================================
    // 2. DIRECT API FLOWS (NO OAUTH AVAILABLE)
    // ==========================================
    
    // ✅ Extracting token for Direct APIs
    const token = await getToken();
    const headersConfig = { 
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };

    const analyticsTools = ['Mixpanel', 'Amplitude'];
    if (analyticsTools.includes(tool)) {
      const apiKey = window.prompt(`Enter your ${tool} API Key / Token:`);
      if (!apiKey) { setIsConnecting(null); return; }
      const projectId = window.prompt(`Enter your ${tool} Project ID:`);
      if (!projectId) { setIsConnecting(null); return; }

      fetch('https://agentos-api-5suh.onrender.com/api/integrations/analytics/connect', {
        method: 'POST',
        headers: headersConfig, // ✅ Secure Header added
        body: JSON.stringify({ provider: tool.toLowerCase(), api_key: apiKey, project_id: projectId, workspace_id: workspaceId })
      }).then(res => res.json()).then(data => {
        if (data.status === 'connected') setConnectedTools(prev => [...prev, tool]);
      }).finally(() => setIsConnecting(null));
      return;
    }

    const monitoringTools = ['Datadog', 'Sentry', 'Crashlytics'];
    if (monitoringTools.includes(tool)) {
      const apiKey = window.prompt(`Enter your ${tool} API Token/Key:`);
      const orgSlug = window.prompt(`Enter your ${tool} Organization Slug/Project ID:`);
      if (!apiKey || !orgSlug) { setIsConnecting(null); return; }

      fetch('https://agentos-api-5suh.onrender.com/api/integrations/monitoring/connect', {
        method: 'POST',
        headers: headersConfig, // ✅ Secure Header added
        body: JSON.stringify({ provider: tool.toLowerCase(), api_key: apiKey, org_slug: orgSlug, workspace_id: workspaceId })
      }).then(res => res.json()).then(data => {
        if (data.status === 'connected') setConnectedTools(prev => [...prev, tool]);
      }).finally(() => setIsConnecting(null));
      return;
    }

    const reviewTools = ['App Store', 'Google Play', 'Chrome Extension'];
    if (reviewTools.includes(tool)) {
      const apiKey = window.prompt(`Enter your ${tool} API Key / Service JSON Token:`);
      const appId = window.prompt(`Enter your ${tool} App ID / Package Name:`);
      if (!apiKey || !appId) { setIsConnecting(null); return; }

      fetch('https://agentos-api-5suh.onrender.com/api/integrations/reviews/connect', {
        method: 'POST',
        headers: headersConfig, // ✅ Secure Header added
        body: JSON.stringify({ provider: tool.toLowerCase().replace(' ', '_'), api_key: apiKey, app_id: appId, workspace_id: workspaceId })
      }).then(res => res.json()).then(data => {
        if (data.status === 'connected') setConnectedTools(prev => [...prev, tool]);
      }).finally(() => setIsConnecting(null));
      return;
    }

    if (tool === 'Community Forum') {
      const domain = window.prompt(`Enter your Forum Domain:`);
      const apiKey = window.prompt(`Enter your Community API Key:`);
      if (!domain || !apiKey) { setIsConnecting(null); return; }
      fetch('https://agentos-api-5suh.onrender.com/api/integrations/community/connect', {
        method: 'POST',
        headers: headersConfig, // ✅ Secure Header added
        body: JSON.stringify({ api_key: apiKey, domain: domain, workspace_id: workspaceId })
      }).then(res => res.json()).then(data => {
        if (data.status === 'connected') setConnectedTools(prev => [...prev, tool]);
      }).finally(() => setIsConnecting(null));
      return;
    }

    if (tool === 'Twitter/X') {
      const bearerToken = window.prompt(`Enter your Twitter/X Bearer Token:`);
      if (!bearerToken) { setIsConnecting(null); return; }
      fetch('https://agentos-api-5suh.onrender.com/api/integrations/twitter/connect', {
        method: 'POST',
        headers: headersConfig, // ✅ Secure Header added
        body: JSON.stringify({ bearer_token: bearerToken, workspace_id: workspaceId })
      }).then(res => res.json()).then(data => {
        if (data.status === 'connected') setConnectedTools(prev => [...prev, tool]);
      }).finally(() => setIsConnecting(null));
      return;
    }

    if (tool === 'Email') {
      const provider = window.prompt("Enter Email Provider (e.g., Gmail or Outlook):");
      if (!provider) { setIsConnecting(null); return; }
      const appPassword = window.prompt(`Enter your ${provider} App Password / Access Token:`);
      if (!appPassword) { setIsConnecting(null); return; }

      fetch('https://agentos-api-5suh.onrender.com/api/integrations/email/connect', {
        method: 'POST',
        headers: headersConfig, // ✅ Secure Header added
        body: JSON.stringify({ provider: provider.toLowerCase(), access_token: appPassword, workspace_id: workspaceId })
      }).then(res => res.json()).then(data => {
        if (data.status === 'connected') setConnectedTools(prev => [...prev, tool]);
      }).finally(() => setIsConnecting(null));
      return;
    }

    // Default Fallback
    setTimeout(() => {
      setConnectedTools(prev => prev.includes(tool) ? prev : [...prev, tool]);
      setIsConnecting(null);
    }, 800);
  };

  const handleNext = () => {
    if (connectedTools.length === 0) {
      alert("Please connect at least one tool to train your AI Chief Product Officer.");
      return;
    }
    router.push('/onboarding/sync');
  };

  const INTEGRATION_CATEGORIES = [
    { title: 'Engineering', tools: ['GitHub', 'GitLab', 'Bitbucket', 'Jira', 'Linear'] },
    { title: 'Customer Support', tools: ['Zendesk', 'Intercom', 'Freshdesk', 'Salesforce Cases', 'HubSpot'] },
    { title: 'Communication', tools: ['Slack', 'Discord', 'Teams', 'Email'] },
    { title: 'Community', tools: ['Reddit', 'Twitter/X', 'LinkedIn', 'YouTube', 'Community Forum'] },
    { title: 'Reviews', tools: ['App Store', 'Google Play', 'Chrome Extension'] },
    { title: 'Analytics', tools: ['Mixpanel', 'Amplitude', 'GA4'] },
    { title: 'Monitoring', tools: ['Datadog', 'Sentry', 'Crashlytics'] },
    { title: 'Meetings', tools: ['Zoom', 'Google Meet', 'Gong'] },
    { title: 'CRM', tools: ['Salesforce', 'HubSpot'] },
    { title: 'Knowledge', tools: ['Notion', 'Confluence', 'Google Docs'] }
  ];

  return (
    <div className="min-h-screen bg-[#050505] text-white p-6 md:p-12 font-sans overflow-y-auto">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-block border border-gray-800 bg-[#111] px-4 py-1.5 rounded-full text-xs font-semibold tracking-widest text-gray-400 uppercase mb-4">
            Step 2 of 3
          </div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4 uppercase">
            Connect Your Company
          </h1>
          <p className="text-gray-400 text-lg">
            Select the tools your company uses. AgentOS will build a unified knowledge graph.
          </p>
        </div>

        <div className="columns-1 md:columns-2 lg:columns-3 gap-8 space-y-8">
          {INTEGRATION_CATEGORIES.map((category) => (
            <div key={category.title} className="break-inside-avoid bg-[#0a0a0a] border border-gray-800 p-6 rounded-2xl shadow-lg">
              <h2 className="text-sm font-semibold tracking-wider text-gray-500 uppercase border-b border-gray-800 pb-3 mb-4">
                {category.title}
              </h2>
              <div className="space-y-3">
                {category.tools.map((tool) => {
                  const isConnected = connectedTools.includes(tool);
                  const isLoading = isConnecting === tool;
                  return (
                    <div 
                      key={tool} 
                      className={`flex items-center justify-between p-3 rounded-xl border transition-all duration-200
                        ${isConnected 
                          ? 'border-green-500/30 bg-green-900/10' 
                          : 'border-gray-800 bg-[#111] hover:border-gray-600'}`}
                    >
                      <span className="font-medium text-gray-200">{tool}</span>
                      <button
                        onClick={() => handleConnect(tool)}
                        disabled={isConnected || isLoading}
                        className={`text-xs px-3 py-1.5 rounded-lg font-semibold transition-all flex items-center gap-1.5
                          ${isConnected 
                            ? 'bg-green-500/10 text-green-400 cursor-default border border-green-500/20' 
                            : 'bg-white text-black hover:bg-gray-200'}`}
                      >
                        {isLoading ? (
                          <span className="animate-pulse">Syncing...</span>
                        ) : isConnected ? (
                          <>
                            <CheckCircle2 size={14} /> Connected
                          </>
                        ) : (
                          <>
                            <LinkIcon size={14} /> Connect
                          </>
                        )}
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        <div className="sticky bottom-6 mt-12 bg-[#050505]/90 backdrop-blur-md border border-gray-800 p-6 rounded-2xl flex items-center justify-between shadow-2xl">
          <div>
            <p className="text-white font-semibold">{connectedTools.length} Tools Connected</p>
            <p className="text-gray-400 text-sm">AgentOS is ready to ingest data.</p>
          </div>
          <button 
            onClick={handleNext}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-lg flex items-center gap-2 transition-all duration-200"
          >
            Start Data Sync <ArrowRight size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}

export default function IntegrationsPage() {
  return (
    <Suspense fallback={<div className="text-white text-center p-10">Loading AgentOS Integrations...</div>}>
      <IntegrationsContent />
    </Suspense>
  );
}