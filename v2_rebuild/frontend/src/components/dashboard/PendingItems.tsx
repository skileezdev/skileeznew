"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import {
    Clock,
    ArrowRight,
    MessageSquare,
    DollarSign,
    Target
} from "lucide-react";
import Link from "next/link";
import { formatDistanceToNow } from "date-fns";

export default function PendingItems() {
    const { user } = useAuth();
    const [items, setItems] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    const isCoach = user?.current_role === "coach";

    useEffect(() => {
        const fetchItems = async () => {
            if (!user) return;
            try {
                const endpoint = isCoach
                    ? "/marketplace/proposals/me"
                    : "/marketplace/requests/me";
                const res = await api.get(endpoint);

                // For coach, show pending proposals. For student, show active requests.
                const filtered = isCoach
                    ? res.data.filter((p: any) => p.status === "pending").slice(0, 3)
                    : res.data.filter((r: any) => r.is_active).slice(0, 3);

                setItems(filtered);
            } catch (err) {
                console.error("Failed to fetch pending items", err);
            } finally {
                setLoading(false);
            }
        };
        fetchItems();
    }, [user, isCoach]);

    if (loading) {
        return (
            <div className="space-y-3 animate-pulse">
                {[1, 2].map(i => (
                    <div key={i} className="h-20 bg-gray-50 rounded-2xl"></div>
                ))}
            </div>
        );
    }

    if (items.length === 0) {
        return (
            <div className="text-center py-6 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
                <p className="text-gray-400 text-xs font-bold uppercase tracking-wider">
                    {isCoach ? "No pending proposals" : "No active requests"}
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {items.map((item) => (
                <div
                    key={item.id}
                    className="p-4 bg-white border border-gray-100 rounded-2xl hover:border-primary-200 transition-all shadow-sm hover:shadow-md group"
                >
                    <div className="flex justify-between items-start mb-2">
                        <div className="flex items-center gap-2">
                            <div className="p-2 bg-primary-50 text-primary-600 rounded-lg">
                                {isCoach ? <Target size={14} /> : <MessageSquare size={14} />}
                            </div>
                            <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">
                                {isCoach ? "Proposal Sent" : "Request Active"}
                            </span>
                        </div>
                        <span className="text-[10px] text-gray-400 font-bold">
                            {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
                        </span>
                    </div>

                    <h4 className="font-bold text-gray-900 truncate mb-3">
                        {isCoach ? item.learning_request?.title : item.title}
                    </h4>

                    <div className="flex items-center justify-between mt-auto">
                        <div className="flex items-center gap-3">
                            <div className="flex items-center gap-1 text-[10px] font-black text-gray-500 uppercase">
                                <DollarSign size={10} className="text-green-500" />
                                {isCoach ? item.price_per_session : item.budget}/sess
                            </div>
                            <div className="flex items-center gap-1 text-[10px] font-black text-gray-500 uppercase">
                                <Clock size={10} className="text-blue-500" />
                                {isCoach ? item.session_count : item.sessions_needed} sessions
                            </div>
                        </div>
                        <Link
                            href={isCoach ? `/marketplace/${item.learning_request_id}` : `/marketplace/manage`}
                            className="p-1.5 bg-gray-50 text-gray-400 group-hover:bg-primary-50 group-hover:text-primary-600 rounded-lg transition-all"
                        >
                            <ArrowRight size={14} />
                        </Link>
                    </div>
                </div>
            ))}
        </div>
    );
}
