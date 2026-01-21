"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import {
    FileText,
    Target,
    CheckCircle2,
    Clock,
    DollarSign,
    ExternalLink,
    AlertCircle
} from "lucide-react";
import Link from "next/link";

interface ContextData {
    type: "contract" | "proposal";
    id: number;
    status: string;
    title: string;
    amount: number;
    sessions: number;
}

export default function ContextSidebar({ otherUserId }: { otherUserId: number | null }) {
    const [context, setContext] = useState<ContextData | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!otherUserId) return;

        const fetchContext = async () => {
            setLoading(true);
            try {
                const res = await api.get(`/marketplace/messages/context/${otherUserId}`);
                setContext(res.data);
            } catch (err) {
                console.error("Failed to fetch conversation context", err);
            } finally {
                setLoading(false);
            }
        };

        fetchContext();
    }, [otherUserId]);

    if (!otherUserId) return null;

    if (loading) {
        return (
            <div className="w-80 p-6 border-l border-gray-100 hidden lg:block bg-gray-50/30 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-1/3 mb-6"></div>
                <div className="h-40 bg-gray-200 rounded-3xl mb-4"></div>
                <div className="h-24 bg-gray-200 rounded-2xl"></div>
            </div>
        );
    }

    if (!context) {
        return (
            <div className="w-80 p-8 border-l border-gray-100 hidden lg:block bg-gray-50/30">
                <div className="text-center py-12">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4 grayscale opacity-30">
                        <AlertCircle size={32} />
                    </div>
                    <h4 className="text-gray-400 font-black uppercase text-[10px] tracking-widest mb-2">No active context</h4>
                    <p className="text-gray-400 text-xs font-medium leading-relaxed">
                        Start a contract or send a proposal to see related details here.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="w-80 p-6 border-l border-gray-100 hidden lg:block bg-gray-50/30 overflow-y-auto custom-scrollbar">
            <h4 className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-6">Related Workflow</h4>

            <div className={`p-6 rounded-[2rem] border mb-6 transition-all ${context.type === 'contract'
                    ? "bg-primary-600 border-primary-600 text-white shadow-xl shadow-primary-100"
                    : "bg-white border-gray-100 text-gray-900 shadow-sm"
                }`}>
                <div className="flex justify-between items-start mb-4">
                    <div className={`p-2 rounded-xl ${context.type === 'contract' ? "bg-white/20" : "bg-primary-50 text-primary-600"}`}>
                        {context.type === 'contract' ? <FileText size={18} /> : <Target size={18} />}
                    </div>
                    <span className={`text-[10px] font-black uppercase tracking-widest px-2 py-0.5 rounded-full ${context.type === 'contract' ? "bg-white/20" : "bg-primary-50 text-primary-600"
                        }`}>
                        {context.status}
                    </span>
                </div>

                <h3 className="font-black text-lg leading-tight mb-4">{context.title}</h3>

                <div className="space-y-3 mb-6">
                    <div className="flex items-center gap-2 text-xs font-bold opacity-80">
                        <DollarSign size={14} /> ${context.amount} / per session
                    </div>
                    <div className="flex items-center gap-2 text-xs font-bold opacity-80">
                        <Clock size={14} /> {context.sessions} Sessions
                    </div>
                </div>

                <Link
                    href={context.type === 'contract' ? `/dashboard/contracts/${context.id}` : `/marketplace/${context.id}`}
                    className={`w-full py-3 rounded-xl text-xs font-black flex items-center justify-center gap-2 transition-all ${context.type === 'contract'
                            ? "bg-white text-primary-600 hover:bg-primary-50"
                            : "bg-gray-900 text-white hover:bg-black"
                        }`}
                >
                    View Details <ExternalLink size={14} />
                </Link>
            </div>

            {/* Quick Status Info */}
            <div className="space-y-4">
                <div className="p-4 bg-white rounded-2xl border border-gray-100 shadow-sm">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">System Status</span>
                    </div>
                    <p className="text-xs text-gray-600 font-medium">This conversation is linked to an active {context.type}.</p>
                </div>
            </div>
        </div>
    );
}
