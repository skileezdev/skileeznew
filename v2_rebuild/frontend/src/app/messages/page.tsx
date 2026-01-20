"use client";

import { useEffect, useState, useRef } from "react";
import api from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { ConversationList } from "@/components/chat/ConversationList";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { MessageInput } from "@/components/chat/MessageInput";
import { MessageSquare, MoreVertical, Phone, Video } from "lucide-react";
import { motion } from "framer-motion";

export default function MessagesPage() {
    const { user } = useAuth();

    interface Conversation {
        user_id: number;
        name: string;
        avatar?: string;
        last_message: string;
        timestamp: string;
        unread: number;
        is_online?: boolean;
    }

    interface Message {
        id: number;
        content: string;
        sender_id: number;
        recipient_id: number;
        created_at: string;
        is_read: boolean;
    }

    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(true);
    const [chatLoading, setChatLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Fetch Conversations
    useEffect(() => {
        if (!user) return;

        const fetchConversations = async () => {
            try {
                const res = await api.get("/marketplace/messages/conversations");
                setConversations(res.data);
            } catch (err) {
                console.error("Failed to fetch conversations", err);
            } finally {
                setLoading(false);
            }
        };

        fetchConversations();
        // Poll every 10s for new message previews
        const interval = setInterval(fetchConversations, 10000);
        return () => clearInterval(interval);
    }, [user]);

    // Fetch Messages for Active Conversation
    useEffect(() => {
        if (!activeConversationId) return;

        const fetchMessages = async () => {
            // Don't set loading on poll
            try {
                const res = await api.get(`/marketplace/messages/?other_user_id=${activeConversationId}`);
                setMessages(res.data);
            } catch (err) {
                console.error("Failed to fetch messages", err);
            }
        };

        setChatLoading(true);
        fetchMessages().then(() => setChatLoading(false));

        const interval = setInterval(fetchMessages, 3000); // 3s polling for active chat
        return () => clearInterval(interval);
    }, [activeConversationId]);

    // Scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, activeConversationId]);

    const handleSendMessage = async (content: string) => {
        if (!activeConversationId) return;

        try {
            // Optimistic updatre
            const fakeMsg = {
                id: Date.now(),
                content,
                sender_id: user?.id || 0,
                recipient_id: activeConversationId,
                created_at: new Date().toISOString(),
                is_read: false
            };
            setMessages((prev: any) => [...prev, fakeMsg]);

            await api.post("/marketplace/messages/", {
                content,
                recipient_id: activeConversationId,
                message_type: "TEXT"
            });

            // Refresh to get real ID and time
            const res = await api.get(`/marketplace/messages/?other_user_id=${activeConversationId}`);
            setMessages(res.data);
        } catch (err) {
            console.error("Failed to send message", err);
        }
    };

    const activeUser = conversations.find((c: any) => c.user_id === activeConversationId);

    return (
        <div className="h-screen pt-20 pb-4 bg-muted/30 flex justify-center">
            <div className="w-full max-w-7xl px-4 sm:px-6 lg:px-8 h-full">
                <div className="bg-white rounded-[2rem] shadow-2xl h-full flex overflow-hidden border border-border">
                    {/* Sidebar */}
                    <div className="w-full md:w-80 lg:w-96 border-r border-gray-100 flex flex-col bg-gray-50/50">
                        <div className="p-6 border-b border-gray-100">
                            <h1 className="text-2xl font-black text-gray-900 tracking-tight flex items-center">
                                Messages
                                <span className="ml-2 text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">{conversations.length}</span>
                            </h1>
                        </div>

                        <div className="flex-1 overflow-y-auto custom-scrollbar">
                            {loading ? (
                                <div className="p-4 space-y-4">
                                    {[1, 2, 3].map(i => <div key={i} className="h-20 bg-gray-200 rounded-2xl animate-pulse" />)}
                                </div>
                            ) : (
                                <ConversationList
                                    conversations={conversations}
                                    activeId={activeConversationId || undefined}
                                    onSelect={setActiveConversationId}
                                />
                            )}
                        </div>
                    </div>

                    {/* Chat Area */}
                    <div className="flex-1 flex flex-col bg-white relative">
                        {activeConversationId ? (
                            <>
                                {/* Chat Header */}
                                <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-white/80 backdrop-blur-md sticky top-0 z-10">
                                    <div className="flex items-center space-x-4">
                                        <div className="relative">
                                            {activeUser?.avatar ? (
                                                <img src={activeUser.avatar} className="w-10 h-10 rounded-full object-cover" />
                                            ) : (
                                                <div className="w-10 h-10 bg-gradient-to-br from-primary to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                                                    {activeUser?.name?.[0]}
                                                </div>
                                            )}
                                            <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white rounded-full"></div>
                                        </div>
                                        <div>
                                            <h3 className="font-bold text-gray-900">{activeUser?.name}</h3>
                                            <p className="text-xs text-green-500 font-medium">Online</p>
                                        </div>
                                    </div>

                                    <div className="flex items-center space-x-2">
                                        <button className="p-2.5 text-gray-400 hover:text-primary hover:bg-primary/5 rounded-xl transition-colors">
                                            <Phone size={20} />
                                        </button>
                                        <button className="p-2.5 text-gray-400 hover:text-primary hover:bg-primary/5 rounded-xl transition-colors">
                                            <Video size={20} />
                                        </button>
                                        <button className="p-2.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-xl transition-colors">
                                            <MoreVertical size={20} />
                                        </button>
                                    </div>
                                </div>

                                {/* Messages List */}
                                <div
                                    className="flex-1 overflow-y-auto p-6 custom-scrollbar bg-[url('/bg-pattern.svg')] bg-opacity-5"
                                    ref={scrollRef}
                                >
                                    {chatLoading && messages.length === 0 ? (
                                        <div className="flex justify-center pt-10">
                                            <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                                        </div>
                                    ) : (
                                        messages.map((msg: any) => (
                                            <MessageBubble
                                                key={msg.id}
                                                content={msg.content}
                                                timestamp={msg.created_at}
                                                isOwn={msg.sender_id === user?.id}
                                                isRead={msg.is_read}
                                                senderName={msg.sender_id === user?.id ? "You" : activeUser?.name}
                                            />
                                        ))
                                    )}
                                </div>

                                {/* Input Area */}
                                <MessageInput onSend={handleSendMessage} />
                            </>
                        ) : (
                            <div className="flex-1 flex flex-col items-center justify-center text-center p-8 bg-gray-50/30">
                                <div className="w-24 h-24 bg-gradient-to-br from-primary/10 to-purple-500/10 rounded-full flex items-center justify-center mb-6">
                                    <MessageSquare className="w-12 h-12 text-primary/40" />
                                </div>
                                <h3 className="text-2xl font-black text-gray-900 mb-2">Select a Conversation</h3>
                                <p className="text-gray-500 max-w-sm">Choose a person from the sidebar to start chatting. Your conversations are secure and private.</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
