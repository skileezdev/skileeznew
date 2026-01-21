"use client";

import { useAuth } from "@/context/AuthContext";
import { useState, useEffect } from "react";
import Link from "next/link";
import api from "@/lib/api";
import {
    LayoutDashboard,
    ShoppingBag,
    FileText,
    RotateCcw,
    LogOut,
    ChevronRight,
    Calendar,
    Clock,
    Award,
    TrendingUp,
    MessageCircle,
    Bell
} from "lucide-react";
import RecentActivity from "@/components/dashboard/RecentActivity";
import UpcomingSessions from "@/components/dashboard/UpcomingSessions";
import PendingItems from "@/components/dashboard/PendingItems";

export default function DashboardPage() {
    const { user, logout, switchRole } = useAuth();
    const [stats, setStats] = useState({ contracts: 0, sessions: 0 });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await api.get("/contracts");
                setStats({
                    contracts: res.data.length,
                    sessions: res.data.reduce((acc: number, c: any) => acc + (c.total_sessions - c.completed_sessions), 0)
                });
            } catch (err) {
                console.error("Failed to fetch dashboard stats", err);
            } finally {
                setLoading(false);
            }
        };
        if (user) fetchStats();
    }, [user]);

    const handleRoleSwitch = async () => {
        const target = user?.current_role === "student" ? "coach" : "student";
        await switchRole(target);
    };

    return (
        <div className="min-h-screen bg-[#FDFDFF] flex font-inter">
            {/* Sidebar with Glassmorphism */}
            <aside className="w-72 bg-white/80 backdrop-blur-md border-r border-gray-100 p-8 flex flex-col sticky top-0 h-screen z-10">
                <div className="flex items-center gap-2 mb-12">
                    <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-purple-600 rounded-xl shadow-lg shadow-primary-200 flex items-center justify-center text-white font-black text-xl">S</div>
                    <span className="text-xl font-black bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-600">SKILEEZ</span>
                </div>

                <nav className="flex-1 space-y-1">
                    <Link href="/dashboard" className="flex items-center gap-3 px-5 py-3 bg-primary-50 text-primary-600 rounded-2xl font-bold transition-all shadow-sm shadow-primary-100/50 group">
                        <LayoutDashboard size={20} className="group-hover:scale-110 transition-transform" />
                        Dashboard
                    </Link>
                    <Link href="/marketplace" className="flex items-center gap-3 px-5 py-3 text-gray-500 hover:bg-gray-50 hover:text-gray-900 rounded-2xl font-semibold transition-all group">
                        <ShoppingBag size={20} className="group-hover:rotate-12 transition-transform" />
                        Marketplace
                    </Link>
                    <Link href="/dashboard/contracts" className="flex items-center gap-3 px-5 py-3 text-gray-500 hover:bg-gray-50 hover:text-gray-900 rounded-2xl font-semibold transition-all group">
                        <FileText size={20} className="group-hover:scale-110 transition-transform" />
                        My Contracts
                    </Link>
                </nav>

                <div className="mt-auto space-y-4">
                    {/* Role Swapper Widget */}
                    <div className="p-4 bg-gray-50 rounded-2xl border border-gray-100">
                        <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3">Current Role</p>
                        <div className="flex items-center justify-between">
                            <span className="font-bold text-gray-900 capitalize">{user?.current_role}</span>
                            <button
                                onClick={handleRoleSwitch}
                                className="p-2 bg-white hover:bg-primary-50 text-gray-400 hover:text-primary-600 rounded-xl shadow-sm border border-gray-100 transition-all active:scale-95"
                                title="Switch Role"
                            >
                                <RotateCcw size={16} />
                            </button>
                        </div>
                    </div>

                    <button
                        onClick={logout}
                        className="w-full flex items-center gap-3 px-5 py-3 text-red-500 hover:bg-red-50 rounded-2xl font-bold transition-all group"
                    >
                        <LogOut size={20} className="group-hover:-translate-x-1 transition-transform" />
                        Logout
                    </button>
                </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 p-12 overflow-y-auto">
                <header className="flex justify-between items-start mb-16">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <span className="px-3 py-1 bg-primary-100 text-primary-600 text-[10px] font-black uppercase tracking-widest rounded-full">
                                {user?.current_role === 'student' ? 'Learner' : 'Coach'} Mode
                            </span>
                            {user?.onboarding_completed ? (
                                <span className="flex items-center gap-1 text-green-500 text-[10px] font-black uppercase tracking-widest">
                                    <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
                                    Profile Active
                                </span>
                            ) : (
                                <span className="text-amber-500 text-[10px] font-black uppercase tracking-widest underline decoration-2 cursor-pointer">
                                    Complete Onboarding
                                </span>
                            )}
                        </div>
                        <h1 className="text-5xl font-black text-gray-900 tracking-tight leading-tight">
                            Hey, {user?.first_name || 'learner'}! 👋
                        </h1>
                        <p className="text-gray-400 mt-3 text-lg font-medium">
                            {user?.current_role === 'student'
                                ? "What are we mastering today?"
                                : "Your students are waiting for your expertise."}
                        </p>
                    </div>

                    {/* Profile Summary Card */}
                    <div className="bg-white p-4 rounded-3xl shadow-xl shadow-gray-100 border border-gray-50 flex items-center gap-4 group cursor-pointer hover:border-primary-100 transition-all">
                        <div className="text-right">
                            <div className="font-bold text-gray-900">{user?.first_name} {user?.last_name?.[0]}.</div>
                            <div className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">{user?.profile_completion_percentage}% Complete</div>
                        </div>
                        <div className="w-12 h-12 bg-gradient-to-br from-primary-100 to-primary-50 rounded-2xl flex items-center justify-center text-primary-600 font-black text-lg border border-primary-100 ring-4 ring-primary-50/50 group-hover:scale-105 transition-transform">
                            {user?.first_name?.[0]}
                        </div>
                    </div>
                </header>

                {/* Stats Grid */}
                <section className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                    <div className="bg-white p-8 rounded-[2.5rem] shadow-sm border border-gray-100 hover:shadow-md transition-all group relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-6 opacity-5 group-hover:opacity-10 transition-opacity">
                            <FileText size={80} />
                        </div>
                        <div className="relative z-10">
                            <h3 className="text-gray-400 font-black uppercase text-[10px] tracking-widest mb-4">Active Contracts</h3>
                            <div className="flex items-baseline gap-2">
                                <span className="text-5xl font-black text-gray-900">{stats.contracts}</span>
                                <span className="text-gray-400 font-bold">Total</span>
                            </div>
                            <div className="mt-6 flex items-center gap-2 text-primary-600 text-sm font-bold">
                                View Details <ChevronRight size={16} />
                            </div>
                        </div>
                    </div>

                    <div className="bg-gradient-to-br from-primary-600 to-purple-700 p-8 rounded-[2.5rem] shadow-xl shadow-primary-200/50 hover:scale-[1.02] transition-all group overflow-hidden">
                        <div className="relative z-10 h-full flex flex-col">
                            <h3 className="text-primary-100 font-black uppercase text-[10px] tracking-widest mb-6">Upcoming Sessions</h3>
                            <div className="flex-1">
                                <UpcomingSessions />
                            </div>
                        </div>
                        {/* Decorative background element */}
                        <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-white/5 rounded-full blur-3xl"></div>
                    </div>

                    <div className="bg-white p-8 rounded-[2.5rem] shadow-sm border border-gray-100 flex flex-col justify-center items-center text-center group">
                        <div className="w-20 h-20 bg-gray-50 rounded-3xl flex items-center justify-center mb-6 text-4xl shadow-inner group-hover:rotate-12 transition-transform">🎓</div>
                        <p className="text-[10px] font-black text-gray-400 tracking-widest uppercase mb-2">Achievement Rank</p>
                        <div className="text-xl font-black text-gray-900">Novice Explorer</div>
                        <div className="w-full h-1.5 bg-gray-100 rounded-full mt-4 overflow-hidden">
                            <div className="w-1/3 h-full bg-gradient-to-r from-primary-500 to-purple-500 rounded-full"></div>
                        </div>
                    </div>
                </section>

                {/* Main Activity Area */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Left/Main Column */}
                    <div className="lg:col-span-2 space-y-8">
                        <div className="bg-white rounded-[2.5rem] border border-gray-100 p-10">
                            <div className="flex justify-between items-center mb-10">
                                <h2 className="text-2xl font-black text-gray-900 group flex items-center gap-2">
                                    Recent Activity
                                    <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                                </h2>
                                <button className="text-sm font-bold text-primary-600 hover:text-primary-700">View All</button>
                            </div>

                            {stats.contracts === 0 && stats.sessions === 0 ? (
                                <div className="text-center py-12 px-8 border-2 border-dashed border-gray-50 rounded-[2rem]">
                                    <div className="text-4xl mb-4 grayscale opacity-50">📁</div>
                                    <p className="text-gray-400 font-bold mb-6 italic">No activity yet. Let's change that!</p>
                                    <Link
                                        href="/marketplace"
                                        className="inline-block py-4 px-8 bg-gray-900 text-white font-black rounded-2xl shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-1 active:scale-95"
                                    >
                                        Explore Marketplace
                                    </Link>
                                </div>
                            ) : (
                                <RecentActivity />
                            )}
                        </div>
                    </div>

                    {/* Right column / Sidebar Widgets */}
                    <div className="space-y-8">
                        {/* Pending Items Widget - NEW */}
                        <div className="bg-white rounded-[2.5rem] border border-gray-100 p-8 shadow-sm">
                            <div className="flex justify-between items-center mb-6">
                                <h2 className="text-sm font-black text-gray-900 uppercase tracking-widest flex items-center gap-2">
                                    {user?.current_role === 'student' ? 'Active Requests' : 'Pending Proposals'}
                                    <span className="w-1.5 h-1.5 bg-amber-500 rounded-full"></span>
                                </h2>
                                <Link href={user?.current_role === 'student' ? '/marketplace/manage' : '/find-work'} className="text-[10px] font-bold text-primary-600">View All</Link>
                            </div>
                            <PendingItems />
                        </div>
                        {/* Quick Tips or Announcements */}
                        <div className="bg-indigo-50/50 p-8 rounded-[2.5rem] border border-indigo-100">
                            <div className="flex items-center gap-3 mb-6">
                                <div className="p-3 bg-indigo-100 text-indigo-600 rounded-2xl">
                                    <Award size={24} />
                                </div>
                                <h3 className="font-black text-indigo-900 uppercase text-xs tracking-wider">Pro Tip</h3>
                            </div>
                            <p className="text-indigo-800/70 font-medium leading-relaxed">
                                Profiles with a professional headshot get <span className="text-indigo-900 font-black">40% more matches</span>. Update yours today in settings!
                            </p>
                        </div>

                        {/* Market pulse widget */}
                        <div className="bg-white p-8 rounded-[2.5rem] border border-gray-100 shadow-sm">
                            <div className="flex items-center gap-2 mb-6">
                                <TrendingUp size={16} className="text-green-500" />
                                <h3 className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Market Pulse</h3>
                            </div>
                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <span className="text-sm font-bold text-gray-700">Web Design</span>
                                    <span className="text-[10px] font-black bg-green-100 text-green-600 px-2 py-0.5 rounded-full">HIGH</span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-sm font-bold text-gray-700">Digital Marketing</span>
                                    <span className="text-[10px] font-black bg-blue-100 text-blue-600 px-2 py-0.5 rounded-full">STABLE</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
