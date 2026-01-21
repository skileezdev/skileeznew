"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import {
    Calendar,
    Clock,
    Video,
    ChevronRight,
    MapPin
} from "lucide-react";
import { format } from "date-fns";
import Link from "next/link";

interface Session {
    id: number;
    contract_id: number;
    session_number: number;
    scheduled_at: string;
    duration_minutes: number;
    status: string;
    meeting_link?: string;
}

export default function UpcomingSessions() {
    const [sessions, setSessions] = useState<Session[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSessions = async () => {
            try {
                const res = await api.get("/contracts/sessions/all");
                // Filter only upcoming scheduled sessions
                const upcoming = res.data
                    .filter((s: Session) => s.status === "scheduled" && s.scheduled_at && new Date(s.scheduled_at) > new Date())
                    .sort((a: Session, b: Session) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime())
                    .slice(0, 3);
                setSessions(upcoming);
            } catch (err) {
                console.error("Failed to fetch sessions", err);
            } finally {
                setLoading(false);
            }
        };
        fetchSessions();
    }, []);

    if (loading) {
        return (
            <div className="space-y-4 animate-pulse">
                {[1, 2].map(i => (
                    <div key={i} className="h-32 bg-gray-50 rounded-3xl"></div>
                ))}
            </div>
        );
    }

    if (sessions.length === 0) {
        return (
            <div className="bg-white/10 p-6 rounded-3xl border border-white/10">
                <p className="text-primary-100/70 text-sm font-medium">No sessions scheduled yet.</p>
                <Link href="/marketplace" className="text-white text-xs font-black uppercase tracking-widest mt-4 flex items-center gap-1 hover:underline">
                    Browse Marketplace <ChevronRight size={12} />
                </Link>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {sessions.map((session) => (
                <div
                    key={session.id}
                    className="bg-white/10 p-5 rounded-3xl border border-white/20 hover:bg-white/20 transition-all group cursor-pointer"
                >
                    <div className="flex justify-between items-start mb-4">
                        <div className="px-3 py-1 bg-white/20 rounded-full text-[10px] font-black uppercase tracking-widest text-white">
                            Session #{session.session_number}
                        </div>
                        {session.meeting_link && (
                            <div className="p-2 bg-green-500 text-white rounded-lg shadow-lg">
                                <Video size={14} />
                            </div>
                        )}
                    </div>

                    <h4 className="text-white font-bold mb-3 flex items-center gap-2">
                        <Calendar size={14} className="text-primary-200" />
                        {format(new Date(session.scheduled_at), "MMM d, h:mm a")}
                    </h4>

                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1.5 text-primary-100/80 text-xs font-bold">
                            <Clock size={12} />
                            {session.duration_minutes} min
                        </div>
                        <div className="flex items-center gap-1.5 text-primary-100/80 text-xs font-bold">
                            <MapPin size={12} />
                            Online
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
}
