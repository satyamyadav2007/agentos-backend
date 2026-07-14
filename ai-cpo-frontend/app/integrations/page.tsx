"use client";

import { UserButton, useUser } from "@clerk/nextjs";
import { Code, Hash, MessageSquare, Database, CheckCircle, ArrowRight, Plug, UploadCloud, FileText } from "lucide-react";
import Link from "next/link";
import Nango from '@nangohq/frontend';
import { useEffect, useState } from 'react';

export default function IntegrationsPage() {
  const { user } = useUser();
  const [connecting, setConnecting] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  
  // ⚡ Initialize Nango (Replace with your actual Nango Public Key)
  const nango = new Nango({
  publicKey: process.env.NEXT_PUBLIC_NANGO_PUBLIC_KEY!,
});

  // ⚡ THE REAL NANGO AUTH FLOW
  const handleConnect = async (provider: string) => {
    setConnecting(provider);
    
    try {
      // provider config key Nango dashboard se aati hai (e.g., 'github-integration', 'jira')
      const providerConfigKey = provider.toLowerCase(); 
      const connectionId = `${user?.id || 'demo-user'}-${providerConfigKey}`;

      // Yeh line Nango ka asli login popup open karegi!
      const result = await nango.auth(providerConfigKey, connectionId);
      
      alert(`✅ Success: ${provider} connected perfectly!`);
      
      // Optional: Backend ko bata do ki naya connection ban gaya hai
      // fetch('/api/nango-webhook', { ... })
      
    } catch (error) {
      console.error("Nango Auth Error:", error);
      alert(`🚨 Failed to connect ${provider}. Check console for details.`);
    } finally {
      setConnecting(null);
    }
  };
  // ⚡ Naya function file backend ko bhejne ke liye
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      alert(data.message);
    } catch (error) {
      alert("🚨 Upload failed. Is the backend running?");
    } finally {
      setIsUploading(false);
    }
  };

 
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-8 transition-colors duration-200">
      
      {/* Top Nav */}
      <div className="flex justify-between items-center mb-12">
        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600 flex items-center gap-3">
          <Plug className="h-8 w-8 text-blue-600" /> Workspace Integrations
        </h1>
        <div className="flex items-center gap-6">
          <Link href="/" className="text-sm font-bold text-gray-500 hover:text-blue-600 transition-colors">
            Go to Dashboard <ArrowRight className="inline h-4 w-4" />
          </Link>
          <UserButton />
        </div>
      </div>

      <div className="max-w-5xl mx-auto">
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-2">Connect Your Data Sources</h2>
          <p className="text-gray-500 dark:text-gray-400">AgentOS needs access to your tools to autonomously fetch bugs, support tickets, and revenue data.</p>
        </div>

        {/* Integration Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* GitHub Integration */}
          <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700 flex flex-col justify-between">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-gray-100 dark:bg-gray-700 rounded-lg"><Code className="h-8 w-8" /></div>
                <div>
                  <h3 className="text-lg font-bold">GitHub Enterprise</h3>
                  <p className="text-sm text-gray-500">Sync Repos, Issues, and PRs</p>
                </div>
              </div>
            </div>
            <button 
              onClick={() => handleConnect('GitHub')}
              className="w-full mt-4 bg-gray-900 dark:bg-gray-100 hover:bg-gray-800 dark:hover:bg-white text-white dark:text-gray-900 font-bold py-2 rounded-lg transition-colors flex justify-center items-center gap-2"
            >
              {connecting === 'GitHub' ? "Connecting..." : "Connect GitHub"}
            </button>
          </div>

          {/* Zendesk Integration */}
          <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700 flex flex-col justify-between">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-lg"><MessageSquare className="h-8 w-8" /></div>
                <div>
                  <h3 className="text-lg font-bold">Zendesk Support</h3>
                  <p className="text-sm text-gray-500">Ingest Customer Tickets</p>
                </div>
              </div>
            </div>
            <button 
              onClick={() => handleConnect('Zendesk')}
              className="w-full mt-4 border-2 border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-500 font-bold py-2 rounded-lg transition-colors"
            >
              {connecting === 'Zendesk' ? "Connecting..." : "Connect Zendesk"}
            </button>
          </div>

          {/* Salesforce / HubSpot */}
          <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700 flex flex-col justify-between">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg"><Database className="h-8 w-8" /></div>
                <div>
                  <h3 className="text-lg font-bold">Salesforce / HubSpot</h3>
                  <p className="text-sm text-gray-500">Map Bugs to Revenue Risk (ARR)</p>
                </div>
              </div>
            </div>
            <button 
              onClick={() => handleConnect('CRM')}
              className="w-full mt-4 border-2 border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-500 font-bold py-2 rounded-lg transition-colors"
            >
               {connecting === 'CRM' ? "Connecting..." : "Connect CRM"}
            </button>
          </div>

          {/* Slack Integration */}
          <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700 flex flex-col justify-between">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-lg"><Hash className="h-8 w-8" /></div>
                <div>
                  <h3 className="text-lg font-bold">Slack Workspace</h3>
                  <p className="text-sm text-gray-500">Push Alerts & AI Summaries</p>
                </div>
              </div>
            </div>
            <button 
              onClick={() => handleConnect('Slack')}
              className="w-full mt-4 border-2 border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-500 font-bold py-2 rounded-lg transition-colors"
            >
               {connecting === 'Slack' ? "Connecting..." : "Connect Slack"}
            </button>
          </div>

        </div> {/* End of Integrations Grid */}

        {/* ⚡ PHASE 4: SMB MANUAL UPLOAD ZONE */}
        <div className="mt-12 p-10 border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-2xl bg-gray-50 dark:bg-gray-800/30 text-center transition-all hover:bg-gray-100 dark:hover:bg-gray-800/70">
          <UploadCloud className="h-16 w-16 mx-auto text-blue-500 mb-4 animate-bounce" />
          <h3 className="text-2xl font-bold mb-2">SMB Fallback: Manual Data Ingestion</h3>
          <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-xl mx-auto">
            Don't use GitHub or Zendesk? No problem. Upload your raw CSV, Excel, or crash log files directly. AgentOS will automatically parse, clean, and analyze the data.
          </p>
          
          <label className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-xl cursor-pointer transition-colors inline-flex items-center gap-2 shadow-lg hover:shadow-xl">
            {isUploading ? "Uploading & Parsing..." : <><FileText className="h-5 w-5" /> Browse Files (CSV, TXT, LOG)</>}
            <input 
              type="file" 
              className="hidden" 
              accept=".csv,.txt,.log" 
              onChange={handleFileUpload} 
              disabled={isUploading}
            />
          </label>
        </div>
      </div>
    </div>  
  );
}