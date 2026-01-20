"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import {
    Plus,
    Trash2,
    HelpCircle,
    ArrowLeft,
    Sparkles,
    Target,
    Clock,
    DollarSign
} from "lucide-react";
import Link from "next/link";

export default function CreateRequestPage() {
    const [formData, setFormData] = useState({
        title: "",
        description: "",
        budget: "",
        experience_level: "beginner",
        skill_type: "short_term",
        sessions_needed: "1",
    });
    const [screeningQuestions, setScreeningQuestions] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const router = useRouter();

    const addQuestion = () => {
        if (screeningQuestions.length < 5) {
            setScreeningQuestions([...screeningQuestions, ""]);
        }
    };

    const removeQuestion = (index: number) => {
        setScreeningQuestions(screeningQuestions.filter((_, i) => i !== index));
    };

    const updateQuestion = (index: number, text: string) => {
        const newQuestions = [...screeningQuestions];
        newQuestions[index] = text;
        setScreeningQuestions(newQuestions);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            await api.post("/marketplace/requests", {
                ...formData,
                budget: formData.budget ? parseFloat(formData.budget) : null,
                sessions_needed: parseInt(formData.sessions_needed),
                screening_questions: screeningQuestions
                    .filter(q => q.trim() !== "")
                    .map(q => ({ question_text: q }))
            });
            router.push("/marketplace");
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to create request");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#FDFDFF] py-16 px-4 sm:px-6 lg:px-8 font-inter">
            <div className="max-w-3xl mx-auto">
                {/* Back Navigation */}
                <Link href="/marketplace" className="inline-flex items-center gap-2 text-gray-400 hover:text-gray-900 font-bold text-sm mb-12 transition-colors group">
                    <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" /> Back to Marketplace
                </Link>

                <div className="bg-white p-12 rounded-[3rem] shadow-xl shadow-gray-100/50 border border-gray-100 relative overflow-hidden">
                    {/* Decorative Gradient */}
                    <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-primary-400 via-purple-500 to-primary-600"></div>

                    <div className="mb-12">
                        <div className="flex items-center gap-2 text-primary-600 font-black text-[10px] uppercase tracking-widest mb-3">
                            <Sparkles size={14} /> Knowledge Seekers
                        </div>
                        <h1 className="text-4xl font-black text-gray-900 tracking-tight leading-tight">
                            Post your request.
                        </h1>
                        <p className="text-gray-400 mt-3 text-lg font-medium">
                            Tell the world what you want to learn and find the perfect match.
                        </p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-10">
                        {error && (
                            <div className="p-4 bg-red-50 border border-red-100 text-red-600 text-sm rounded-2xl flex items-center gap-3 font-medium animate-in fade-in slide-in-from-top-2">
                                <span className="p-1 bg-red-100 rounded-full">!</span>
                                {error}
                            </div>
                        )}

                        <div className="space-y-8">
                            {/* Basic Info */}
                            <div>
                                <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3 ml-1">Learning Title</label>
                                <input
                                    type="text"
                                    required
                                    placeholder="e.g., Master Advanced Figma Prototyping"
                                    className="w-full px-6 py-4 bg-gray-50/50 border border-gray-100 rounded-[1.5rem] focus:ring-2 focus:ring-primary-500 outline-none transition-all placeholder:text-gray-300 font-bold text-gray-800"
                                    value={formData.title}
                                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                />
                            </div>

                            <div>
                                <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3 ml-1">Project Deep-Dive</label>
                                <textarea
                                    required
                                    rows={5}
                                    placeholder="Be specific! Mention your goals, your current roadblocks, and what success looks like for you..."
                                    className="w-full px-6 py-4 bg-gray-50/50 border border-gray-100 rounded-[1.5rem] focus:ring-2 focus:ring-primary-500 outline-none transition-all placeholder:text-gray-300 font-medium text-gray-700 leading-relaxed"
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                />
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div>
                                    <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3 ml-1">Proposed Budget ($/Session)</label>
                                    <div className="relative">
                                        <DollarSign className="absolute left-6 top-1/2 -translate-y-1/2 text-gray-300" size={18} />
                                        <input
                                            type="number"
                                            placeholder="Leave blank for TBD"
                                            className="w-full pl-14 pr-6 py-4 bg-gray-50/50 border border-gray-100 rounded-[1.5rem] focus:ring-2 focus:ring-primary-500 outline-none transition-all font-bold text-gray-800"
                                            value={formData.budget}
                                            onChange={(e) => setFormData({ ...formData, budget: e.target.value })}
                                        />
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3 ml-1">Target Experience</label>
                                    <div className="relative">
                                        <Target className="absolute left-6 top-1/2 -translate-y-1/2 text-gray-300" size={18} />
                                        <select
                                            className="w-full pl-14 pr-6 py-4 bg-gray-50/50 border border-gray-100 rounded-[1.5rem] focus:ring-2 focus:ring-primary-500 outline-none transition-all font-bold text-gray-800 appearance-none"
                                            value={formData.experience_level}
                                            onChange={(e) => setFormData({ ...formData, experience_level: e.target.value })}
                                        >
                                            <option value="beginner">Beginner</option>
                                            <option value="intermediate">Intermediate</option>
                                            <option value="advanced">Advanced (Ninja)</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            {/* Screening Questions (V1 Mirror Core Logic) */}
                            <div className="space-y-6 pt-6 border-t border-gray-50">
                                <div className="flex justify-between items-center">
                                    <div>
                                        <h3 className="text-lg font-black text-gray-900 group flex items-center gap-2">
                                            Screening Questions
                                            <div className="w-1.5 h-1.5 bg-primary-500 rounded-full"></div>
                                        </h3>
                                        <p className="text-xs text-gray-400 font-medium">Ask potential coaches specific questions to vet their expertise.</p>
                                    </div>
                                    <button
                                        type="button"
                                        onClick={addQuestion}
                                        disabled={screeningQuestions.length >= 5}
                                        className="p-3 bg-primary-50 text-primary-600 rounded-2xl hover:bg-primary-100 transition-all active:scale-95 disabled:opacity-30"
                                    >
                                        <Plus size={20} />
                                    </button>
                                </div>

                                <div className="space-y-4">
                                    {screeningQuestions.map((q, index) => (
                                        <div key={index} className="flex gap-4 group animate-in slide-in-from-right-4 duration-300">
                                            <div className="flex-1 relative">
                                                <HelpCircle className="absolute left-5 top-1/2 -translate-y-1/2 text-primary-200" size={18} />
                                                <input
                                                    type="text"
                                                    required
                                                    placeholder={`Question #${index + 1}: e.g., Have you ever built a production SaaS?`}
                                                    className="w-full pl-14 pr-6 py-4 bg-white border border-gray-100 rounded-2xl focus:ring-2 focus:primary-500 outline-none transition-all text-sm font-semibold shadow-sm"
                                                    value={q}
                                                    onChange={(e) => updateQuestion(index, e.target.value)}
                                                />
                                            </div>
                                            <button
                                                type="button"
                                                onClick={() => removeQuestion(index)}
                                                className="p-4 bg-red-50 text-red-400 hover:text-red-600 hover:bg-red-100 rounded-2xl transition-all"
                                            >
                                                <Trash2 size={20} />
                                            </button>
                                        </div>
                                    ))}
                                    {screeningQuestions.length === 0 && (
                                        <div className="text-center py-8 px-6 bg-gray-50/50 rounded-[2rem] border-2 border-dashed border-gray-100">
                                            <p className="text-gray-400 text-xs font-bold italic tracking-wide">No screening questions added yet. Recommended for quality matches!</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-5 px-8 bg-gray-900 text-white font-black rounded-[1.5rem] shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all transform active:scale-[0.98] disabled:opacity-50 flex justify-center items-center gap-2 group text-lg"
                        >
                            {loading ? (
                                <div className="w-6 h-6 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                            ) : (
                                <>
                                    Launch Request <Plus size={22} className="group-hover:rotate-90 transition-transform duration-300" />
                                </>
                            )}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}
