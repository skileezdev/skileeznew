"use client";

import { useAuth } from "@/context/AuthContext";
import Link from "next/link";

export default function DashboardPage() {
    const { user, logout } = useAuth();

    return (
        <div className="min-h-screen bg-gray-50 flex">
            {/* Sidebar navigation */}
            <aside className="w-64 bg-white border-r border-gray-200 p-6 flex flex-col">
                <div className="text-2xl font-black text-indigo-600 mb-10">SKILEEZ V2</div>
                <nav className="flex-1 space-y-2">
                    <Link href="/dashboard" className="block px-4 py-3 bg-indigo-50 text-indigo-700 rounded-xl font-bold transition">
                        Dashboard
                    </Link>
                    <Link href="/marketplace" className="block px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-xl transition">
                        Marketplace
                    </Link>
                    <Link href="/dashboard/contracts" className="block px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-xl transition">
                        My Contracts
                    </Link>
                </nav>
                <button
                    onClick={logout}
                    className="mt-auto px-4 py-3 text-red-500 hover:bg-red-50 rounded-xl font-bold text-left transition"
                >
                    Logout
                </button>
            </aside>

            {/* Main Content */}
            <main className="flex-1 p-10">
                <header className="flex justify-between items-center mb-12">
                    <div>
                        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">
                            Welcome back, <span className="text-indigo-600">{user?.first_name || 'learner'}</span>!
                        </h1>
                        <p className="text-gray-500 mt-2 text-lg">Your learning journey continues here.</p>
                    </div>
                    <div className="w-14 h-14 bg-indigo-100 rounded-2xl flex items-center justify-center text-indigo-600 text-xl font-black shadow-inner">
                        {user?.email?.[0]?.toUpperCase() || 'U'}
                    </div>
                </header>

                <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {/* Active Progress Card */}
                    <div className="bg-white p-8 rounded-[2rem] shadow-sm border border-gray-100 flex flex-col justify-between">
                        <div>
                            <h3 className="text-gray-400 font-bold uppercase text-xs tracking-widest mb-4">Active Progress</h3>
                            <div className="text-4xl font-black text-gray-900">0 Contracts</div>
                        </div>
                        <p className="text-sm text-gray-500 mt-6">Accept a proposal to start a new learning contract.</p>
                    </div>

                    {/* Action Card */}
                    <Link href="/marketplace" className="bg-indigo-600 p-8 rounded-[2rem] shadow-xl shadow-indigo-100 hover:scale-[1.02] transition-transform duration-300 group">
                        <h3 className="text-indigo-200 font-bold uppercase text-xs tracking-widest mb-4">Marketplace</h3>
                        <div className="text-4xl font-black text-white group-hover:translate-x-1 transition-transform">Find a Coach</div>
                        <p className="text-sm text-indigo-100 mt-6 opacity-80">Browse learning requests and share your expertise with others.</p>
                    </Link>

                    {/* Feature Teaser Card */}
                    <div className="bg-white p-8 rounded-[2rem] shadow-sm border border-gray-100 flex flex-col justify-center items-center text-center">
                        <div className="w-20 h-20 bg-gray-50 rounded-[1.5rem] flex items-center justify-center mb-6 text-4xl shadow-inner">📹</div>
                        <p className="text-sm font-bold text-gray-400 tracking-wide uppercase">Integrated Video System</p>
                        <p className="text-xs text-gray-300 mt-2 italic">Coming in the next phase...</p>
                    </div>
                </section>

                {/* Recent Activity Placeholder */}
                <div className="mt-12 bg-white/50 backdrop-blur-sm p-8 rounded-[2rem] border border-gray-100 border-dashed">
                    <p className="text-gray-400 text-center font-medium">Your recent session activity will appear here.</p>
                </div>
            </main>
        </div>
    );
}
