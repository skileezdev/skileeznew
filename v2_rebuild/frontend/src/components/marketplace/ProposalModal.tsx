"use client";

import { useState } from "react";
import api from "@/lib/api";
import { X, Send, DollarSign, Clock, Calendar } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface ProposalModalProps {
    isOpen: boolean;
    onClose: () => void;
    requestId: number;
    requestTitle: string;
    onSuccess?: () => void;
}

export function ProposalModal({ isOpen, onClose, requestId, requestTitle, onSuccess }: ProposalModalProps) {
    const [formData, setFormData] = useState({
        cover_letter: "",
        proposed_rate: "",
        estimated_hours: "",
        start_date: "",
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            await api.post(`/marketplace/requests/${requestId}/proposals`, {
                ...formData,
                proposed_rate: parseFloat(formData.proposed_rate),
                estimated_hours: parseInt(formData.estimated_hours),
            });
            onSuccess?.();
            onClose();
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to submit proposal");
        } finally {
            setLoading(false);
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <div className="fixed inset-0 bg-black/50 z-50" onClick={onClose}></div>

                    {/* Modal */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="fixed inset-0 z-50 flex items-center justify-center p-4"
                    >
                        <div className="bg-white rounded-[2rem] shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                            {/* Header */}
                            <div className="sticky top-0 bg-gradient-to-r from-primary to-purple-600 px-6 py-4 rounded-t-[2rem] flex items-center justify-between">
                                <div>
                                    <h3 className="text-xl font-black text-white">Submit Proposal</h3>
                                    <p className="text-sm text-white/80 font-medium mt-1">{requestTitle}</p>
                                </div>
                                <button onClick={onClose} className="p-2 text-white hover:bg-white/20 rounded-lg transition-colors">
                                    <X size={24} />
                                </button>
                            </div>

                            {/* Content */}
                            <form onSubmit={handleSubmit} className="p-6 space-y-6">
                                {error && (
                                    <div className="p-4 bg-red-50 border border-red-200 rounded-xl">
                                        <p className="text-sm text-red-600 font-medium">{error}</p>
                                    </div>
                                )}

                                {/* Cover Letter */}
                                <div>
                                    <label className="block text-sm font-bold text-gray-700 mb-2">Cover Letter</label>
                                    <textarea
                                        value={formData.cover_letter}
                                        onChange={(e) => setFormData({ ...formData, cover_letter: e.target.value })}
                                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all font-medium resize-none"
                                        rows={6}
                                        placeholder="Introduce yourself and explain why you're the best fit for this request..."
                                        required
                                    />
                                    <p className="text-xs text-gray-500 mt-2">Highlight your relevant experience and approach</p>
                                </div>

                                {/* Rate & Hours Grid */}
                                <div className="grid md:grid-cols-2 gap-6">
                                    {/* Proposed Rate */}
                                    <div>
                                        <label className="block text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
                                            <DollarSign size={18} className="text-green-500" />
                                            Hourly Rate (USD)
                                        </label>
                                        <input
                                            type="number"
                                            value={formData.proposed_rate}
                                            onChange={(e) => setFormData({ ...formData, proposed_rate: e.target.value })}
                                            className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all font-medium"
                                            placeholder="50"
                                            min="0"
                                            step="0.01"
                                            required
                                        />
                                    </div>

                                    {/* Estimated Hours */}
                                    <div>
                                        <label className="block text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
                                            <Clock size={18} className="text-blue-500" />
                                            Estimated Hours
                                        </label>
                                        <input
                                            type="number"
                                            value={formData.estimated_hours}
                                            onChange={(e) => setFormData({ ...formData, estimated_hours: e.target.value })}
                                            className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all font-medium"
                                            placeholder="20"
                                            min="1"
                                            required
                                        />
                                    </div>
                                </div>

                                {/* Start Date */}
                                <div>
                                    <label className="block text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
                                        <Calendar size={18} className="text-purple-500" />
                                        Proposed Start Date
                                    </label>
                                    <input
                                        type="date"
                                        value={formData.start_date}
                                        onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all font-medium"
                                        required
                                    />
                                </div>

                                {/* Total Estimate */}
                                {formData.proposed_rate && formData.estimated_hours && (
                                    <div className="bg-primary/5 border border-primary/20 rounded-xl p-4">
                                        <p className="text-sm text-gray-600 font-medium mb-1">Estimated Total</p>
                                        <p className="text-3xl font-black bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
                                            ${(parseFloat(formData.proposed_rate) * parseInt(formData.estimated_hours)).toFixed(2)}
                                        </p>
                                    </div>
                                )}

                                {/* Submit Button */}
                                <div className="flex gap-4 pt-6 border-t border-gray-100">
                                    <button
                                        type="button"
                                        onClick={onClose}
                                        className="px-6 py-3 border-2 border-gray-200 rounded-xl font-bold text-gray-700 hover:bg-gray-50 transition-all"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        disabled={loading}
                                        className="flex-1 bg-gradient-to-r from-primary to-purple-600 text-white py-3 rounded-xl font-bold shadow-lg shadow-primary/30 hover:shadow-xl hover:scale-[1.02] disabled:opacity-50 disabled:scale-100 transition-all flex items-center justify-center gap-2"
                                    >
                                        {loading ? (
                                            <div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin"></div>
                                        ) : (
                                            <>
                                                Submit Proposal
                                                <Send size={20} />
                                            </>
                                        )}
                                    </button>
                                </div>
                            </form>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
