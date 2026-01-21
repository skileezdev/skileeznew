"use client";

import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Clock, ShieldCheck, Mail, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

export default function CoachPendingPage() {
    const { user, loading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!loading) {
            if (!user) {
                router.push("/auth/login");
            } else if (user.current_role !== "coach") {
                router.push("/dashboard");
            } else if (user.onboarding_completed && user.coach_profile?.is_approved) {
                router.push("/dashboard");
            } else if (!user.onboarding_completed) {
                router.push("/onboarding");
            }
        }
    }, [user, loading, router]);

    if (loading || !user) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-primary/5 via-purple-500/5 to-pink-500/5 flex items-center justify-center p-4">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="max-w-2xl w-full bg-white rounded-[2.5rem] shadow-2xl overflow-hidden border border-white/50"
            >
                <div className="p-12 text-center">
                    <div className="w-24 h-24 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-8 animate-pulse">
                        <Clock className="w-12 h-12 text-amber-600" />
                    </div>

                    <h1 className="text-4xl font-black text-gray-900 mb-4 tracking-tight">
                        Application Under Review
                    </h1>

                    <p className="text-xl text-gray-500 font-medium mb-12 leading-relaxed">
                        Great work, {user.first_name}! Your profile is complete. Our team is now reviewing your application to ensure the best experience for our students.
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                        <div className="p-6 bg-gray-50 rounded-2xl border border-gray-100">
                            <ShieldCheck className="w-8 h-8 text-primary mx-auto mb-3" />
                            <h3 className="font-bold text-gray-900 text-sm mb-1">Quality Check</h3>
                            <p className="text-xs text-gray-400">Verifying skills & bio</p>
                        </div>
                        <div className="p-6 bg-gray-50 rounded-2xl border border-gray-100">
                            <Mail className="w-8 h-8 text-purple-500 mx-auto mb-3" />
                            <h3 className="font-bold text-gray-900 text-sm mb-1">Email Notice</h3>
                            <p className="text-xs text-gray-400">We'll notify you soon</p>
                        </div>
                        <div className="p-6 bg-gray-50 rounded-2xl border border-gray-100">
                            <Clock className="w-8 h-8 text-amber-500 mx-auto mb-3" />
                            <h3 className="font-bold text-gray-900 text-sm mb-1">24-48 Hours</h3>
                            <p className="text-xs text-gray-400">Average review time</p>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div className="p-4 bg-primary/5 rounded-2xl border border-primary/20 text-primary-700 font-bold text-sm">
                            You currently have limited access until approved.
                        </div>

                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <button
                                onClick={() => router.push('/')}
                                className="px-8 py-4 bg-gray-900 text-white rounded-2xl font-black shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all flex items-center justify-center gap-2"
                            >
                                <ArrowLeft size={20} />
                                Back to Home
                            </button>
                            <Link
                                href="/profile/edit"
                                className="px-8 py-4 bg-white border-2 border-gray-100 text-gray-600 rounded-2xl font-black hover:bg-gray-50 transition-all flex items-center justify-center"
                            >
                                Edit Profile
                            </Link>
                        </div>
                    </div>

                    <p className="mt-12 text-sm text-gray-400 font-medium italic">
                        "Your knowledge is your power. We can't wait to share it with the world."
                    </p>
                </div>
            </motion.div>
        </div>
    );
}
