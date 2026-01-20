"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";
import { X, Send, AlertCircle, Info } from "lucide-react";

interface ScreeningQuestion {
    id: number;
    question_text: string;
}

interface ProposalModalProps {
    requestId: number;
    requestTitle: string;
    screeningQuestions: ScreeningQuestion[];
    onClose: () => void;
    onSuccess: () => void;
}

export default function ProposalModal({ requestId, requestTitle, screeningQuestions, onClose, onSuccess }: ProposalModalProps) {
    const [formData, setFormData] = useState({
        cover_letter: "",
        price_per_session: "",
        session_count: "1",
        approach_summary: "",
    });
    const [answers, setAnswers] = useState<Record<number, string>>({});
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleAnswerChange = (questionId: number, text: string) => {
        setAnswers(prev => ({ ...prev, [questionId]: text }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        // Validate answers
        const unanswered = screeningQuestions.filter(q => !answers[q.id]?.trim());
        if (unanswered.length > 0) {
            setError("Please answer all screening questions.");
            setLoading(false);
            return;
        }

        try {
            await api.post("/marketplace/proposals", {
                learning_request_id: requestId,
                cover_letter: formData.cover_letter,
                price_per_session: parseFloat(formData.price_per_session),
                session_count: parseInt(formData.session_count),
                approach_summary: formData.approach_summary,
                answers: screeningQuestions.map(q => ({
                    question_id: q.id,
                    answer_text: answers[q.id]
                }))
            });
            onSuccess();
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to submit proposal");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-md flex items-center justify-center z-50 p-4 overflow-y-auto">
            <div className="bg-white rounded-[2.5rem] max-w-2xl w-full p-10 shadow-2xl relative animate-in fade-in zoom-in slide-in-from-bottom-4 duration-300">
                {/* Header Section */}
                <div className="flex justify-between items-start mb-8">
                    <div>
                        <div className="flex items-center gap-2 text-primary-600 font-black text-[10px] uppercase tracking-widest mb-2">
                            <Send size={14} /> Send Proposal
                        </div>
                        <h2 className="text-3xl font-black text-gray-900 leading-tight">Apply to Help</h2>
                        <p className="text-gray-400 font-medium text-sm mt-1">Project: <span className="text-gray-900">{requestTitle}</span></p>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-3 bg-gray-50 text-gray-400 hover:text-gray-900 hover:bg-gray-100 rounded-2xl transition-all active:scale-95"
                    >
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-8">
                    {error && (
                        <div className="p-4 bg-red-50 border border-red-100 text-red-600 text-sm rounded-2xl flex items-center gap-3 font-medium">
                            <AlertCircle size={18} />
                            {error}
                        </div>
                    )}

                    {/* Screening Questions Section (1:1 Mirror) */}
                    {screeningQuestions.length > 0 && (
                        <div className="space-y-6 bg-primary-50/30 p-6 rounded-3xl border border-primary-50">
                            <h3 className="flex items-center gap-2 font-black text-primary-800 text-xs uppercase tracking-widest">
                                <Info size={16} /> Screening Questions
                            </h3>
                            {screeningQuestions.map((q) => (
                                <div key={q.id}>
                                    <label className="block text-sm font-bold text-gray-800 mb-2">{q.question_text}</label>
                                    <textarea
                                        required
                                        rows={2}
                                        placeholder="Your detailed answer..."
                                        className="w-full px-5 py-4 bg-white border border-gray-100 rounded-2xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all text-sm shadow-sm"
                                        value={answers[q.id] || ""}
                                        onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                                    />
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Core Proposal Details */}
                    <div className="space-y-6">
                        <div>
                            <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2 ml-1">Your Pitch (Cover Letter)</label>
                            <textarea
                                required
                                rows={4}
                                minLength={50}
                                placeholder="Why are you the perfect match? Share your unique background and passion..."
                                className="w-full px-5 py-4 bg-gray-50/50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all text-sm"
                                value={formData.cover_letter}
                                onChange={(e) => setFormData({ ...formData, cover_letter: e.target.value })}
                            />
                            <p className="mt-2 text-[10px] text-gray-300 font-bold text-right italic">
                                {formData.cover_letter.length}/50 minimum characters
                            </p>
                        </div>

                        <div className="grid grid-cols-2 gap-6">
                            <div>
                                <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2 ml-1">Price per Session ($)</label>
                                <div className="relative">
                                    <span className="absolute left-5 top-1/2 -translate-y-1/2 text-gray-400 font-bold">$</span>
                                    <input
                                        type="number"
                                        required
                                        min="5"
                                        className="w-full pl-10 pr-5 py-4 bg-gray-50/50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all font-bold"
                                        value={formData.price_per_session}
                                        onChange={(e) => setFormData({ ...formData, price_per_session: e.target.value })}
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2 ml-1">Total Sessions</label>
                                <div className="relative">
                                    <span className="absolute left-5 top-1/2 -translate-y-1/2 text-gray-400 font-bold">#</span>
                                    <input
                                        type="number"
                                        required
                                        min="1"
                                        className="w-full pl-10 pr-5 py-4 bg-gray-50/50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all font-bold"
                                        value={formData.session_count}
                                        onChange={(e) => setFormData({ ...formData, session_count: e.target.value })}
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-4 pt-4 border-t border-gray-50">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 py-4 bg-gray-50 text-gray-500 font-black rounded-2xl hover:bg-gray-100 hover:text-gray-900 transition-all active:scale-95"
                        >
                            Back
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="flex-[2] py-4 bg-gradient-to-r from-primary-600 to-purple-600 text-white font-black rounded-2xl shadow-xl shadow-primary-200/50 hover:shadow-2xl hover:-translate-y-1 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                        >
                            {loading ? (
                                <svg className="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                            ) : (
                                <>
                                    Send Application <Send size={18} />
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
