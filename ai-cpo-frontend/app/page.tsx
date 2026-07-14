import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import { SignInButton } from '@clerk/nextjs';

// ⚡ FIX 1: Yahan 'async' add kiya
export default async function LandingPage() {
  
  // ⚡ FIX 2: Yahan 'await' add kiya
  const { userId } = await auth();

  // Agar user logged in hai, toh purana UI mat dikhao! Seedha Onboarding flow par bhej do.
  if (userId) {
    redirect('/onboarding');
  }

  // Agar user logged in NAHI hai, toh usko Login page/button dikhao...........
  return (
    <div className="min-h-screen bg-[#050505] text-white flex flex-col items-center justify-center p-6 text-center">
      <h1 className="text-5xl md:text-7xl font-black mb-6 tracking-tight">
        Agent<span className="text-blue-500">OS</span>
      </h1>
      <p className="text-gray-400 text-xl mb-10 max-w-2xl">
        The AI Chief Product Officer for Enterprise. Connect your data, find root causes, and protect your revenue automatically.
      </p>
      
      <SignInButton mode="modal" fallbackRedirectUrl="/onboarding">
        <button className="bg-blue-600 hover:bg-blue-500 text-white font-bold py-4 px-10 rounded-full transition-all text-lg shadow-[0_0_20px_rgba(37,99,235,0.4)] hover:shadow-[0_0_30px_rgba(37,99,235,0.6)]">
          Login / Get Started
        </button>
      </SignInButton>
    </div>
  );
}