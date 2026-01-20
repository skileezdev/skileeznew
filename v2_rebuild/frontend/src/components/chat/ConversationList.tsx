"use client";

import { cn } from "@/lib/utils";
import { formatDistanceToNow } from "date-fns";

interface Conversation {
    user_id: number;
    name: string;
    avatar?: string;
    last_message: string;
    timestamp: string;
    unread: number;
    is_online?: boolean;
}

interface ConversationListProps {
    conversations: Conversation[];
    activeId?: number;
    onSelect: (id: number) => void;
}

export function ConversationList({ conversations, activeId, onSelect }: ConversationListProps) {
    return (
        <div className="flex flex-col space-y-2 p-2">
            {conversations.map((conv) => (
                <button
                    key={conv.user_id}
                    onClick={() => onSelect(conv.user_id)}
                    className={cn(
                        "flex items-center p-3 rounded-2xl transition-all duration-200 text-left w-full group hover:bg-white/60",
                        activeId === conv.user_id ? "bg-white shadow-md ring-1 ring-black/5" : "hover:shadow-sm"
                    )}
                >
                    <div className="relative flex-shrink-0 mr-4">
                        {conv.avatar ? (
                            <img src={conv.avatar} alt={conv.name} className="w-12 h-12 rounded-xl object-cover" />
                        ) : (
                            <div className="w-12 h-12 bg-gradient-to-br from-indigo-400 to-purple-500 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-inner">
                                {conv.name[0]}
                            </div>
                        )}
                        {conv.is_online && (
                            <div className="absolute -bottom-1 -right-1 w-3.5 h-3.5 bg-green-500 border-2 border-white rounded-full"></div>
                        )}
                    </div>

                    <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-baseline mb-1">
                            <h4 className={cn(
                                "font-bold truncate text-gray-900 group-hover:text-primary transition-colors",
                                activeId === conv.user_id ? "text-primary" : ""
                            )}>
                                {conv.name}
                            </h4>
                            <span className="text-[10px] font-medium text-gray-400 flex-shrink-0 ml-2">
                                {formatDistanceToNow(new Date(conv.timestamp), { addSuffix: false })}
                            </span>
                        </div>
                        <p className={cn(
                            "text-xs truncate",
                            conv.unread > 0 ? "font-bold text-gray-800" : "text-gray-500",
                            activeId === conv.user_id ? "text-primary/80" : ""
                        )}>
                            {conv.last_message}
                        </p>
                    </div>

                    {conv.unread > 0 && (
                        <div className="ml-3 flex-shrink-0">
                            <span className="inline-flex items-center justify-center w-5 h-5 bg-primary text-white text-[10px] font-bold rounded-full shadow-lg shadow-primary/30">
                                {conv.unread}
                            </span>
                        </div>
                    )}
                </button>
            ))}
        </div>
    );
}
