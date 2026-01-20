"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import api from "@/lib/api";
import { Mail, Lock, User, Eye, EyeOff, ArrowRight, Briefcase, BookOpen } from "lucide-react";
import { motion } from "framer-motion";

export default function SignupPage() {
    const router = useRouter();
    const [formData, setFormData] = useState({
        first_name: "",
        last_name: "",
        email: "",
        password: "",
        confirm_password: "",
        is_student: true,
        is_coach: false,
    });
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        if (formData.password !== formData.confirm_password) {
            setError("Passwords do not match");
            return;
        }

        if (!formData.is_student && !formData.is_coach) {
            setError("Please select at least one role");
            return;
        }

        setLoading(true);

        try {
            await api.post("/auth/register", {
                first_name: formData.first_name,
                last_name: formData.last_name,
                email: formData.email,
                password: formData.password,
                is_student: formData.is_student,
                is_coach: formData.is_coach,
            });
            router.push("/auth/login?registered=true");
        } catch (err: any) {
            setError(err.response?.data?.detail || "Registration failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-primary/5 via-purple-500/5 to-pink-500/5 flex items-center justify-center p-4 py-12">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-2xl"
            >
                {/* Logo */}
                <Link href="/" className="flex items-center justify-center space-x-3 mb-8">
                    <div className="w-12 h-12 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center shadow-lg">
                        <span className="text-white font-bold text-2xl">S</span>
                    </div>
                    <span className="text-3xl font-black tracking-tight text-foreground">Skileez</span>
                </Link>

                {/* Signup Card */}
                <div className="glass-panel rounded-[2rem] p-8 shadow-2xl border-white/50">
                    <div className="text-center mb-8">
                        <h1 className="text-3xl font-black text-gray-900 mb-2">Create Your Account</h1>
                        <p className="text-gray-500 font-medium">Join thousands of learners and coaches</p>
                    </div>

                    {error && (
                        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
                            <p className="text-sm text-red-600 font-medium">{error}</p>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* Role Selection */}
                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-3">I want to join as:</label>
                            <div className="grid grid-cols-2 gap-4">
                                <button
                                    type="button"
                                    onClick={() => setFormData({ ...formData, is_student: !formData.is_student })}
                                    className={`p-4 rounded-xl border-2 transition-all ${formData.is_student
                                            ? "border-primary bg-primary/5 shadow-md"
                                            : "border-gray-200 hover:border-gray-300"
                                        }`}
                                >
                                    <BookOpen className={`w-8 h-8 mx-auto mb-2 ${formData.is_student ? "text-primary" : "text-gray-400"}`} />
                                    <p className={`font-bold ${formData.is_student ? "text-primary" : "text-gray-600"}`}>Student</p>
                                    <p className="text-xs text-gray-500 mt-1">Learn new skills</p>
                                </button>

                                <button
                                    type="button"
                                    onClick={() => setFormData({ ...formData, is_coach: !formData.is_coach })}
                                    className={`p-4 rounded-xl border-2 transition-all ${formData.is_coach
                                            ? "border-purple-600 bg-purple-50 shadow-md"
                                            : "border-gray-200 hover:border-gray-300"
                                        }`}
                                >
                                    <Briefcase className={`w-8 h-8 mx-auto mb-2 ${formData.is_coach ? "text-purple-600" : "text-gray-400"}`} />
                                    <p className={`font-bold ${formData.is_coach ? "text-purple-600" : "text-gray-600"}`}>Coach</p>
                                    <p className="text-xs text-gray-500 mt-1">Share expertise</p>
                                </button>
                            </div>
                        </div>

                        {/* Name Fields */}
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-2">First Name</label>
                                <div className="relative">
                                    <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                    <input
                                        type="text"
                                        value={formData.first_name}
                                        onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                                        className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all font-medium"
                                        placeholder="John"
                                        required
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-2">Last Name</label>
                                <input
                                    type="text"
                                    value={formData.last_name}
                                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all font-medium"
                                    placeholder="Doe"
                                    required
                                />
                            </div>
                        </div>

                        {/* Email */}
                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-2">Email</label>
                            <div className="relative">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                <input
                                    type="email"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all font-medium"
                                    placeholder="you@example.com"
                                    required
                                />
                            </div>
                        </div>

                        {/* Password */}
                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-2">Password</label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                <input
                                    type={showPassword ? "text" : "password"}
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    className="w-full pl-12 pr-12 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all font-medium"
                                    placeholder="••••••••"
                                    required
                                    minLength={8}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                                >
                                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                                </button>
                            </div>
                        </div>

                        {/* Confirm Password */}
                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-2">Confirm Password</label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                <input
                                    type={showPassword ? "text" : "password"}
                                    value={formData.confirm_password}
                                    onChange={(e) => setFormData({ ...formData, confirm_password: e.target.value })}
                                    className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all font-medium"
                                    placeholder="••••••••"
                                    required
                                />
                            </div>
                        </div>

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-gradient-to-r from-primary to-purple-600 text-white py-4 rounded-xl font-bold text-lg shadow-lg shadow-primary/30 hover:shadow-xl hover:scale-[1.02] disabled:opacity-50 disabled:scale-100 transition-all flex items-center justify-center gap-2"
                        >
                            {loading ? (
                                <div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin"></div>
                            ) : (
                                <>
                                    Create Account
                                    <ArrowRight size={20} />
                                </>
                            )}
                        </button>
                    </form>

                    {/* Divider */}
                    <div className="relative my-8">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-gray-200"></div>
                        </div>
                        <div className="relative flex justify-center text-sm">
                            <span className="px-4 bg-white text-gray-500 font-medium">Already have an account?</span>
                        </div>
                    </div>

                    {/* Sign In Link */}
                    <Link
                        href="/auth/login"
                        className="block w-full text-center py-4 border-2 border-gray-200 rounded-xl font-bold text-gray-700 hover:bg-gray-50 hover:border-gray-300 transition-all"
                    >
                        Sign In
                    </Link>
                </div>
            </motion.div>
        </div>
    );
}
