"use client";

import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const { user, loading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!loading) {
            if (!user) {
                router.push("/auth/login");
            } else if (!user.onboarding_completed) {
                router.push("/onboarding");
            } else if (user.current_role === "coach" && !user.coach_profile?.is_approved) {
                router.push("/onboarding/pending");
            }
        }
    }, [user, loading, router]);

    if (loading || !user || !user.onboarding_completed || (user.current_role === "coach" && !user.coach_profile?.is_approved)) {
        return (
            <div className="flex justify-center items-center h-screen bg-gray-50">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
            </div>
        );
    }

    return <>{children}</>;
}
