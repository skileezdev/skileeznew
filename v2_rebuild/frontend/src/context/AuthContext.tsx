"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface User {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    is_student: bool;
    is_coach: bool;
}

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (token: string) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const token = localStorage.getItem("skileez_token");
        if (token) {
            // In a real app, you'd verify the token or fetch the user profile here
            // For now, we'll just parse the token if it's there or wait for a real login
            const storedUser = localStorage.getItem("skileez_user");
            if (storedUser) {
                setUser(JSON.parse(storedUser));
            }
        }
        setLoading(false);
    }, []);

    const login = (token: string) => {
        localStorage.setItem("skileez_token", token);
        // Ideally fetch user after login, but for this demo phase we'll redirect
        router.push("/dashboard");
    };

    const logout = () => {
        localStorage.removeItem("skileez_token");
        localStorage.removeItem("skileez_user");
        setUser(null);
        router.push("/auth/login");
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
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
