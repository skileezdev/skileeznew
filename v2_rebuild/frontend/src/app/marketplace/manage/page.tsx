"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import Link from "next/link";
import {
    ChevronRight,
    MessageSquare,
    Clock,
    Plus,
    Target,
    Users,
    ArrowRight,
    TrendingUp,
    FileText,
    CheckCircle2
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";

interface LearningRequest {
    id: number;
    title: string;
    description: string;
    is_active: boolean;
    created_at: string;
    proposals_count?: number; // Calculated field or from API
}

interface Proposal {
    id: number;
    coach_id: number;
    status: string;
    price_per_session: number;
    session_count: number;
    created_at: string;
    coach: {
        first_name: string;
        last_name: string;
    };
}

export default function ManageRequestsPage() {
    const [requests, setRequests] = useState<LearningRequest[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedRequest, setSelectedRequest] = useState<number | null>(null);
    const [proposals, setProposals] = useState<Proposal[]>([]);
    const [proposalsLoading, setProposalsLoading] = useState(false);

    const fetchRequests = async () => {
        try {
            const res = await api.get("/marketplace/requests/me");
            setRequests(res.data);
        } catch (err) {
            console.error("Failed to fetch my requests", err);
        } finally {
            setLoading(false);
        }
    };

    const fetchProposals = async (requestId: number) => {
        setProposalsLoading(true);
        try {
            const res = await api.get(`/marketplace/requests/${requestId}/proposals`);
            setProposals(res.data);
        } catch (err) {
            console.error("Failed to fetch proposals", err);
        } finally {
            setProposalsLoading(false);
        }
    };

    useEffect(() => {
        fetchRequests();
    }, []);

    useEffect(() => {
        if (selectedRequest) {
            fetchProposals(selectedRequest);
        }
    }, [selectedRequest]);

    const handleAcceptProposal = async (proposalId: number) => {
        if (!confirm("Are you sure you want to accept this proposal? This will create a contract.")) return;
        try {
            await api.post(`/marketplace/proposals/${proposalId}/accept`);
            // Refresh
            if (selectedRequest) fetchProposals(selectedRequest);
            fetchRequests();
            alert("Proposal accepted! A contract has been created.");
        } catch (err) {
            console.error("Failed to accept proposal", err);
            alert("Failed to accept proposal.");
        }
    };

    return (
        <div className="min-h-screen bg-[#FDFDFF] p-8 md:p-12 font-inter">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex justify-between items-end mb-16">
                    <div>
                        <div className="flex items-center gap-2 text-primary-600 font-black text-[10px] uppercase tracking-widest mb-3">
                            <Target size={14} /> My Learning Path
                        </div>
                        <h1 className="text-5xl font-black text-gray-900 tracking-tight">Manage Requests</h1>
                        <p className="text-gray-400 mt-2 text-lg font-medium">Oversee your active learning requests and review coach proposals.</p>
                    </div>
                    <Link
                        href="/marketplace/create"
                        className="py-4 px-8 bg-gray-900 text-white font-black rounded-2xl shadow-xl hover:shadow-2xl transition-all transform hover:-translate-y-1 active:scale-95 flex items-center gap-2"
                    >
                        <Plus size={18} /> New Request
                    </Link>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
                    {/* Requests List */}
                    <div className="lg:col-span-1 space-y-6">
                        <h2 className="text-sm font-black text-gray-400 uppercase tracking-widest mb-4">Your Requests</h2>
                        {loading ? (
                            <div className="space-y-4">
                                {[1, 2, 3].map(i => <div key={i} className="h-24 bg-gray-100 rounded-3xl animate-pulse"></div>)}
                            </div>
                        ) : requests.length === 0 ? (
                            <div className="p-10 bg-white rounded-3xl border border-dashed border-gray-200 text-center">
                                <p className="text-gray-400 font-bold italic">No requests posted yet.</p>
                            </div>
                        ) : (
                            requests.map((req) => (
                                <div
                                    key={req.id}
                                    onClick={() => setSelectedRequest(req.id)}
                                    className={`p-6 rounded-[2.5rem] border transition-all cursor-pointer group ${selectedRequest === req.id
                                            ? "bg-primary-600 border-primary-600 shadow-xl shadow-primary-200 text-white"
                                            : "bg-white border-gray-100 shadow-sm hover:border-primary-200 text-gray-900"
                                        }`}
                                >
                                    <div className="flex justify-between items-start mb-3">
                                        <span className={`text-[10px] font-black uppercase tracking-widest px-2 py-0.5 rounded-full ${selectedRequest === req.id ? "bg-white/20 text-white" : "bg-primary-50 text-primary-600"
                                            }`}>
                                            {req.is_active ? "Active" : "Fulfilled"}
                                        </span>
                                        <span className={`text-[10px] font-bold ${selectedRequest === req.id ? "text-primary-100" : "text-gray-400"}`}>
                                            {formatDistanceToNow(new Date(req.created_at), { addSuffix: true })}
                                        </span>
                                    </div>
                                    <h3 className="font-black truncate mb-2">{req.title}</h3>
                                    <div className={`flex items-center gap-2 text-xs font-bold ${selectedRequest === req.id ? "text-primary-100" : "text-gray-400"}`}>
                                        <MessageSquare size={12} /> View Proposals
                                        <ChevronRight size={14} className={`transition-transform ${selectedRequest === req.id ? "translate-x-1" : "group-hover:translate-x-1"}`} />
                                    </div>
                                </div>
                            ))
                        )}
                    </div>

                    {/* Proposals View */}
                    <div className="lg:col-span-2">
                        {!selectedRequest ? (
                            <div className="h-full flex flex-col items-center justify-center p-20 bg-gray-50/50 rounded-[3rem] border-2 border-dashed border-gray-100">
                                <div className="text-6xl mb-6 grayscale opacity-20">👋</div>
                                <h3 className="text-2xl font-black text-gray-300">Select a request</h3>
                                <p className="text-gray-400 font-medium">Choose a request from the left to view interested coaches.</p>
                            </div>
                        ) : (
                            <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
                                <div className="flex justify-between items-center">
                                    <h2 className="text-2xl font-black text-gray-900">Coach Proposals</h2>
                                    <div className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-100 rounded-2xl shadow-sm">
                                        <Users size={16} className="text-primary-500" />
                                        <span className="text-sm font-black text-gray-700">{proposals.length} Applications</span>
                                    </div>
                                </div>

                                {proposalsLoading ? (
                                    <div className="flex flex-col items-center justify-center py-20">
                                        <div className="w-10 h-10 border-4 border-primary-100 border-t-primary-600 rounded-full animate-spin"></div>
                                    </div>
                                ) : proposals.length === 0 ? (
                                    <div className="p-20 bg-white rounded-[3rem] border border-gray-100 text-center shadow-sm">
                                        <div className="text-5xl mb-6 grayscale opacity-20">🐚</div>
                                        <h3 className="text-xl font-black text-gray-900 mb-2">Finding the right match...</h3>
                                        <p className="text-gray-400 font-medium max-w-sm mx-auto leading-relaxed">
                                            Sit tight! Your request is being shared with our top coaches. We'll notify you when someone applies.
                                        </p>
                                    </div>
                                ) : (
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        {proposals.map((proposal) => (
                                            <div key={proposal.id} className="bg-white p-8 rounded-[2.5rem] border border-gray-100 shadow-sm hover:shadow-xl hover:border-primary-100 transition-all group flex flex-col relative overflow-hidden">
                                                <div className="flex items-center gap-4 mb-6">
                                                    <div className="w-12 h-12 bg-gradient-to-br from-primary-600 to-purple-600 rounded-2xl flex items-center justify-center text-white font-black text-lg">
                                                        {proposal.coach.first_name[0]}
                                                    </div>
                                                    <div>
                                                        <h4 className="font-black text-gray-900 text-lg leading-tight">{proposal.coach.first_name} {proposal.coach.last_name[0]}.</h4>
                                                        <span className="text-[10px] font-black text-primary-600 uppercase tracking-widest">Verified Coach</span>
                                                    </div>
                                                </div>

                                                <div className="space-y-4 mb-8">
                                                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-2xl">
                                                        <span className="text-xs font-bold text-gray-500">Offer</span>
                                                        <span className="text-xl font-black text-gray-900">${proposal.price_per_session}/sess</span>
                                                    </div>
                                                    <div className="flex items-center justify-between px-4">
                                                        <span className="text-xs font-bold text-gray-400">Duration</span>
                                                        <span className="text-sm font-black text-gray-700">{proposal.session_count} Sessions</span>
                                                    </div>
                                                </div>

                                                {proposal.status === 'pending' ? (
                                                    <div className="mt-auto grid grid-cols-2 gap-4">
                                                        <Link
                                                            href={`/messages?userId=${proposal.coach_id}`}
                                                            className="py-4 px-4 bg-gray-900 text-white text-xs font-black rounded-xl text-center hover:bg-black transition-all"
                                                        >
                                                            Chat First
                                                        </Link>
                                                        <button
                                                            onClick={() => handleAcceptProposal(proposal.id)}
                                                            className="py-4 px-4 bg-primary-600 text-white text-xs font-black rounded-xl text-center hover:bg-primary-700 transition-all flex items-center justify-center gap-2"
                                                        >
                                                            Accept <ArrowRight size={14} />
                                                        </button>
                                                    </div>
                                                ) : (
                                                    <div className="mt-auto p-4 bg-green-50 text-green-700 rounded-2xl flex items-center justify-center gap-2 font-black text-xs">
                                                        <CheckCircle2 size={16} /> Already Accepted
                                                    </div>
                                                )}

                                                <div className="absolute top-0 right-0 p-3 opacity-5 group-hover:opacity-10 transition-opacity">
                                                    <TrendingUp size={60} />
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
