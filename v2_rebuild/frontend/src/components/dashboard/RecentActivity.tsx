"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import {
    MessageCircle,
    FileText,
    Calendar,
    Bell,
    CheckCircle2
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";

interface Notification {
    id: number;
    title: string;
    message: string;
    type: string;
    created_at: string;
    is_read: boolean;
}

export default function RecentActivity() {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchNotifications = async () => {
            try {
                const res = await api.get("/messages/notifications");
                setNotifications(res.data.slice(0, 5)); // Only show last 5
            } catch (err) {
                console.error("Failed to fetch notifications", err);
            } finally {
                setLoading(false);
            }
        };
        fetchNotifications();
    }, []);

    const getIcon = (type: string) => {
        switch (type) {
            case "message": return <MessageCircle size={18} className="text-blue-500" />;
            case "contract": return <FileText size={18} className="text-purple-500" />;
            case "session": return <Calendar size={18} className="text-amber-500" />;
            case "system": return <Bell size={18} className="text-gray-500" />;
            default: return <CheckCircle2 size={18} className="text-green-500" />;
        }
    };

    if (loading) {
        return (
            <div className="space-y-4 animate-pulse">
                {[1, 2, 3].map(i => (
                    <div key={i} className="flex gap-4 p-4 rounded-2xl bg-gray-50">
                        <div className="w-10 h-10 bg-gray-200 rounded-xl"></div>
                        <div className="flex-1 space-y-2">
                            <div className="h-4 bg-gray-200 rounded w-1/3"></div>
                            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                        </div>
                    </div>
                ))}
            </div>
        );
    }

    if (notifications.length === 0) {
        return (
            <div className="text-center py-12">
                <p className="text-gray-400 font-medium italic">No recent activity found.</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {notifications.map((notif) => (
                <div
                    key={notif.id}
                    className="flex gap-4 p-4 rounded-2xl hover:bg-gray-50 transition-all border border-transparent hover:border-gray-100 group cursor-pointer"
                >
                    <div className="w-12 h-12 bg-white rounded-xl shadow-sm border border-gray-100 flex items-center justify-center group-hover:scale-110 transition-transform">
                        {getIcon(notif.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-start">
                            <h4 className="font-bold text-gray-900 truncate pr-4">{notif.title}</h4>
                            <span className="text-[10px] text-gray-400 font-bold whitespace-nowrap">
                                {formatDistanceToNow(new Date(notif.created_at), { addSuffix: true })}
                            </span>
                        </div>
                        <p className="text-sm text-gray-500 line-clamp-1 mt-0.5">{notif.message}</p>
                    </div>
                </div>
            ))}
        </div>
    );
}
