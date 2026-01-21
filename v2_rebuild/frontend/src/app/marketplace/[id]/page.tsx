"use client";

import { useEffect, useState, use } from "react";
import api from "@/lib/api";
import Link from "next/link";
import {
    ChevronLeft,
    Clock,
    ShieldCheck,
    Flame,
    Zap,
    Users,
    MapPin,
    Calendar,
    MessageSquare,
    DollarSign,
    Target
} from "lucide-react";
import { ProposalModal } from "@/components/marketplace/ProposalModal";
import { formatDistanceToNow } from "date-fns";

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
    timeframe?: string;
    preferred_times?: any[];
    skill_tags?: string[];
    student: {
        first_name: string;
        last_name: string;
        bio?: string;
        country?: string;
    };
    screening_questions: ScreeningQuestion[];
    created_at: string;
}

export default function RequestDetailPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = use(params);
    const [request, setRequest] = useState<LearningRequest | null>(null);
    const [loading, setLoading] = useState(true);
    const [selectedRequest, setSelectedRequest] = useState<boolean>(false);
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        const fetchRequest = async () => {
            try {
                const res = await api.get(`/marketplace/requests/${id}`);
                setRequest(res.data);
            } catch (err) {
                console.error("Failed to fetch request detail", err);
            } finally {
                setLoading(false);
            }
        };
        fetchRequest();
    }, [id]);

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#FDFDFF]">
                <div className="w-12 h-12 border-4 border-primary-100 border-t-primary-600 rounded-full animate-spin"></div>
            </div>
        );
    }

    if (!request) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center bg-[#FDFDFF] p-8 text-center">
                <div className="text-6xl mb-6 grayscale opacity-20">🏝️</div>
                <h1 className="text-3xl font-black text-gray-900 mb-4">Request Not Found</h1>
                <p className="text-gray-500 mb-8 max-w-md">The learning request you're looking for might have been removed or fulfilled.</p>
                <Link href="/marketplace" className="py-4 px-8 bg-gray-900 text-white font-black rounded-2xl shadow-xl hover:shadow-2xl transition-all">
                    Back to Marketplace
                </Link>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#FDFDFF] font-inter">
            <div className="max-w-6xl mx-auto p-8 md:p-12 lg:p-16">
                {/* Back Nav */}
                <Link href="/marketplace" className="inline-flex items-center gap-2 text-gray-400 hover:text-primary-600 font-bold mb-12 transition-colors group">
                    <ChevronLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
                    Back to Marketplace
                </Link>

                {success && (
                    <div className="mb-12 p-8 bg-green-50 border border-green-200 text-green-700 rounded-[2.5rem] text-center font-bold animate-in fade-in zoom-in duration-300 shadow-xl shadow-green-100/50 flex items-center justify-center gap-3">
                        <Zap size={24} className="fill-green-500" />
                        <span className="text-xl">Application Sent Successfully! 🚀</span>
                    </div>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-16">
                    {/* Main Content */}
                    <div className="lg:col-span-2 space-y-12">
                        <section>
                            <div className="flex flex-wrap gap-3 mb-6">
                                <span className="flex items-center gap-1.5 px-4 py-2 bg-primary-50 text-primary-600 text-[10px] font-black uppercase tracking-wider rounded-full border border-primary-100">
                                    <ShieldCheck size={14} className="fill-primary-100" /> Verified Only
                                </span>
                                {request.skill_type === "long_term" && (
                                    <span className="flex items-center gap-1.5 px-4 py-2 bg-purple-50 text-purple-600 text-[10px] font-black uppercase tracking-wider rounded-full border border-purple-100">
                                        <Flame size={14} className="fill-purple-100" /> Immersive
                                    </span>
                                )}
                                <span className="flex items-center gap-1.5 px-4 py-2 bg-gray-50 text-gray-500 text-[10px] font-black uppercase tracking-wider rounded-full border border-gray-100">
                                    <Clock size={14} /> Created {formatDistanceToNow(new Date(request.created_at), { addSuffix: true })}
                                </span>
                            </div>

                            <h1 className="text-5xl md:text-6xl font-black text-gray-900 tracking-tight leading-tight mb-8">
                                {request.title}
                            </h1>

                            <div className="prose prose-lg max-w-none text-gray-600 font-medium leading-[1.8]">
                                {request.description.split('\n').map((para, i) => (para ? <p key={i} className="mb-6">{para}</p> : <br key={i} />))}
                            </div>
                        </section>

                        <hr className="border-gray-100" />

                        {/* Screening Questions (V1 Parity) */}
                        {request.screening_questions?.length > 0 && (
                            <section className="space-y-6">
                                <h3 className="text-xl font-black text-gray-900 flex items-center gap-2">
                                    <MessageSquare size={24} className="text-primary-500" />
                                    Screening Questions
                                </h3>
                                <div className="space-y-4">
                                    {request.screening_questions.map((q, i) => (
                                        <div key={q.id} className="p-6 bg-white rounded-3xl border border-gray-100 shadow-sm flex gap-4 items-start">
                                            <div className="w-8 h-8 rounded-xl bg-gray-50 flex items-center justify-center text-gray-400 font-black text-xs shrink-0">
                                                {i + 1}
                                            </div>
                                            <p className="text-gray-700 font-bold leading-relaxed">{q.question_text}</p>
                                        </div>
                                    ))}
                                </div>
                            </section>
                        )}
                    </div>

                    {/* Sidebar / Actions */}
                    <div className="space-y-8">
                        {/* Summary Widget */}
                        <div className="bg-white p-8 rounded-[2.5rem] border border-gray-100 shadow-xl shadow-gray-100/50 sticky top-8">
                            <div className="space-y-8 mb-10">
                                <div>
                                    <div className="text-[10px] font-black text-gray-300 uppercase tracking-widest mb-2">Offered Budget</div>
                                    <div className="text-4xl font-black text-gray-900 flex items-baseline gap-1">
                                        {request.budget ? `$${request.budget}` : 'TBD'}
                                        {request.budget && <span className="text-sm text-gray-400 font-bold uppercase tracking-wider">/ session</span>}
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-6">
                                    <div className="space-y-1">
                                        <div className="text-[10px] font-black text-gray-300 uppercase tracking-widest">Sessions</div>
                                        <div className="font-black text-gray-900">{request.sessions_needed} Total</div>
                                    </div>
                                    <div className="space-y-1">
                                        <div className="text-[10px] font-black text-gray-300 uppercase tracking-widest">Experience</div>
                                        <div className="font-black text-gray-900 border-b-2 border-primary-500 inline-block capitalize">{request.experience_level || 'Any'}</div>
                                    </div>
                                    {request.timeframe && (
                                        <div className="space-y-1">
                                            <div className="text-[10px] font-black text-gray-300 uppercase tracking-widest">Timeframe</div>
                                            <div className="font-black text-gray-900">{request.timeframe}</div>
                                        </div>
                                    )}
                                </div>
                            </div>

                            <button
                                onClick={() => setSelectedRequest(true)}
                                className="w-full py-5 bg-primary-600 hover:bg-primary-700 text-white font-black rounded-2xl shadow-lg shadow-primary-200 hover:shadow-2xl transition-all transform hover:-translate-y-1 active:scale-95 flex items-center justify-center gap-3"
                            >
                                Apply Now <Zap size={20} className="fill-white" />
                            </button>

                            <div className="mt-8 pt-8 border-t border-gray-50">
                                <h4 className="text-[10px] font-black text-gray-300 uppercase tracking-widest mb-6 flex items-center gap-2">
                                    <Users size={12} /> About The Student
                                </h4>
                                <div className="flex items-center gap-4 mb-6">
                                    <div className="w-14 h-14 bg-gradient-to-br from-primary-100 to-primary-50 rounded-2xl flex items-center justify-center text-primary-600 font-black text-xl border border-primary-100 shadow-inner">
                                        {request.student.first_name[0]}
                                    </div>
                                    <div>
                                        <div className="font-black text-gray-900 text-lg leading-tight">{request.student.first_name} {request.student.last_name[0]}.</div>
                                        <div className="flex items-center gap-1 text-gray-400 text-xs font-bold mt-1">
                                            <MapPin size={10} /> {request.student.country || 'International'}
                                        </div>
                                    </div>
                                </div>
                                <p className="text-gray-500 text-sm font-medium leading-relaxed italic">
                                    "{request.student.bio || 'Joining Skileez to master new skills with top coaches.'}"
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {selectedRequest && (
                <ProposalModal
                    isOpen={true}
                    requestId={request.id}
                    requestTitle={request.title}
                    onClose={() => setSelectedRequest(false)}
                    onSuccess={() => {
                        setSelectedRequest(false);
                        setSuccess(true);
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                        setTimeout(() => setSuccess(false), 8000);
                    }}
                />
            )}
        </div>
    );
}
