"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import api from "@/lib/api";
import {
    Calendar,
    Clock,
    Video,
    CheckCircle2,
    AlertCircle,
    ChevronLeft as ArrowLeft,
    ExternalLink,
    MessageSquare,
    MoreVertical,
    RotateCcw,
    Zap,
    CircleHelp
} from "lucide-react";
import Link from "next/link";

interface Session {
    id: number;
    session_number: number;
    status: string;
    scheduled_at: string | null;
    duration_minutes: number;
    meeting_link: string | null;
    reschedule_requested: boolean;
    reschedule_requested_at: string | null;
    new_requested_date: string | null;
    reschedule_reason: string | null;
}

interface Contract {
    id: number;
    contract_number: string;
    status: string;
    total_amount: number;
    rate: number;
    total_sessions: number;
    completed_sessions: number;
    learning_request: { title: string; description: string };
    student: { first_name: string; last_name: string };
    coach: { first_name: string; last_name: string };
    sessions: Session[];
}

export default function ContractDetailPage() {
    const { id } = useParams();
    const [contract, setContract] = useState<Contract | null>(null);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState<number | null>(null);
    const [showRescheduleModal, setShowRescheduleModal] = useState(false);
    const [rescheduleSessionId, setRescheduleSessionId] = useState<number | null>(null);
    const [rescheduleForm, setRescheduleForm] = useState({ date: "", reason: "" });

    const fetchContract = async () => {
        try {
            const res = await api.get(`/contracts/${id}`);
            setContract(res.data);
        } catch (err) {
            console.error("Failed to fetch contract", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchContract();
    }, [id]);

    const handleStartSession = async (sessionId: number) => {
        setActionLoading(sessionId);
        try {
            await api.post(`/contracts/sessions/${sessionId}/start`);
            await fetchContract();
        } catch (err) {
            console.error("Failed to start session", err);
        } finally {
            setActionLoading(null);
        }
    };

    const handleCompleteSession = async (sessionId: number) => {
        setActionLoading(sessionId);
        try {
            await api.post(`/contracts/sessions/${sessionId}/complete`);
            await fetchContract();
        } catch (err) {
            console.error("Failed to complete session", err);
        } finally {
            setActionLoading(null);
        }
    };

    if (loading) return (
        <div className="min-h-screen flex items-center justify-center bg-[#FDFDFF]">
            <div className="w-12 h-12 border-4 border-primary-100 border-t-primary-600 rounded-full animate-spin"></div>
        </div>
    );

    if (!contract) return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-[#FDFDFF] p-8 text-center">
            <h1 className="text-3xl font-black text-gray-900 mb-4">Contract not found</h1>
            <Link href="/dashboard/contracts" className="text-primary-600 font-bold hover:underline">Back to Workspace</Link>
        </div>
    );

    return (
        <div className="min-h-screen bg-[#FDFDFF] p-8 md:p-12 font-inter">
            <div className="max-w-6xl mx-auto">
                {/* Header Navigation */}
                <Link href="/dashboard/contracts" className="inline-flex items-center gap-2 text-gray-400 hover:text-gray-900 font-bold text-sm mb-12 transition-colors group">
                    <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" /> Back to Agreements
                </Link>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
                    {/* Left Column: Contract Details */}
                    <div className="lg:col-span-1 space-y-8">
                        <div className="bg-white p-10 rounded-[3rem] shadow-xl shadow-gray-100/50 border border-gray-100 relative overflow-hidden">
                            <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-primary-500 to-purple-600"></div>

                            <div className="mb-8">
                                <span className="text-[10px] font-black text-gray-300 uppercase tracking-widest block mb-1">Contract Number</span>
                                <h1 className="text-3xl font-black text-gray-900">{contract.contract_number}</h1>
                                <div className={`mt-3 inline-block px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border ${contract.status === 'active' ? 'bg-green-50 text-green-600 border-green-100' : 'bg-amber-50 text-amber-600 border-amber-100'}`}>
                                    {contract.status.replace('_', ' ')}
                                </div>
                            </div>

                            <div className="space-y-6">
                                <div>
                                    <h3 className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Topic</h3>
                                    <p className="font-bold text-gray-900 leading-tight">{contract.learning_request.title}</p>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <h3 className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Student</h3>
                                        <p className="font-bold text-gray-700 text-sm">{contract.student.first_name} {contract.student.last_name[0]}.</p>
                                    </div>
                                    <div>
                                        <h3 className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Coach</h3>
                                        <p className="font-bold text-gray-700 text-sm">{contract.coach.first_name} {contract.coach.last_name[0]}.</p>
                                    </div>
                                </div>
                                <div className="pt-6 border-t border-gray-50 flex items-center justify-between">
                                    <div>
                                        <h3 className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Rate</h3>
                                        <p className="text-xl font-black text-gray-900">${contract.rate}<span className="text-xs text-gray-400">/hr</span></p>
                                    </div>
                                    <div className="text-right">
                                        <h3 className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Total</h3>
                                        <p className="text-xl font-black text-primary-600">${contract.total_amount}</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Quick Actions */}
                        <div className="flex gap-4">
                            <button className="flex-1 py-4 bg-gray-900 text-white font-black rounded-2xl shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-2 text-sm">
                                <MessageSquare size={18} /> Chat
                            </button>
                            <button className="flex-1 py-4 bg-white border border-gray-100 text-gray-400 font-black rounded-2xl shadow-sm hover:text-gray-900 transition-all flex items-center justify-center gap-2 text-sm">
                                <CircleHelp size={18} /> Support
                            </button>
                        </div>
                    </div>

                    {/* Right Column: Sessions Feed (The "Soul" of Management) */}
                    <div className="lg:col-span-2 space-y-8">
                        <div className="bg-white rounded-[3rem] border border-gray-100 p-10 shadow-sm">
                            <div className="flex justify-between items-center mb-10">
                                <div>
                                    <h2 className="text-2xl font-black text-gray-900">Session Roadmap</h2>
                                    <p className="text-xs font-medium text-gray-400 mt-1">Track and manage each stage of your learning journey.</p>
                                </div>
                                <div className="text-right">
                                    <div className="text-2xl font-black text-primary-600">{contract.completed_sessions}/{contract.total_sessions}</div>
                                    <div className="text-[10px] font-black text-gray-300 uppercase tracking-widest">Completed</div>
                                </div>
                            </div>

                            <div className="space-y-6">
                                {contract.sessions.map((session) => (
                                    <div key={session.id} className="group relative pl-8 border-l-2 border-gray-100 hover:border-primary-200 transition-all py-2">
                                        {/* Timeline Dot */}
                                        <div className={`absolute left-[-9px] top-1/2 -translate-y-1/2 w-4 h-4 rounded-full border-4 border-white shadow-sm transition-all ${session.status === 'completed' ? 'bg-primary-500' :
                                            session.status === 'in_progress' ? 'bg-amber-500 animate-pulse' : 'bg-gray-200'
                                            }`}></div>

                                        <div className="bg-gray-50/50 group-hover:bg-white rounded-[2rem] p-6 border border-transparent group-hover:border-gray-100 group-hover:shadow-xl group-hover:shadow-gray-100/30 transition-all">
                                            <div className="flex flex-col md:flex-row justify-between gap-4">
                                                <div className="flex gap-4">
                                                    <div className="p-4 bg-white rounded-2xl shadow-sm border border-gray-100 h-fit">
                                                        <span className="text-[10px] font-black text-gray-300 uppercase block mb-1">No.</span>
                                                        <span className="text-lg font-black text-gray-900">{session.session_number}</span>
                                                    </div>
                                                    <div>
                                                        <h4 className="font-black text-gray-900 capitalize mb-1">{session.status.replace('_', ' ')}</h4>
                                                        <div className="flex flex-wrap items-center gap-4 text-xs font-bold text-gray-400">
                                                            <div className="flex items-center gap-1">
                                                                <Calendar size={14} />
                                                                {session.scheduled_at ? new Date(session.scheduled_at).toLocaleDateString() : 'Scheduling...'}
                                                            </div>
                                                            <div className="flex items-center gap-1">
                                                                <Clock size={14} />
                                                                {session.duration_minutes} Minutes
                                                            </div>
                                                        </div>
                                                        {session.reschedule_requested && (
                                                            <div className="mt-3 inline-flex items-center gap-2 px-3 py-1.5 bg-amber-50 text-amber-700 text-[10px] font-black uppercase rounded-lg border border-amber-100">
                                                                <RotateCcw size={12} /> Reschedule Pending
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>

                                                <div className="flex items-center gap-3">
                                                    {session.status === 'scheduled' && (
                                                        <>
                                                            <button
                                                                onClick={() => handleStartSession(session.id)}
                                                                disabled={actionLoading === session.id}
                                                                className="py-3 px-6 bg-primary-600 text-white font-black text-xs rounded-xl shadow-lg hover:shadow-xl hover:scale-105 active:scale-95 transition-all flex items-center gap-2"
                                                            >
                                                                {actionLoading === session.id ? 'Starting...' : <>Start Now <Zap size={14} className="fill-white" /></>}
                                                            </button>
                                                            <button
                                                                onClick={() => {
                                                                    setRescheduleSessionId(session.id);
                                                                    setShowRescheduleModal(true);
                                                                }}
                                                                className="p-3 bg-white border border-gray-100 text-gray-400 hover:text-gray-900 rounded-xl shadow-sm transition-all active:scale-95"
                                                            >
                                                                <RotateCcw size={18} />
                                                            </button>
                                                            <button className="p-3 bg-white border border-gray-100 text-gray-400 hover:text-gray-900 rounded-xl shadow-sm transition-all active:scale-95">
                                                                <MoreVertical size={18} />
                                                            </button>
                                                        </>
                                                    )}
                                                    {session.status === 'in_progress' && (
                                                        <>
                                                            {session.meeting_link && (
                                                                <a
                                                                    href={session.meeting_link}
                                                                    target="_blank"
                                                                    className="py-3 px-6 bg-blue-600 text-white font-black text-xs rounded-xl shadow-lg hover:shadow-xl items-center gap-2 flex"
                                                                >
                                                                    Video Link <ExternalLink size={14} />
                                                                </a>
                                                            )}
                                                            <button
                                                                onClick={() => handleCompleteSession(session.id)}
                                                                disabled={actionLoading === session.id}
                                                                className="py-3 px-6 bg-green-600 text-white font-black text-xs rounded-xl shadow-lg hover:shadow-xl hover:scale-105 active:scale-95 transition-all"
                                                            >
                                                                {actionLoading === session.id ? 'Saving...' : 'End & Complete'}
                                                            </button>
                                                        </>
                                                    )}
                                                    {session.status === 'completed' && (
                                                        <div className="flex items-center gap-2 text-green-500 font-black text-xs uppercase italic drop-shadow-sm">
                                                            <CheckCircle2 size={16} /> Verified Done
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Policy Note (1:1 V1 Mirror) */}
                        <div className="bg-primary-50/50 p-8 rounded-[2.5rem] border border-primary-50 flex gap-4">
                            <div className="p-3 bg-white rounded-2xl h-fit shadow-sm">
                                <AlertCircle className="text-primary-600" size={24} />
                            </div>
                            <div>
                                <h4 className="font-black text-primary-900 text-sm mb-1 uppercase tracking-widest">Attendance Policy</h4>
                                <p className="text-primary-800/60 text-xs font-medium leading-relaxed italic">
                                    Rescheduling is only allowed 24 hours prior to the session start. Late attendance exceeding 15 minutes may result in a forfeit session.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Reschedule Modal (V1 Mirror) */}
            {showRescheduleModal && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-gray-900/60 backdrop-blur-sm">
                    <div className="bg-white w-full max-w-lg rounded-[3rem] p-10 shadow-2xl border border-gray-100 animate-in fade-in zoom-in duration-300">
                        <div className="flex justify-between items-center mb-8">
                            <div>
                                <h2 className="text-3xl font-black text-gray-900">Reschedule</h2>
                                <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mt-1">Session Adjustment</p>
                            </div>
                            <button
                                onClick={() => setShowRescheduleModal(false)}
                                className="p-3 bg-gray-50 text-gray-400 hover:text-gray-900 rounded-2xl transition-all"
                            >
                                <ArrowLeft size={20} className="rotate-90" />
                            </button>
                        </div>

                        <div className="space-y-6">
                            <div>
                                <label className="block text-[10px] font-black text-gray-300 uppercase tracking-widest mb-2 px-1">Proposed New Date</label>
                                <input
                                    type="datetime-local"
                                    className="w-full px-6 py-4 bg-gray-50 border border-transparent focus:border-primary-500 focus:bg-white rounded-[1.5rem] outline-none transition-all font-bold text-gray-900"
                                    value={rescheduleForm.date}
                                    onChange={(e) => setRescheduleForm({ ...rescheduleForm, date: e.target.value })}
                                />
                            </div>

                            <div>
                                <label className="block text-[10px] font-black text-gray-300 uppercase tracking-widest mb-2 px-1">Reason for Change</label>
                                <textarea
                                    rows={3}
                                    placeholder="Explain why you need to move this session..."
                                    className="w-full px-6 py-4 bg-gray-50 border border-transparent focus:border-primary-500 focus:bg-white rounded-[1.5rem] outline-none transition-all font-bold text-gray-900 resize-none"
                                    value={rescheduleForm.reason}
                                    onChange={(e) => setRescheduleForm({ ...rescheduleForm, reason: e.target.value })}
                                />
                            </div>

                            <button
                                onClick={async () => {
                                    if (!rescheduleSessionId) return;
                                    try {
                                        await api.post(`/contracts/sessions/${rescheduleSessionId}/reschedule-request`, {
                                            new_date: rescheduleForm.date,
                                            reason: rescheduleForm.reason
                                        });
                                        setShowRescheduleModal(false);
                                        await fetchContract();
                                    } catch (err) {
                                        console.error("Failed to reschedule", err);
                                    }
                                }}
                                className="w-full py-5 bg-primary-600 text-white font-black rounded-[2rem] shadow-lg shadow-primary-200 hover:shadow-xl hover:-translate-y-1 transition-all active:scale-95 flex items-center justify-center gap-2"
                            >
                                Submit Request <Zap size={18} />
                            </button>
                            <p className="text-[10px] text-center text-gray-300 font-bold italic px-4">
                                Note: Rescheduling requests must be approved by the other party.
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
