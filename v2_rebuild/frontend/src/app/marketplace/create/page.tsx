"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { DollarSign, Clock, Target, FileText, Tag, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";

export default function CreateRequestPage() {
    const router = useRouter();
    const [formData, setFormData] = useState({
        title: "",
        description: "",
        budget: "",
        experience_level: "intermediate",
        duration: "1-3 months",
        skills_required: "",
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            await api.post("/marketplace/requests", {
                ...formData,
                budget: parseFloat(formData.budget),
            });
            router.push("/marketplace?created=true");
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to create request");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-muted/30 pt-32 pb-12">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <div className="mb-8">
                        <h1 className="text-4xl font-black text-gray-900 mb-2">Post a Learning Request</h1>
                        <p className="text-gray-500 font-medium">Describe what you want to learn and connect with expert coaches</p>
                    </div>

                    {error && (
                        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
                            <p className="text-sm text-red-600 font-medium">{error}</p>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="bg-white rounded-[2rem] shadow-lg border border-gray-100 p-8 space-y-8">
                        {/* Title */}
                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
                                <FileText size={18} className="text-primary" />
                                Request Title
                            </label>
                            <input
                                type="text"
                                value={formData.title}
                                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all font-medium"
                                placeholder="e.g., Learn Python for Data Science"
                                required
                            />
                            <p className="text-xs text-gray-500 mt-2">Be specific about what you want to learn</p>
                        </div>

                        {/* Description */}
                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-2">Description</label>
                            <textarea
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all font-medium resize-none"
                                rows={6}
                                placeholder="Describe your learning goals, current skill level, and what you hope to achieve..."
                                required
                            />
                        </div>

                        {/* Budget & Duration Grid */}
                        <div className="grid md:grid-cols-2 gap-6">
                            {/* Budget */}
                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
                                    <DollarSign size={18} className="text-green-500" />
                                    Budget (USD)
                                </label>
                                <input
                                    type="number"
                                    value={formData.budget}
                                    onChange={(e) => setFormData({ ...formData, budget: e.target.value })}
                                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all font-medium"
                                    placeholder="500"
                                    min="0"
                                    step="0.01"
                                    required
                                />
                            </div>

                            {/* Duration */}
                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
                                    <Clock size={18} className="text-blue-500" />
                                    Duration
                                </label>
                                <select
                                    value={formData.duration}
                                    onChange={(e) => setFormData({ ...formData, duration: e.target.value })}
                                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all font-medium"
                                >
                                    <option value="less than 1 month">Less than 1 month</option>
                                    <option value="1-3 months">1-3 months</option>
                                    <option value="3-6 months">3-6 months</option>
                                    <option value="more than 6 months">More than 6 months</option>
                                </select>
                            </div>
                        </div>

                        {/* Experience Level */}
                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
                                <Target size={18} className="text-purple-500" />
                                Experience Level
                            </label>
                            <div className="grid grid-cols-3 gap-4">
                                {["beginner", "intermediate", "advanced"].map((level) => (
                                    <button
                                        key={level}
                                        type="button"
                                        onClick={() => setFormData({ ...formData, experience_level: level })}
                                        className={`p-4 rounded-xl border-2 transition-all capitalize font-bold ${formData.experience_level === level
                                                ? "border-primary bg-primary/5 text-primary shadow-md"
                                                : "border-gray-200 text-gray-600 hover:border-gray-300"
                                            }`}
                                    >
                                        {level}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Skills Required */}
                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
                                <Tag size={18} className="text-orange-500" />
                                Skills Required
                            </label>
                            <input
                                type="text"
                                value={formData.skills_required}
                                onChange={(e) => setFormData({ ...formData, skills_required: e.target.value })}
                                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all font-medium"
                                placeholder="Python, Machine Learning, Data Analysis (comma-separated)"
                            />
                            <p className="text-xs text-gray-500 mt-2">List the skills you're looking for in a coach</p>
                        </div>

                        {/* Submit Button */}
                        <div className="flex gap-4 pt-6 border-t border-gray-100">
                            <button
                                type="button"
                                onClick={() => router.back()}
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
                                        Post Request
                                        <ArrowRight size={20} />
                                    </>
                                )}
                            </button>
                        </div>
                    </form>
                </motion.div>
            </div>
        </div>
    );
}
