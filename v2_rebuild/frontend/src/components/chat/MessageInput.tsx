"use client";

import { Send, Paperclip, Smile } from "lucide-react";
import { useState, KeyboardEvent } from "react";

interface MessageInputProps {
    onSend: (content: string) => void;
    disabled?: boolean;
}

export function MessageInput({ onSend, disabled }: MessageInputProps) {
    const [message, setMessage] = useState("");

    const handleSend = () => {
        if (message.trim() && !disabled) {
            onSend(message);
            setMessage("");
        }
    };

    const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="p-4 bg-white border-t border-gray-100">
            <div className="flex items-center space-x-2 bg-gray-50 rounded-2xl p-2 border border-transparent focus-within:border-primary/20 focus-within:bg-white focus-within:shadow-sm transition-all duration-200">
                <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-200/50 rounded-xl transition-colors">
                    <Paperclip size={20} />
                </button>

                <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Type your message..."
                    className="flex-1 bg-transparent border-none outline-none text-sm font-medium text-gray-800 placeholder-gray-400 py-2"
                    disabled={disabled}
                />

                <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-200/50 rounded-xl transition-colors">
                    <Smile size={20} />
                </button>

                <button
                    onClick={handleSend}
                    disabled={!message.trim() || disabled}
                    className="p-2.5 bg-gradient-to-br from-primary to-primary-600 text-white rounded-xl shadow-lg shadow-primary/30 hover:shadow-xl hover:scale-105 disabled:opacity-50 disabled:shadow-none disabled:scale-100 transition-all duration-200"
                >
                    <Send size={18} />
                </button>
            </div>
        </div>
    );
}
