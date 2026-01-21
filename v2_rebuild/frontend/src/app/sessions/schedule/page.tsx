"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import {
    Calendar as CalendarIcon,
    ChevronLeft,
    ChevronRight,
    Clock,
    Video,
    User,
    Plus,
    Filter
} from "lucide-react";
import {
    format,
    addMonths,
    subMonths,
    startOfMonth,
    endOfMonth,
    startOfWeek,
    endOfWeek,
    isSameMonth,
    isSameDay,
    addDays,
    eachDayOfInterval
} from "date-fns";
import Link from "next/link";

export default function SchedulingPage() {
    const { user } = useAuth();
    const [currentMonth, setCurrentMonth] = useState(new Date());
    const [sessions, setSessions] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedDate, setSelectedDate] = useState(new Date());

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

    const renderHeader = () => (
        <div className="flex items-center justify-between mb-12">
            <div>
                <h1 className="text-5xl font-black text-gray-900 tracking-tight">Schedule</h1>
                <p className="text-gray-400 mt-2 text-lg font-medium">Manage your upcoming learning blocks.</p>
            </div>
            <div className="flex items-center gap-4 bg-white p-2 rounded-3xl shadow-sm border border-gray-100">
                <button
                    onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}
                    className="p-3 hover:bg-gray-50 rounded-2xl transition-colors text-gray-400 hover:text-primary-600"
                >
                    <ChevronLeft size={24} />
                </button>
                <h2 className="text-xl font-black text-gray-900 px-4 min-w-[180px] text-center">
                    {format(currentMonth, 'MMMM yyyy')}
                </h2>
                <button
                    onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
                    className="p-3 hover:bg-gray-50 rounded-2xl transition-colors text-gray-400 hover:text-primary-600"
                >
                    <ChevronRight size={24} />
                </button>
            </div>
        </div>
    );

    const renderDays = () => {
        const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        return (
            <div className="grid grid-cols-7 mb-4">
                {days.map(day => (
                    <div key={day} className="text-center text-[10px] font-black text-gray-400 uppercase tracking-[0.2em]">
                        {day}
                    </div>
                ))}
            </div>
        );
    };

    const renderCells = () => {
        const monthStart = startOfMonth(currentMonth);
        const monthEnd = endOfMonth(monthStart);
        const startDate = startOfWeek(monthStart);
        const endDate = endOfWeek(monthEnd);

        const rows = [];
        let days = [];
        let day = startDate;
        let formattedDate = "";

        while (day <= endDate) {
            for (let i = 0; i < 7; i++) {
                formattedDate = format(day, 'd');
                const cloneDay = day;
                const sessionsOfDay = sessions.filter(s => isSameDay(new Date(s.scheduled_at), cloneDay));
                const isSelected = isSameDay(day, selectedDate);
                const isCurrentMonth = isSameMonth(day, monthStart);

                days.push(
                    <div
                        key={day.toString()}
                        className={`min-h-[140px] p-4 border border-gray-50 bg-white transition-all cursor-pointer group hover:bg-primary-50/30 ${!isCurrentMonth ? "opacity-30" : ""
                            } ${isSelected ? "ring-2 ring-primary-500 ring-inset bg-primary-50/50" : ""}`}
                        onClick={() => setSelectedDate(cloneDay)}
                    >
                        <span className={`text-sm font-black ${isSelected ? "text-primary-600" : "text-gray-400"}`}>
                            {formattedDate}
                        </span>
                        <div className="mt-2 space-y-1">
                            {sessionsOfDay.map(session => (
                                <div
                                    key={session.id}
                                    className="px-2 py-1.5 bg-primary-600 text-white rounded-lg text-[10px] font-bold truncate shadow-sm hover:scale-105 transition-transform"
                                >
                                    {format(new Date(session.scheduled_at), 'h:mm a')} • {session.session_number}
                                </div>
                            ))}
                        </div>
                    </div>
                );
                day = addDays(day, 1);
            }
            rows.push(
                <div className="grid grid-cols-7" key={day.toString()}>
                    {days}
                </div>
            );
            days = [];
        }
        return <div className="rounded-[2.5rem] overflow-hidden border border-gray-100 shadow-2xl">{rows}</div>;
    };

    return (
        <div className="min-h-screen bg-[#FDFDFF] pt-32 pb-12 px-8">
            <div className="max-w-7xl mx-auto">
                {renderHeader()}

                <div className="grid grid-cols-1 lg:grid-cols-4 gap-12">
                    {/* Calendar Area */}
                    <div className="lg:col-span-3">
                        {renderDays()}
                        {renderCells()}
                    </div>

                    {/* Details Sidebar */}
                    <div className="space-y-8">
                        <div className="bg-gray-900 rounded-[2.5rem] p-8 text-white shadow-2xl">
                            <div className="flex items-center gap-3 mb-6">
                                <CalendarIcon className="text-primary-400" size={20} />
                                <h3 className="text-lg font-black tracking-tight">Agenda for {format(selectedDate, 'MMM do')}</h3>
                            </div>

                            <div className="space-y-4">
                                {sessions.filter(s => isSameDay(new Date(s.scheduled_at), selectedDate)).length > 0 ? (
                                    sessions.filter(s => isSameDay(new Date(s.scheduled_at), selectedDate)).map(session => (
                                        <Link
                                            key={session.id}
                                            href={`/sessions/join/${session.id}`}
                                            className="block p-5 bg-white/10 rounded-2xl hover:bg-white/20 transition-all border border-white/5 group"
                                        >
                                            <div className="flex justify-between items-start mb-4">
                                                <div className="p-2 bg-primary-500 rounded-xl">
                                                    <Video size={16} />
                                                </div>
                                                <span className="text-[10px] font-black uppercase tracking-widest text-primary-400">
                                                    {session.status}
                                                </span>
                                            </div>
                                            <h4 className="font-bold text-lg mb-1 leading-tight">Session #{session.session_number}</h4>
                                            <div className="flex items-center gap-2 text-xs text-white/60 font-medium">
                                                <Clock size={12} /> {format(new Date(session.scheduled_at), 'h:mm a')} • {session.duration_minutes}m
                                            </div>
                                        </Link>
                                    ))
                                ) : (
                                    <div className="py-12 text-center">
                                        <div className="w-12 h-12 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-4 grayscale">
                                            <Clock className="text-white/20" />
                                        </div>
                                        <p className="text-white/40 text-sm font-medium">No sessions scheduled for this day.</p>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Quick Actions */}
                        <div className="bg-white rounded-[2.5rem] p-8 border border-gray-100 shadow-xl">
                            <h3 className="text-sm font-black text-gray-900 uppercase tracking-widest mb-6">Quick Actions</h3>
                            <div className="space-y-3">
                                <button className="w-full py-4 px-6 bg-gray-50 text-gray-900 rounded-2xl font-bold flex items-center gap-3 hover:bg-gray-100 transition-all">
                                    <div className="p-2 bg-white rounded-lg shadow-sm">
                                        <Plus size={16} className="text-primary-600" />
                                    </div>
                                    Book New Session
                                </button>
                                <button className="w-full py-4 px-6 bg-gray-50 text-gray-900 rounded-2xl font-bold flex items-center gap-3 hover:bg-gray-100 transition-all">
                                    <div className="p-2 bg-white rounded-lg shadow-sm">
                                        <Filter size={16} className="text-primary-600" />
                                    </div>
                                    Filter View
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
