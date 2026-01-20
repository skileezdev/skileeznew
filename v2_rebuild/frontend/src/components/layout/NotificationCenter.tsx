"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { Bell, MessageSquare, FileText, Calendar, X } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { motion, AnimatePresence } from "framer-motion";

interface Notification {
    id: number;
    title: string;
    message: string;
    type: string;
    is_read: boolean;
    created_at: string;
    related_id?: number;
    related_type?: string;
}

interface NotificationCenterProps {
    isOpen: boolean;
    onClose: () => void;
}

export function NotificationCenter({ isOpen, onClose }: NotificationCenterProps) {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!isOpen) return;

        const fetchNotifications = async () => {
            try {
                const res = await api.get("/marketplace/messages/notifications");
                setNotifications(res.data);
            } catch (err) {
                console.error("Failed to fetch notifications", err);
            } finally {
                setLoading(false);
            }
        };

        fetchNotifications();
        const interval = setInterval(fetchNotifications, 10000); // Poll every 10s
        return () => clearInterval(interval);
    }, [isOpen]);

    const getIcon = (type: string) => {
        switch (type) {
            case "message":
                return <MessageSquare size={18} className="text-blue-500" />;
            case "contract":
                return <FileText size={18} className="text-green-500" />;
            case "session":
                return <Calendar size={18} className="text-purple-500" />;
            default:
                return <Bell size={18} className="text-gray-500" />;
        }
    };

    const unreadCount = notifications.filter((n) => !n.is_read).length;

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <div className="fixed inset-0 z-40" onClick={onClose}></div>

                    {/* Notification Panel */}
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="absolute right-0 top-16 w-96 bg-white rounded-2xl shadow-2xl border border-gray-100 z-50 overflow-hidden"
                    >
                        {/* Header */}
                        <div className="bg-gradient-to-r from-primary/5 to-purple-500/5 px-6 py-4 border-b border-gray-100 flex items-center justify-between">
                            <div>
                                <h3 className="text-lg font-black text-gray-900">Notifications</h3>
                                {unreadCount > 0 && (
                                    <p className="text-xs text-gray-500 font-medium">{unreadCount} unread</p>
                                )}
                            </div>
                            <button onClick={onClose} className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors">
                                <X size={20} />
                            </button>
                        </div>

                        {/* Notifications List */}
                        <div className="max-h-96 overflow-y-auto">
                            {loading ? (
                                <div className="p-8 flex justify-center">
                                    <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                                </div>
                            ) : notifications.length > 0 ? (
                                <div className="divide-y divide-gray-100">
                                    {notifications.map((notif) => (
                                        <div
                                            key={notif.id}
                                            className={`p-4 hover:bg-gray-50 transition-colors cursor-pointer ${!notif.is_read ? "bg-primary/5" : ""
                                                }`}
                                        >
                                            <div className="flex items-start gap-3">
                                                <div className="flex-shrink-0 mt-1">{getIcon(notif.type)}</div>
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-start justify-between gap-2">
                                                        <h4 className="text-sm font-bold text-gray-900 truncate">{notif.title}</h4>
                                                        {!notif.is_read && (
                                                            <div className="w-2 h-2 bg-primary rounded-full flex-shrink-0 mt-1"></div>
                                                        )}
                                                    </div>
                                                    <p className="text-xs text-gray-600 mt-1 line-clamp-2">{notif.message}</p>
                                                    <p className="text-[10px] text-gray-400 font-medium mt-2">
                                                        {formatDistanceToNow(new Date(notif.created_at), { addSuffix: true })}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="p-12 text-center">
                                    <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
                                        <Bell className="w-8 h-8 text-gray-300" />
                                    </div>
                                    <h4 className="text-sm font-bold text-gray-900 mb-1">All caught up!</h4>
                                    <p className="text-xs text-gray-500">No new notifications</p>
                                </div>
                            )}
                        </div>

                        {/* Footer */}
                        {notifications.length > 0 && (
                            <div className="bg-gray-50 px-6 py-3 border-t border-gray-100">
                                <button className="text-xs font-bold text-primary hover:text-primary-700 transition-colors">
                                    Mark all as read
                                </button>
                            </div>
                        )}
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
