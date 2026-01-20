"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import Link from "next/link";
import { ProposalModal } from "@/components/marketplace/ProposalModal";
import {
    Search,
    Filter,
    Clock,
    ShieldCheck,
    Flame,
    Zap,
    ChevronRight,
    Users,
    ShoppingBag
} from "lucide-react";

interface ScreeningQuestion {
    id: number;
    question_text: string;
}

interface LearningRequest {
    id: number;
    title: string;
    description: string;
    budget: number | null;
    experience_level: string | null;
    skill_type: string;
    sessions_needed: number;
    student: {
        first_name: string;
        last_name: string;
    };
    screening_questions: ScreeningQuestion[];
    created_at: string;
}

export default function MarketplacePage() {
    const [requests, setRequests] = useState<LearningRequest[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedRequest, setSelectedRequest] = useState<LearningRequest | null>(null);
    const [success, setSuccess] = useState(false);
    const [searchTerm, setSearchTerm] = useState("");

    const fetchRequests = async () => {
        setLoading(true);
        try {
            const res = await api.get("/marketplace/requests");
            setRequests(res.data);
        } catch (err) {
            console.error("Failed to fetch requests", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRequests();
    }, []);

    const filteredRequests = requests.filter(req =>
        req.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        req.description.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="min-h-screen bg-[#FDFDFF] p-8 md:p-12 font-inter">
            <div className="max-w-7xl mx-auto">
                {success && (
                    <div className="mb-8 p-5 bg-green-50 border border-green-200 text-green-700 rounded-[1.5rem] text-center font-bold animate-in fade-in slide-in-from-top-4 duration-300 shadow-lg shadow-green-100/50 flex items-center justify-center gap-2">
                        <Zap size={20} className="fill-green-500" />
                        Application Sent! Success 🚀
                    </div>
                )}

                {/* Header Section */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-16">
                    <div>
                        <div className="flex items-center gap-2 text-primary-600 font-black text-[10px] uppercase tracking-widest mb-3">
                            <ShoppingBag size={14} /> Knowledge Exchange
                        </div>
                        <h1 className="text-5xl font-black text-gray-900 tracking-tight leading-tight">
                            Marketplace
                        </h1>
                        <p className="text-gray-400 mt-2 text-lg font-medium max-w-xl leading-relaxed">
                            Support fellow learners, build your portfolio, and earn rewards by sharing your expertise.
                        </p>
                    </div>
                    <Link
                        href="/marketplace/create"
                        className="group py-4 px-8 bg-gray-900 text-white font-black rounded-2xl shadow-xl hover:shadow-2xl transition-all transform hover:-translate-y-1 active:scale-95 flex items-center gap-2"
                    >
                        Post a Request <ChevronRight size={18} className="group-hover:translate-x-1 transition-transform" />
                    </Link>
                </div>

                {/* Filters Row */}
                <div className="flex flex-col md:flex-row gap-4 mb-12">
                    <div className="relative flex-1 group">
                        <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-primary-500 transition-colors" size={20} />
                        <input
                            type="text"
                            placeholder="Search skills, topics, or keywords..."
                            className="w-full pl-14 pr-6 py-4 bg-white border border-gray-100 rounded-[2rem] shadow-sm outline-none focus:ring-2 focus:ring-primary-500 transition-all font-medium text-gray-700 placeholder:text-gray-300"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <button className="px-8 py-4 bg-white border border-gray-100 rounded-[2rem] shadow-sm font-bold text-gray-500 flex items-center gap-2 hover:bg-gray-50 transition-all active:scale-95">
                        <Filter size={18} /> Filters
                    </button>
                </div>

                {loading ? (
                    <div className="flex flex-col items-center justify-center py-32 space-y-4">
                        <div className="w-12 h-12 border-4 border-primary-100 border-t-primary-600 rounded-full animate-spin"></div>
                        <p className="text-gray-400 font-black uppercase text-[10px] tracking-widest">Scanning Marketplace...</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        {filteredRequests.map((req) => (
                            <div key={req.id} className="bg-white p-8 md:p-10 rounded-[2.5rem] shadow-sm border border-gray-100 hover:shadow-xl hover:border-primary-100 transition-all group relative overflow-hidden flex flex-col">
                                {/* Trust/Scarcity Badges (V1 Mirror) */}
                                <div className="flex justify-between items-start mb-6">
                                    <div className="flex flex-wrap gap-2">
                                        <span className="flex items-center gap-1.5 px-3 py-1.5 bg-primary-50 text-primary-600 text-[10px] font-black uppercase tracking-wider rounded-full border border-primary-50">
                                            <ShieldCheck size={12} className="fill-primary-100" /> Verified Only
                                        </span>
                                        {req.skill_type === "long_term" && (
                                            <span className="flex items-center gap-1.5 px-3 py-1.5 bg-purple-50 text-purple-600 text-[10px] font-black uppercase tracking-wider rounded-full border border-purple-50">
                                                <Flame size={12} className="fill-purple-100" /> Immersive
                                            </span>
                                        )}
                                    </div>
                                    <div className="flex items-center gap-1 text-amber-600 bg-amber-50 px-3 py-1.5 rounded-full border border-amber-50">
                                        <Users size={14} className="fill-amber-100" />
                                        <span className="text-[10px] font-black uppercase tracking-widest">3 Spots Left!</span>
                                    </div>
                                </div>

                                <div className="mb-6">
                                    <h3 className="text-3xl font-black text-gray-900 group-hover:text-primary-600 transition-colors leading-tight mb-2">
                                        {req.title}
                                    </h3>
                                    <div className="flex items-center gap-2 text-gray-400 text-sm font-medium">
                                        <div className="w-6 h-6 bg-gray-100 rounded-full flex items-center justify-center text-[10px] font-black text-gray-600">
                                            {req.student.first_name[0]}
                                        </div>
                                        {req.student.first_name} {req.student.last_name[0]}. • {new Date(req.created_at).toLocaleDateString()}
                                    </div>
                                </div>

                                <p className="text-gray-500 font-medium leading-relaxed line-clamp-3 mb-8">
                                    {req.description}
                                </p>

                                <div className="mt-auto pt-8 border-t border-gray-50 flex items-center justify-between">
                                    <div className="space-y-1">
                                        <div className="text-[10px] font-black text-gray-300 uppercase tracking-widest">Offered Reward</div>
                                        <div className="text-2xl font-black text-gray-900 flex items-baseline gap-1">
                                            {req.budget ? `$${req.budget}` : 'TBD'}
                                            {req.budget && <span className="text-xs text-gray-400 font-bold uppercase">/ session</span>}
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => setSelectedRequest(req)}
                                        className="py-4 px-8 bg-primary-600 hover:bg-primary-700 text-white font-black rounded-2xl shadow-lg shadow-primary-100 hover:shadow-xl transition-all transform hover:-translate-y-1 active:scale-95 flex items-center gap-2"
                                    >
                                        Apply Now <Zap size={16} className="fill-white" />
                                    </button>
                                </div>

                                {/* Floating Scarcity Indicator (V1 Soul) */}
                                <div className="absolute top-0 right-0 p-2 transform translate-x-12 translate-y-[-12px] rotate-45">
                                    <div className="bg-primary-500 text-white text-[8px] font-black px-10 py-1 uppercase tracking-[0.2em] shadow-lg">
                                        HOT ITEM
                                    </div>
                                </div>
                            </div>
                        ))}

                        {filteredRequests.length === 0 && (
                            <div className="col-span-full text-center py-32 bg-white rounded-[3rem] border-2 border-dashed border-gray-100">
                                <div className="text-6xl mb-6 grayscale opacity-20">🔎</div>
                                <h3 className="text-2xl font-black text-gray-300">No requests found</h3>
                                <p className="text-gray-400 font-medium mt-2">Try adjusting your filters or search terms.</p>
                            </div>
                        )}
                    </div>
                )}

                {/* Proposal Modal (1:1 Mirror logic injected here) */}
                {selectedRequest && (
                    <ProposalModal
                        isOpen={true}
                        requestId={selectedRequest.id}
                        requestTitle={selectedRequest.title}
                        onClose={() => setSelectedRequest(null)}
                        onSuccess={() => {
                            setSelectedRequest(null);
                            setSuccess(true);
                            window.scrollTo({ top: 0, behavior: 'smooth' });
                            setTimeout(() => setSuccess(false), 5000);
                            fetchRequests();
                        }}
                    />
                )}
            </div>
        </div>
    );
}
