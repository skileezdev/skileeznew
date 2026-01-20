"use client";

import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { Check, CheckCheck } from "lucide-react";

interface MessageBubbleProps {
    content: string;
    isOwn: boolean;
    timestamp: string;
    isRead?: boolean;
    senderName?: string;
    avatar?: string;
}

export function MessageBubble({ content, isOwn, timestamp, isRead, senderName, avatar }: MessageBubbleProps) {
    return (
        <div className={cn("flex w-full mb-4", isOwn ? "justify-end" : "justify-start")}>
            {!isOwn && (
                <div className="flex-shrink-0 mr-2 self-end">
                    {avatar ? (
                        <img src={avatar} alt={senderName} className="w-8 h-8 rounded-full object-cover" />
                    ) : (
                        <div className="w-8 h-8 bg-gradient-to-br from-gray-400 to-gray-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
                            {senderName?.[0] || "?"}
                        </div>
                    )}
                </div>
            )}

            <div className={cn(
                "max-w-[75%] md:max-w-[60%] flex flex-col",
                isOwn ? "items-end" : "items-start"
            )}>
                {!isOwn && senderName && (
                    <span className="text-[10px] text-gray-500 ml-1 mb-1 font-medium">{senderName}</span>
                )}

                <div className={cn(
                    "px-5 py-3 rounded-[1.25rem] text-sm leading-relaxed shadow-sm relative",
                    isOwn
                        ? "bg-gradient-to-br from-primary to-primary-600 text-white rounded-tr-sm"
                        : "bg-white border border-gray-100 text-gray-800 rounded-tl-sm"
                )}>
                    {content}
                </div>

                <div className="flex items-center mt-1 space-x-1">
                    <span className="text-[10px] text-gray-400 font-medium">
                        {format(new Date(timestamp), "h:mm a")}
                    </span>
                    {isOwn && (
                        <span className={isRead ? "text-primary" : "text-gray-300"}>
                            {isRead ? <CheckCheck size={12} /> : <Check size={12} />}
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
}
