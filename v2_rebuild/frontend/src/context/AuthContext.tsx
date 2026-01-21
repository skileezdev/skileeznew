"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

// Extended Profile Interfaces
interface Experience {
    title: string;
    company: string;
    start_date: string;
    is_current: boolean;
}

interface Education {
    degree: string;
    institution: string;
}

interface PortfolioItem {
    title: string;
    description: string;
    category: string;
}

interface Language {
    language: string;
    proficiency: string;
}

interface CoachProfile {
    id: number;
    bio?: string;
    profile_picture?: string;
    coach_title?: string;
    hourly_rate?: number;

    // V1 specific
    goal?: string;
    skills?: string;
    country?: string;
    phone_number?: string;
    date_of_birth?: string;
    onboarding_step?: number;
    is_approved: boolean;

    experience?: Experience[];
    education?: Education[];
    portfolio_items?: PortfolioItem[];
    languages?: Language[];
}

interface StudentProfile {
    id: number;
    bio?: string;
    profile_picture?: string;

    // V1 specific
    age?: number;
    country?: string;
    languages?: Language[];
}

interface User {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    is_student: boolean;
    is_coach: boolean;
    current_role: "student" | "coach";
    onboarding_completed: boolean;
    profile_completion_percentage: number;
    student_profile?: StudentProfile;
    coach_profile?: CoachProfile;
}

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (token: string) => Promise<void>;
    logout: () => void;
    refreshUser: () => Promise<void>;
    switchRole: (role: "student" | "coach") => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    const fetchUser = async () => {
        try {
            const res = await api.get("/auth/me");
            setUser(res.data);
            localStorage.setItem("skileez_user", JSON.stringify(res.data));
        } catch (error) {
            console.error("Failed to fetch user", error);
            logout();
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const token = localStorage.getItem("skileez_token");
        if (token) {
            fetchUser();
        } else {
            setLoading(false);
        }
    }, []);

    const login = async (token: string) => {
        localStorage.setItem("skileez_token", token);

        // Fetch User and decide where to go
        try {
            const res = await api.get("/auth/me");
            const userData = res.data;
            setUser(userData);
            localStorage.setItem("skileez_user", JSON.stringify(userData));

            // V1 Parity Flow: Register -> Login -> Onboarding -> (Coach Only) Admin Approval -> Dashboard
            if (!userData.onboarding_completed) {
                router.push("/onboarding");
            } else if (userData.current_role === "coach" && !userData.coach_profile?.is_approved) {
                router.push("/onboarding/pending");
            } else {
                router.push("/dashboard");
            }
        } catch (error) {
            console.error("Failed to fetch user after login", error);
            logout();
        }
    };

    const logout = () => {
        localStorage.removeItem("skileez_token");
        localStorage.removeItem("skileez_user");
        setUser(null);
        router.push("/auth/login");
    };

    const switchRole = async (role: "student" | "coach") => {
        try {
            const res = await api.post(`/auth/switch-role?target_role=${role}`);
            setUser(res.data);
            localStorage.setItem("skileez_user", JSON.stringify(res.data));
            router.refresh();
        } catch (error) {
            console.error("Failed to switch role", error);
        }
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout, refreshUser: fetchUser, switchRole }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};
