"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { Calendar, Clock, Video, MoreHorizontal, User } from "lucide-react";
import { format, isPast, isFuture, addMinutes } from "date-fns";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";

export default function SessionsPage() {
    const { user } = useAuth();
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSessions = async () => {
            try {
                const res = await api.get("/contracts/sessions/all");
                setSessions(res.data);
            } catch (err) {
                console.error("Failed to fetch sessions", err);
            } finally {
                setLoading(false);
            }
        };

        fetchSessions();
    }, []);

    const upcomingSessions = sessions.filter((s: any) => s.scheduled_at && isFuture(new Date(s.scheduled_at)));
    const pastSessions = sessions.filter((s: any) => s.scheduled_at && isPast(new Date(s.scheduled_at)));
    const unscheduledSessions = sessions.filter((s: any) => !s.scheduled_at);

    const SessionCard = ({ session, isUnscheduled = false }: { session: any, isUnscheduled?: boolean }) => {
        // Logic for Join Button: 10 mins before start
        const canJoin = session.scheduled_at &&
            isPast(addMinutes(new Date(session.scheduled_at), -10)) &&
            isFuture(addMinutes(new Date(session.scheduled_at), session.duration_minutes));

        return (
            <div className="bg-white rounded-[1.5rem] p-6 shadow-sm border border-gray-100 flex flex-col md:flex-row items-center justify-between gap-6 hover:shadow-md transition-all">
                <div className="flex items-center gap-6 w-full md:w-auto">
                    <div className={`w-16 h-16 rounded-2xl flex flex-col items-center justify-center font-bold text-gray-900 border ${canJoin ? "bg-green-50 border-green-200 text-green-700 animate-pulse" : "bg-gray-50 border-gray-100"}`}>
                        {isUnscheduled ? (
                            <Calendar className="w-6 h-6 text-gray-400" />
                        ) : (
                            <>
                                <span className="text-xl">{format(new Date(session.scheduled_at!), "d")}</span>
                                <span className="text-[10px] uppercase tracking-wider">{format(new Date(session.scheduled_at!), "MMM")}</span>
                            </>
                        )}
                    </div>

                    <div>
                        <h3 className="text-lg font-bold text-gray-900">Session #{session.session_number}</h3>
                        <div className="flex items-center gap-3 mt-1 text-sm text-gray-500 font-medium">
                            {isUnscheduled ? (
                                <span className="text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full">Unscheduled</span>
                            ) : (
                                <>
                                    <Clock size={14} />
                                    <span>{format(new Date(session.scheduled_at!), "h:mm a")} - {format(addMinutes(new Date(session.scheduled_at!), session.duration_minutes), "h:mm a")}</span>
                                </>
                            )}
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-3 w-full md:w-auto">
                    {canJoin ? (
                        <Link
                            href={session.meeting_link || "#"}
                            target="_blank"
                            className="flex-1 md:flex-none px-6 py-3 bg-green-600 text-white rounded-xl font-bold hover:bg-green-700 transition-all shadow-lg shadow-green-200 flex items-center justify-center gap-2"
                        >
                            <Video size={18} />
                            Join Meeting
                        </Link>
                    ) : (
                        isUnscheduled ? (
                            <button
                                className="flex-1 md:flex-none px-6 py-3 bg-primary text-white rounded-xl font-bold hover:bg-primary-700 transition-all shadow-lg shadow-primary/20"
                            >
                                Schedule Now
                            </button>
                        ) : (
                            <button
                                className="flex-1 md:flex-none px-6 py-3 bg-white border border-gray-200 text-gray-700 rounded-xl font-bold hover:bg-gray-50 transition-all"
                            >
                                Reschedule
                            </button>
                        )
                    )}

                    <button className="p-3 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-xl transition-all">
                        <MoreHorizontal size={20} />
                    </button>
                </div>
            </div>
        );
    };

    return (
        <div className="min-h-screen bg-muted/30 pt-32 pb-12">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
                <h1 className="text-4xl font-black text-gray-900 tracking-tight mb-8">Sessions</h1>

                {loading ? (
                    <div className="space-y-4">
                        {[1, 2, 3].map(i => <div key={i} className="h-24 bg-white rounded-3xl animate-pulse" />)}
                    </div>
                ) : (
                    <div className="space-y-12">
                        {/* Unscheduled */}
                        {unscheduledSessions.length > 0 && (
                            <section>
                                <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                                    <div className="w-2 h-2 rounded-full bg-amber-500"></div>
                                    Action Required
                                </h2>
                                <div className="space-y-4">
                                    {unscheduledSessions.map((session: any) => (
                                        <SessionCard key={session.id} session={session} isUnscheduled />
                                    ))}
                                </div>
                            </section>
                        )}

                        {/* Upcoming */}
                        <section>
                            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full bg-green-500"></div>
                                Upcoming
                            </h2>
                            {upcomingSessions.length > 0 ? (
                                <div className="space-y-4">
                                    {upcomingSessions.map((session: any) => (
                                        <SessionCard key={session.id} session={session} />
                                    ))}
                                </div>
                            ) : (
                                <p className="text-gray-500 text-sm italic">No upcoming sessions.</p>
                            )}
                        </section>

                        {/* Past */}
                        <section>
                            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full bg-gray-300"></div>
                                Past
                            </h2>
                            {pastSessions.length > 0 ? (
                                <div className="space-y-4 opacity-70 hover:opacity-100 transition-opacity">
                                    {pastSessions.map((session: any) => (
                                        <SessionCard key={session.id} session={session} />
                                    ))}
                                </div>
                            ) : (
                                <p className="text-gray-500 text-sm italic">No past sessions.</p>
                            )}
                        </section>
                    </div>
                )}
            </div>
        </div>
    );
}
