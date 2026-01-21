"use client";

import { useEffect, useState, use } from "react";
import api from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import {
    Clock,
    Video,
    Calendar,
    User,
    ShieldCheck,
    ExternalLink,
    AlertCircle,
    CheckCircle2,
    ChevronLeft
} from "lucide-react";
import Link from "next/link";
import { format } from "date-fns";

export default function SessionJoinPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = use(params);
    const { user } = useAuth();
    const [session, setSession] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchSession = async () => {
            try {
                const res = await api.get(`/contracts/sessions/${id}`);
                setSession(res.data);
            } catch (err: any) {
                console.error("Failed to fetch session", err);
                setError(err.response?.data?.detail || "Failed to load session details.");
            } finally {
                setLoading(false);
            }
        };

        fetchSession();
    }, [id]);

    const handleStartSession = async () => {
        try {
            await api.post(`/contracts/sessions/${id}/start`);
            // Refresh local state or redirect
            if (session.meeting_link) {
                window.open(session.meeting_link, "_blank");
            }
        } catch (err) {
            console.error("Failed to start session", err);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-muted/30 flex items-center justify-center pt-20">
                <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    if (error || !session) {
        return (
            <div className="min-h-screen bg-muted/30 flex items-center justify-center pt-20 px-4">
                <div className="max-w-md w-full bg-white rounded-[2.5rem] p-10 shadow-2xl border border-red-100 text-center">
                    <div className="w-20 h-20 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6">
                        <AlertCircle className="text-red-500 w-10 h-10" />
                    </div>
                    <h2 className="text-2xl font-black text-gray-900 mb-2">Session Not Found</h2>
                    <p className="text-gray-500 mb-8 font-medium">{error || "We couldn't find the session you're looking for."}</p>
                    <Link href="/dashboard" className="inline-flex items-center gap-2 px-8 py-4 bg-gray-900 text-white font-black rounded-2xl hover:bg-black transition-all">
                        <ChevronLeft size={20} /> Back to Dashboard
                    </Link>
                </div>
            </div>
        );
    }

    const scheduledDate = new Date(session.scheduled_at);
    const isPast = scheduledDate < new Date();
    const isJoinable = !isPast || (isPast && session.status !== 'completed');
    const partner = user?.id === session.contract.coach_id ? session.contract.student : session.contract.coach;

    return (
        <div className="min-h-screen bg-[#FDFDFF] pt-32 pb-12 px-4">
            <div className="max-w-4xl mx-auto">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Left: Session Info */}
                    <div className="lg:col-span-2 space-y-8">
                        <div className="bg-white rounded-[3rem] p-10 shadow-2xl border border-gray-100 relative overflow-hidden">
                            {/* Decorative Background */}
                            <div className="absolute top-0 right-0 w-64 h-64 bg-primary-50 rounded-full -mr-32 -mt-32 blur-3xl opacity-50"></div>

                            <div className="relative z-10">
                                <span className="inline-flex items-center gap-2 px-4 py-2 bg-primary-50 text-primary-600 rounded-full text-xs font-black uppercase tracking-widest mb-6">
                                    <ShieldCheck size={14} /> Secure Session
                                </span>

                                <h1 className="text-5xl font-black text-gray-900 mb-4 tracking-tight">
                                    Session #{session.session_number}
                                </h1>
                                <p className="text-xl text-gray-500 font-medium mb-12 max-w-lg">
                                    Welcome to the waiting room. Please verify your connection before joining the call.
                                </p>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                    <div className="flex items-start gap-4">
                                        <div className="p-4 bg-gray-50 rounded-2xl">
                                            <Calendar className="text-primary-600" />
                                        </div>
                                        <div>
                                            <p className="text-xs text-gray-400 font-black uppercase tracking-widest mb-1">Date</p>
                                            <p className="text-lg font-bold text-gray-900">{format(scheduledDate, 'EEEE, MMMM do')}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-start gap-4">
                                        <div className="p-4 bg-gray-50 rounded-2xl">
                                            <Clock className="text-primary-600" />
                                        </div>
                                        <div>
                                            <p className="text-xs text-gray-400 font-black uppercase tracking-widest mb-1">Time</p>
                                            <p className="text-lg font-bold text-gray-900">{format(scheduledDate, 'h:mm a')} ({session.duration_minutes}m)</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Meeting Rules/Safety */}
                        <div className="bg-primary-900 rounded-[2.5rem] p-10 text-white shadow-xl shadow-primary-100">
                            <h3 className="text-xl font-black mb-6">Meeting Guidelines</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="flex items-start gap-3">
                                    <CheckCircle2 className="text-primary-400 mt-1 flex-shrink-0" size={18} />
                                    <p className="text-sm font-medium text-primary-100">Turn on your camera for a better experience.</p>
                                </div>
                                <div className="flex items-start gap-3">
                                    <CheckCircle2 className="text-primary-400 mt-1 flex-shrink-0" size={18} />
                                    <p className="text-sm font-medium text-primary-100">Ensure you are in a quiet environment.</p>
                                </div>
                                <div className="flex items-start gap-3">
                                    <CheckCircle2 className="text-primary-400 mt-1 flex-shrink-0" size={18} />
                                    <p className="text-sm font-medium text-primary-100">Take notes during the session.</p>
                                </div>
                                <div className="flex items-start gap-3">
                                    <CheckCircle2 className="text-primary-400 mt-1 flex-shrink-0" size={18} />
                                    <p className="text-sm font-medium text-primary-100">Respect the scheduled time limit.</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Right: Join Action */}
                    <div className="space-y-8">
                        {/* Person Card */}
                        <div className="bg-white rounded-[2.5rem] p-8 shadow-xl border border-gray-100 text-center">
                            <div className="relative w-24 h-24 mx-auto mb-6">
                                {partner?.profile_picture ? (
                                    <img src={partner.profile_picture} className="w-full h-full rounded-[2rem] object-cover shadow-md" alt={partner.first_name} />
                                ) : (
                                    <div className="w-full h-full bg-gradient-to-br from-primary-600 to-purple-600 rounded-[2rem] flex items-center justify-center text-white text-3xl font-black">
                                        {partner?.first_name?.[0]}
                                    </div>
                                )}
                                <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 border-4 border-white rounded-full"></div>
                            </div>
                            <h4 className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Meeting With</h4>
                            <h3 className="text-xl font-black text-gray-900 mb-1">{partner?.first_name} {partner?.last_name}</h3>
                            <p className="text-xs text-primary-600 font-bold mb-6">{user?.id === session.contract.coach_id ? "Student" : "Coach"}</p>

                            <div className="p-4 bg-gray-50 rounded-2xl flex items-center justify-center gap-3">
                                <Video size={18} className="text-gray-400" />
                                <span className="text-xs font-black text-gray-900 uppercase tracking-widest">Video Enabled</span>
                            </div>
                        </div>

                        {/* Join Button */}
                        <div className="bg-white rounded-[2.5rem] p-8 shadow-xl border border-gray-100">
                            {session.status === 'completed' ? (
                                <div className="text-center">
                                    <div className="w-12 h-12 bg-green-50 text-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
                                        <CheckCircle2 size={24} />
                                    </div>
                                    <h4 className="font-black text-gray-900 mb-2">Session Completed</h4>
                                    <p className="text-xs text-gray-500 font-medium">This session has already ended. Thank you for using Skileez!</p>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    <p className="text-xs text-center text-gray-400 font-bold mb-4">Click below to start or join the call.</p>
                                    <button
                                        onClick={handleStartSession}
                                        disabled={!isJoinable}
                                        className="w-full py-5 bg-primary-600 text-white font-black rounded-[1.5rem] shadow-xl shadow-primary-200 hover:bg-primary-700 hover:-translate-y-1 active:scale-95 transition-all flex items-center justify-center gap-3 disabled:opacity-50 disabled:translate-y-0"
                                    >
                                        <Video size={20} /> Join Session
                                    </button>
                                    <Link
                                        href={`/dashboard/contracts/${session.contract.id}`}
                                        className="w-full py-4 text-gray-500 text-xs font-black rounded-[1.5rem] hover:bg-gray-50 transition-all flex items-center justify-center gap-2"
                                    >
                                        View Contract <ExternalLink size={14} />
                                    </Link>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
