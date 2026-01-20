"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";
import { motion } from "framer-motion";
import { ArrowRight, User, Globe, FileText, CheckCircle } from "lucide-react";

export default function OnboardingPage() {
    const { user, refreshUser } = useAuth();
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        bio: "",
        country: "",
        coach_title: "", // Only for coaches
        skills: "" // Only for coaches
    });

    const isCoach = user?.current_role === "coach";

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            await api.patch("/profiles/me", {
                ...formData,
                onboarding_completed: true
            });
            await refreshUser();
            router.push("/dashboard");
        } catch (error) {
            console.error("Onboarding failed", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-primary/5 via-purple-500/5 to-pink-500/5 flex items-center justify-center p-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-2xl"
            >
                <div className="glass-panel rounded-[2rem] p-8 shadow-2xl border-white/50">
                    <div className="text-center mb-8">
                        <div className="w-16 h-16 bg-gradient-to-br from-primary to-secondary rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg text-white">
                            <User size={32} strokeWidth={2.5} />
                        </div>
                        <h1 className="text-3xl font-black text-gray-900 mb-2">
                            Welcome, {user?.first_name}!
                        </h1>
                        <p className="text-gray-500 font-medium">Let's set up your profile to get started.</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">

                        {/* Two Column Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {/* Country */}
                            <div className="md:col-span-2">
                                <label className="block text-sm font-bold text-gray-700 mb-2">Location (Country)</label>
                                <div className="relative">
                                    <Globe className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                    <input
                                        type="text"
                                        value={formData.country}
                                        onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                                        className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all font-medium"
                                        placeholder="e.g. United States, United Arab Emirates"
                                        required
                                    />
                                </div>
                            </div>

                            {/* Coach Specific Fields */}
                            {isCoach && (
                                <>
                                    <div className="md:col-span-2">
                                        <label className="block text-sm font-bold text-gray-700 mb-2">Professional Title</label>
                                        <input
                                            type="text"
                                            value={formData.coach_title}
                                            onChange={(e) => setFormData({ ...formData, coach_title: e.target.value })}
                                            className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all font-medium"
                                            placeholder="e.g. Senior Software Engineer"
                                            required
                                        />
                                    </div>
                                    <div className="md:col-span-2">
                                        <label className="block text-sm font-bold text-gray-700 mb-2">Top Skills (Comma separated)</label>
                                        <input
                                            type="text"
                                            value={formData.skills}
                                            onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
                                            className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all font-medium"
                                            placeholder="e.g. React, Python, Leadership"
                                            required
                                        />
                                    </div>
                                </>
                            )}

                            {/* Bio */}
                            <div className="md:col-span-2">
                                <label className="block text-sm font-bold text-gray-700 mb-2">Bio</label>
                                <div className="relative">
                                    <FileText className="absolute left-4 top-4 w-5 h-5 text-gray-400" />
                                    <textarea
                                        value={formData.bio}
                                        onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                                        className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all font-medium min-h-[120px]"
                                        placeholder="Tell us a bit about yourself..."
                                        required
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-gradient-to-r from-primary to-purple-600 text-white py-4 rounded-xl font-bold text-lg shadow-lg shadow-primary/30 hover:shadow-xl hover:scale-[1.02] disabled:opacity-50 disabled:scale-100 transition-all flex items-center justify-center gap-2 mt-8"
                        >
                            {loading ? (
                                <div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin"></div>
                            ) : (
                                <>
                                    Complete Setup
                                    <ArrowRight size={20} />
                                </>
                            )}
                        </button>

                    </form>
                </div>
            </motion.div>
        </div>
    );
}
