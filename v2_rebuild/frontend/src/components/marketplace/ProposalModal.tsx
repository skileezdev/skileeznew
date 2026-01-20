"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/api";

interface ProposalModalProps {
    requestId: number;
    requestTitle: string;
    onClose: () => void;
    onSuccess: () => void;
}

export default function ProposalModal({ requestId, requestTitle, onClose, onSuccess }: ProposalModalProps) {
    const [formData, setFormData] = useState({
        cover_letter: "",
        price_per_session: "",
        session_count: "1",
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            await apiFetch("/marketplace/proposals", {
                method: "POST",
                body: JSON.stringify({
                    learning_request_id: requestId,
                    cover_letter: formData.cover_letter,
                    price_per_session: parseFloat(formData.price_per_session),
                    session_count: parseInt(formData.session_count),
                }),
            });
            onSuccess();
        } catch (err: any) {
            setError(err.message || "Failed to submit proposal");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl max-w-xl w-full p-8 shadow-2xl animate-in fade-in zoom-in duration-200">
                <div className="flex justify-between items-start mb-6">
                    <h2 className="text-2xl font-bold text-gray-900">Submit Proposal</h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600">✕</button>
                </div>

                <p className="text-gray-500 mb-6 font-medium">For: <span className="text-indigo-600">{requestTitle}</span></p>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {error && <div className="text-red-500 text-sm">{error}</div>}

                    <div>
                        <label className="block text-sm font-medium text-gray-700">Cover Letter</label>
                        <textarea
                            required
                            rows={4}
                            placeholder="Why are you the best coach for this? (Min 50 characters)"
                            className="mt-1 block w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
                            value={formData.cover_letter}
                            onChange={(e) => setFormData({ ...formData, cover_letter: e.target.value })}
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Price per Session ($)</label>
                            <input
                                type="number"
                                required
                                className="mt-1 block w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
                                value={formData.price_per_session}
                                onChange={(e) => setFormData({ ...formData, price_per_session: e.target.value })}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Session Count</label>
                            <input
                                type="number"
                                required
                                min="1"
                                className="mt-1 block w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
                                value={formData.session_count}
                                onChange={(e) => setFormData({ ...formData, session_count: e.target.value })}
                            />
                        </div>
                    </div>

                    <div className="flex space-x-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 py-3 px-4 bg-gray-100 text-gray-700 font-bold rounded-xl hover:bg-gray-200 transition"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="flex-2 w-full py-3 px-4 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700 transition disabled:opacity-50"
                        >
                            {loading ? "Sending..." : "Send Proposal"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
