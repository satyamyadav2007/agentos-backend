'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, Sparkles, Loader2, AlertCircle } from 'lucide-react';
import { useAuth } from '@clerk/nextjs';

export default function CreateWorkspace() {
  const router = useRouter();
  const { getToken } = useAuth();
  
  // Enterprise UI States
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loadingText, setLoadingText] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const [formData, setFormData] = useState({
    companyName: '',
    industry: '',
    companySize: '',
    region: ''
  });

  const handleNext = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMsg('');
    setLoadingText('Bootstrapping Workspace...');
    
    try {
      const token = await getToken();
      
      // ⚡ ENTERPRISE FIX: Use Environment Variable, fallback to localhost for dev
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      const response = await fetch(`${API_URL}/api/workspaces`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        // ⚡ CRITICAL FIX: Mapped 'companySize' to 'size' so FastAPI accepts it
        body: JSON.stringify({
          companyName: formData.companyName,
          industry: formData.industry,
          companySize: formData.companySize, 
          region: formData.region
        })
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || 'Failed to create workspace');
      }

      setLoadingText('Workspace Created!');
      
      // ⚡ CRITICAL: Save Workspace ID for the next steps (Integrations/Sync)
      if (result.data?.workspace_id) {
        localStorage.setItem('agentos_workspace_id', result.data.workspace_id);
        localStorage.setItem('agentos_org_id', result.data.organization_id);
      }

      // Short delay for UX smoothness
      setTimeout(() => {
        router.push('/onboarding/integrations'); 
      }, 800);
      
    } catch (error: any) {
      console.error("🚨 Error saving workspace:", error);
      // ⚡ ENTERPRISE FIX: In-UI error instead of alert()
      setErrorMsg(error.message || "Failed to connect to AI Kernel. Please try again.");
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white flex flex-col items-center justify-center p-6 font-sans">
      
      {/* Top Header */}
      <div className="text-center mb-12">
        <div className="flex justify-center mb-4">
          <div className="bg-blue-600/10 p-3 rounded-2xl border border-blue-500/20">
            <Sparkles className="text-blue-500 h-8 w-8" />
          </div>
        </div>
        <h1 className="text-3xl md:text-5xl font-bold tracking-tight mb-3">
          Welcome to AgentOS
        </h1>
        <p className="text-gray-400 text-lg md:text-xl tracking-wide uppercase">
          Your AI Chief Product Officer
        </p>
      </div>

      {/* The Form */}
      <div className="w-full max-w-md bg-[#0f0f0f] border border-gray-800 p-8 rounded-2xl shadow-2xl relative overflow-hidden">
        
        {/* Error Toast Setup */}
        {errorMsg && (
          <div className="mb-6 p-3 bg-red-500/10 border border-red-500/50 rounded-lg flex items-center gap-3 text-red-400 text-sm">
            <AlertCircle size={16} />
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleNext} className="space-y-6 relative z-10">
          
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Company Name</label>
            <input 
              required
              disabled={isSubmitting}
              type="text" 
              className="w-full bg-[#151515] border border-gray-700 focus:border-blue-500 rounded-xl px-4 py-3 text-white outline-none transition-all disabled:opacity-50"
              placeholder="e.g. Netflix, Stripe"
              value={formData.companyName}
              onChange={(e) => setFormData({...formData, companyName: e.target.value})}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Industry</label>
            <select 
              required
              disabled={isSubmitting}
              className="w-full bg-[#151515] border border-gray-700 focus:border-blue-500 rounded-xl px-4 py-3 text-white outline-none transition-all appearance-none disabled:opacity-50"
              value={formData.industry}
              onChange={(e) => setFormData({...formData, industry: e.target.value})}
            >
              <option value="" disabled>Select an industry...</option>
              <option value="software">Software / SaaS</option>
              <option value="ecommerce">E-Commerce</option>
              <option value="fintech">Fintech</option>
              <option value="healthcare">Healthcare</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">Size</label>
              <select 
                required
                disabled={isSubmitting}
                className="w-full bg-[#151515] border border-gray-700 focus:border-blue-500 rounded-xl px-4 py-3 text-white outline-none transition-all appearance-none disabled:opacity-50"
                value={formData.companySize}
                onChange={(e) => setFormData({...formData, companySize: e.target.value})}
              >
                <option value="" disabled>Size...</option>
                <option value="1-10">1-10</option>
                <option value="11-50">11-50</option>
                <option value="51-200">51-200</option>
                <option value="201+">201+</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">Region</label>
              <select 
                required
                disabled={isSubmitting}
                className="w-full bg-[#151515] border border-gray-700 focus:border-blue-500 rounded-xl px-4 py-3 text-white outline-none transition-all appearance-none disabled:opacity-50"
                value={formData.region}
                onChange={(e) => setFormData({...formData, region: e.target.value})}
              >
                <option value="" disabled>Region...</option>
                <option value="na">North America</option>
                <option value="eu">Europe</option>
                <option value="apac">APAC</option>
                <option value="global">Global</option>
              </select>
            </div>
          </div>

          <button 
            type="submit" 
            disabled={isSubmitting}
            className="w-full mt-4 bg-white text-black font-bold py-3.5 rounded-xl flex items-center justify-center gap-2 hover:bg-gray-200 transition-all disabled:bg-gray-300"
          >
            {isSubmitting ? (
              <>
                <Loader2 size={18} className="animate-spin" /> {loadingText}
              </>
            ) : (
              <>
                Initialize Workspace <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}