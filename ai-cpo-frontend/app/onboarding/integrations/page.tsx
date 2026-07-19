'use client';
import { useAuth } from '@clerk/nextjs';
import { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { CheckCircle2, ArrowRight, Link as LinkIcon } from 'lucide-react';

// Agar tum Clerk use kar rahe ho token ke liye, toh isey uncomment kar lena:
// import { useAuth } from '@clerk/nextjs';

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

function IntegrationsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  // States
  const [connectedTools, setConnectedTools] = useState<string[]>([]);
  const [isConnecting, setIsConnecting] = useState<string | null>(null);

  // Fallback for getToken if not using Clerk. Replace with your auth method if needed.
  // const { getToken } = useAuth(); 
  const { getToken } = useAuth();

  // ==========================================
  // ⚡ MASTER CALLBACK HANDLER (OAuth Returns)
  // ==========================================
  useEffect(() => {
    const oauthToolMap: Record<string, string> = {
      'jira_auth': 'Jira', 'slack_auth': 'Slack', 'hubspot_auth': 'HubSpot',
      'intercom_auth': 'Intercom', 'discord_auth': 'Discord', 'reddit_auth': 'Reddit',
      'gitlab_auth': 'GitLab', 'teams_auth': 'Teams', 'linkedin_auth': 'LinkedIn',
      'gong_auth': 'Gong', 'linear_auth': 'Linear', 'notion_auth': 'Notion',
      'confluence_auth': 'Confluence', 'zoom_auth': 'Zoom'
    };

    const workspaceId = typeof window !== 'undefined' ? localStorage.getItem('agentos_workspace_id') : null;
    const authCode = searchParams.get('code');
    const state = searchParams.get('state');
    const installationId = searchParams.get('installation_id');

    if (!installationId && !authCode) return;

    if (!workspaceId || workspaceId === 'default_workspace') {
      console.error("🚨 Invalid Workspace ID found in localStorage:", workspaceId);
      return;
    }

    const processIntegrations = async () => {
      try {
        const token = await getToken();
        if (!token) throw new Error("Authentication token missing!");

        let fetchUrl = '';
        let fetchBody: any = {};
        let currentToolName = '';

        if (installationId) {
          fetchUrl = `https://agentos-api-5suh.onrender.com/api/integrations/github/connect`;
          fetchBody = { installation_id: installationId, workspace_id: workspaceId };
          currentToolName = 'GitHub';
        } 
        else if (state === 'google_auth') {
          const targetTool = localStorage.getItem('google_target_tool') || 'Google';
          fetchUrl = `https://agentos-api-5suh.onrender.com/api/integrations/google/connect`;
          fetchBody = { auth_code: authCode, workspace_id: workspaceId, target: targetTool };
          currentToolName = targetTool;
        }
        else if (state === 'freshdesk_auth') {
          const freshdeskSubdomain = localStorage.getItem('temp_freshdesk_subdomain');
          fetchUrl = `https://agentos-api-5suh.onrender.com/api/integrations/freshdesk/connect`;
          fetchBody = { auth_code: authCode, workspace_id: workspaceId, subdomain: freshdeskSubdomain };
          currentToolName = 'Freshdesk';
        }
        else if (state && oauthToolMap[state]) {
          currentToolName = oauthToolMap[state];
          const endpoint = currentToolName.toLowerCase();
          fetchUrl = `https://agentos-api-5suh.onrender.com/api/integrations/${endpoint}/connect`;
          // Added redirect_uri as defensive mechanism for backend validation
          const redirectUri = typeof window !== 'undefined' ? window.location.origin + "/onboarding/integrations" : "";
          fetchBody = { auth_code: authCode, workspace_id: workspaceId, redirect_uri: redirectUri };
        }
        else if (!state && localStorage.getItem('temp_zendesk_subdomain')) {
          const zendeskSubdomain = localStorage.getItem('temp_zendesk_subdomain');
          fetchUrl = `https://agentos-api-5suh.onrender.com/api/integrations/zendesk/connect`;
          fetchBody = { auth_code: authCode, workspace_id: workspaceId, subdomain: zendeskSubdomain };
          currentToolName = 'Zendesk';
        }
        else if (!state && !localStorage.getItem('temp_zendesk_subdomain')) {
          fetchUrl = `https://agentos-api-5suh.onrender.com/api/integrations/salesforce/connect`;
          fetchBody = { auth_code: authCode, workspace_id: workspaceId };
          currentToolName = 'Salesforce';
        }

        if (fetchUrl && currentToolName) {
          console.log(`🔗 Sending ${currentToolName} Auth Code to backend...`);
          const response = await fetch(fetchUrl, {
            method: 'POST',
            headers: { 
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}` 
            },
            body: JSON.stringify(fetchBody)
          });

          const data = await response.json();

          if (response.ok && data.status === 'connected') {
            console.log(`✅ ${currentToolName} Connected Successfully!`);
            setConnectedTools(prev => prev.includes(currentToolName) ? prev : [...prev, currentToolName]);
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
        window.history.replaceState({}, document.title, "/onboarding/integrations");
      }
    };

    processIntegrations();
  }, [searchParams]);

  // ==========================================
  // 🚀 CONNECTION HANDLER (Outbound & API Flows)
  // ==========================================
  const handleConnect = async (toolName: string) => {
    setIsConnecting(toolName);
    const workspaceId = typeof window !== 'undefined' ? localStorage.getItem('agentos_workspace_id') : "default_workspace";
    const redirectUri = encodeURIComponent("https://agentos-frontend-azure.vercel.app/onboarding/integrations");

    // --- 1-CLICK OAUTH 2.0 FLOWS ---
    if (['GA4', 'Google Docs', 'Google Meet', 'YouTube'].includes(toolName)) {
      localStorage.setItem('google_target_tool', toolName);
      const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "YOUR_GOOGLE_CLIENT_ID";
      const scopes = encodeURIComponent("https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/analytics.readonly https://www.googleapis.com/auth/documents.readonly https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/youtube.readonly");
      window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scopes}&access_type=offline&prompt=consent&state=google_auth`;
      return;
    }

    if (toolName === "GitHub") {
      window.location.href = "https://github.com/apps/agentos-ai-cpo/installations/new";
      return;
    } 
    
    if (toolName === "Jira") {
      const clientId = "zjaxoFFVOp1dhVrcWsoKqqrAfnMADIfq"; 
      const jiraAuthUrl = `https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id=zjaxoFFVOp1dhVrcWsoKqqrAfnMADIfq&scope=read%3Ajira-work%20write%3Ajira-work%20read%3Ajira-user%20read%3Aboard-scope%3Ajira-software%20read%3Asprint%3Ajira-software%20offline_access&redirect_uri=https%3A%2F%2Fagentos-frontend-azure.vercel.app%2Fonboarding%2Fintegrations&state=${YOUR_USER_BOUND_VALUE}&response_type=code&prompt=consent`;
      window.location.href = jiraAuthUrl;
      return;
    } 
    
    if (toolName === 'Slack') {
      const clientId = "11490498949286.11534438119542"; 
      const scopes = "channels:history,channels:read,chat:write,groups:history,users:read";
      const slackAuthUrl = `https://slack.com/oauth/v2/authorize?client_id=${clientId}&scope=${scopes}&redirect_uri=${redirectUri}&state=slack_auth`;
      window.location.href = slackAuthUrl;
      return;
    }
    
    if (toolName === "Zendesk") {
      const subdomain = window.prompt("Enter your Zendesk subdomain (e.g., if your URL is 'acme.zendesk.com', enter 'acme'):");
      if (subdomain) {
        localStorage.setItem('temp_zendesk_subdomain', subdomain);
        const clientId = "YOUR_ZENDESK_CLIENT_ID";
        const zendeskAuthUrl = `https://${subdomain}.zendesk.com/oauth/authorizations/new?response_type=code&client_id=${clientId}&redirect_uri=${redirectUri}&scope=read%20write`;
        window.location.href = zendeskAuthUrl;
      } else {
        setIsConnecting(null);
      }
      return;
    }  
    
    if (toolName === 'Salesforce' || toolName === 'Salesforce Cases') {
      const clientId = process.env.NEXT_PUBLIC_SALESFORCE_CLIENT_ID || "TUMHARA_SALESFORCE_CLIENT_ID";
      const salesforceAuthUrl = `https://login.salesforce.com/services/oauth2/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code`;
      window.location.href = salesforceAuthUrl;
      return;
    }
    
    if (toolName === 'HubSpot') {
      const clientId = process.env.NEXT_PUBLIC_HUBSPOT_CLIENT_ID || "YOUR_HUBSPOT_CLIENT_ID";
      const scopes = encodeURIComponent("crm.objects.contacts.read crm.objects.deals.read");
      const hubspotAuthUrl = `https://app.hubspot.com/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scopes}&state=hubspot_auth`;
      window.location.href = hubspotAuthUrl;
      return;
    }
    
    if (toolName === 'Intercom') {
      const clientId = process.env.NEXT_PUBLIC_INTERCOM_CLIENT_ID || "YOUR_INTERCOM_CLIENT_ID";
      const stateParam = "intercom_auth";
      const intercomAuthUrl = `https://app.intercom.com/oauth?client_id=${clientId}&state=${stateParam}`;
      window.location.href = intercomAuthUrl;
      return;
    }
    
    if (toolName === 'Discord') {
      const clientId = process.env.NEXT_PUBLIC_DISCORD_CLIENT_ID || "YOUR_DISCORD_CLIENT_ID";
      const scopes = encodeURIComponent("identify bot");
      const stateParam = "discord_auth";
      const discordAuthUrl = `https://discord.com/api/oauth2/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scopes}&state=${stateParam}`;
      window.location.href = discordAuthUrl;
      return;
    }
    
    if (toolName === 'Reddit') {
      const clientId = process.env.NEXT_PUBLIC_REDDIT_CLIENT_ID || "YOUR_REDDIT_CLIENT_ID";
      const scopes = encodeURIComponent("read identity");
      const stateParam = "reddit_auth";
      const redditAuthUrl = `https://www.reddit.com/api/v1/authorize?client_id=${clientId}&response_type=code&state=${stateParam}&redirect_uri=${redirectUri}&duration=temporary&scope=${scopes}`;
      window.location.href = redditAuthUrl;
      return;
    }

    // --- API KEY / TOKEN FLOWS ---
    const analyticsTools = ['PostHog', 'Mixpanel', 'Amplitude'];
    if (analyticsTools.includes(toolName)) {
      const apiKey = window.prompt(`Enter your ${toolName} API Key / Token (for Amplitude format as API_KEY:SECRET_KEY):`);
      if (!apiKey) { setIsConnecting(null); return; }
      const projectId = window.prompt(`Enter your ${toolName} Project ID:`);
      if (!projectId) { setIsConnecting(null); return; }

      fetch('https://agentos-api-5suh.onrender.com/api/integrations/analytics/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: toolName.toLowerCase(), api_key: apiKey, project_id: projectId, workspace_id: workspaceId })
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'connected') setConnectedTools(prev => [...prev, toolName]);
        else alert(`Failed: ${data.message}`);
      })
      .finally(() => setIsConnecting(null));
      return;
    }

    const crashTools = ['Sentry', 'Crashlytics'];
    if (crashTools.includes(toolName)) {
      const apiKey = window.prompt(`Enter your ${toolName} API Token / Service Key:`);
      if (!apiKey) { setIsConnecting(null); return; }
      const orgSlug = window.prompt(`Enter your ${toolName} Organization Slug (or GCP Project ID):`);
      if (!orgSlug) { setIsConnecting(null); return; }
      const projectSlug = window.prompt(`Enter your ${toolName} Project Slug (or Firebase App ID):`);
      if (!projectSlug) { setIsConnecting(null); return; }

      fetch('https://agentos-api-5suh.onrender.com/api/integrations/crashes/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: toolName.toLowerCase(), api_key: apiKey, org_slug: orgSlug, project_slug: projectSlug, workspace_id: workspaceId })
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'connected') setConnectedTools(prev => [...prev, toolName]);
      })
      .finally(() => setIsConnecting(null));
      return;
    }

    if (toolName === 'Linear') {
      const apiKey = window.prompt(`Enter your Linear Personal API Key:`);
      if (!apiKey) { setIsConnecting(null); return; }
      fetch('https://agentos-api-5suh.onrender.com/api/integrations/linear/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey, workspace_id: workspaceId })
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'connected') setConnectedTools(prev => [...prev, toolName]);
      })
      .finally(() => setIsConnecting(null));
      return;
    }

    if (toolName === 'Datadog') {
      const site = window.prompt(`Enter your Datadog Site (e.g., datadoghq.com):`) || "datadoghq.com";
      const apiKey = window.prompt(`Enter your Datadog API Key:`);
      if (!apiKey) { setIsConnecting(null); return; }
      const appKey = window.prompt(`Enter your Datadog Application Key:`);
      if (!appKey) { setIsConnecting(null); return; }

      fetch('https://agentos-api-5suh.onrender.com/api/integrations/datadog/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey, app_key: appKey, site: site, workspace_id: workspaceId })
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'connected') setConnectedTools(prev => [...prev, toolName]);
      })
      .finally(() => setIsConnecting(null));
      return;
    }

    if (toolName === 'Notion' || toolName === 'Confluence') {
      const providerMap: Record<string, string> = { 'Notion': 'notion', 'Confluence': 'confluence' };
      const providerId = providerMap[toolName];
      const token = window.prompt(`Enter your ${toolName} API Token / Integration Secret:`);
      if (!token) { setIsConnecting(null); return; }

      fetch('https://agentos-api-5suh.onrender.com/api/integrations/knowledge/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: providerId, token: token, workspace_id: workspaceId })
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'connected') setConnectedTools(prev => [...prev, toolName]);
      })
      .finally(() => setIsConnecting(null));
      return;
    }

    // Default fallback if tool logic isn't fully implemented yet
    console.log(`Mock connecting ${toolName}...`);
    setTimeout(() => {
      setConnectedTools(prev => [...prev, toolName]);
      setIsConnecting(null);
    }, 1500);
  };

  /// ==========================================
  // 🚀 START DATA SYNC (Mission Control Trigger)
  // ==========================================
  const handleNext = async () => {
    try {
      // 1. Clerk se fresh token lo
      const token = await getToken();
      const workspaceId = typeof window !== 'undefined' ? localStorage.getItem('agentos_workspace_id') : "default_workspace";

      if (!token) {
        console.error("🚨 Auth Token missing!");
        return;
      }

      console.log("🚀 Initiating Mission Control Sync...");

      // 2. Backend ko token ke sath Secure Request bhejo
      const response = await fetch('https://agentos-api-5suh.onrender.com/api/sync/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` // ⚡ Ye line 401 error ko fix karegi
        },
        body: JSON.stringify({
          workspace_id: workspaceId,
          integrations: connectedTools
        })
      });

      if (!response.ok) {
        console.error("🚨 Backend rejected sync start:", await response.text());
      } else {
        console.log("✅ Sync started successfully on backend!");
      }

    } catch (error) {
      console.error("🚨 Error triggering sync:", error);
    } finally {
      // 3. Sab hone ke baad user ko Sync Page par bhej do
      router.push('/onboarding/sync');
    }
  };

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
            disabled={connectedTools.length === 0}
            className={`font-semibold px-6 py-3 rounded-lg flex items-center gap-2 transition-all duration-200
              ${connectedTools.length > 0 
                ? 'bg-blue-600 hover:bg-blue-700 text-white cursor-pointer' 
                : 'bg-gray-800 text-gray-500 cursor-not-allowed'}`}
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