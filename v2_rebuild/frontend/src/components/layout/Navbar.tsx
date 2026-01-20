"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import {
    Bell,
    ChevronDown,
    Briefcase,
    BookOpen,
    RefreshCw,
    LogOut,
    Settings,
    User as UserIcon,
    Search,
    PlusCircle,
    MessageSquare,
    FileText,
    Calendar,
    LayoutDashboard,
    Menu,
    X
} from "lucide-react";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { NotificationCenter } from "./NotificationCenter";

export function Navbar() {
    const { user, logout, switchRole } = useAuth();
    const pathname = usePathname();
    const [isScrolled, setIsScrolled] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [isNotificationOpen, setIsNotificationOpen] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 10);
        };
        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    const navLinks = {
        coach: [
            { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
            { name: "Find Work", href: "/find-work", icon: Search },
            { name: "Contracts", href: "/contracts", icon: FileText },
            { name: "Sessions", href: "/sessions", icon: Calendar },
            { name: "Messages", href: "/messages", icon: MessageSquare },
        ],
        student: [
            { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
            { name: "Post Request", href: "/marketplace/create", icon: PlusCircle },
            { name: "Browse Coaches", href: "/browse-coaches", icon: Search },
            { name: "Contracts", href: "/contracts", icon: FileText },
            { name: "Sessions", href: "/sessions", icon: Calendar },
            { name: "Messages", href: "/messages", icon: MessageSquare },
        ]
    };

    const currentLinks = user ? navLinks[user.current_role] : [];

    return (
        <nav
            className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled ? "py-3" : "py-5"
                }`}
        >
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div
                    className={`relative flex items-center justify-between px-6 py-3 rounded-2xl transition-all duration-500 ${isScrolled
                        ? "glass-panel shadow-2xl"
                        : "bg-transparent border border-transparent"
                        }`}
                >
                    {/* Logo */}
                    <Link href={user ? "/dashboard" : "/"} className="flex items-center space-x-3 group">
                        <div className="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-primary/30 transition-shadow">
                            <span className="text-white font-bold text-xl">S</span>
                        </div>
                        <span className="text-2xl font-black tracking-tight text-foreground">Skileez</span>
                    </Link>

                    {/* Desktop Navigation */}
                    <div className="hidden lg:flex items-center space-x-1">
                        {user ? (
                            <>
                                <div className="flex items-center space-x-1 mr-4">
                                    {currentLinks.map((link) => (
                                        <Link
                                            key={link.name}
                                            href={link.href}
                                            className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-200 ${pathname === link.href
                                                ? "bg-primary/10 text-primary"
                                                : "text-foreground/70 hover:text-primary hover:bg-primary/5"
                                                }`}
                                        >
                                            {link.name}
                                        </Link>
                                    ))}
                                </div>

                                {/* Role Switcher */}
                                {user.is_student && user.is_coach && (
                                    <button
                                        onClick={() => switchRole(user.current_role === "coach" ? "student" : "coach")}
                                        className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-primary/5 to-secondary/5 border border-primary/10 rounded-xl hover:border-primary/30 hover:shadow-md transition-all group mr-4"
                                    >
                                        <RefreshCw className="w-4 h-4 text-primary group-hover:rotate-180 transition-transform duration-500" />
                                        <span className="text-sm font-bold text-primary capitalize">
                                            {user.current_role === "coach" ? "Student Mode" : "Coach Mode"}
                                        </span>
                                    </button>
                                )}

                                {/* Notifications & User */}
                                <div className="flex items-center space-x-4 ml-4 pl-4 border-l border-gray-200">
                                    <div className="relative">
                                        <button
                                            onClick={() => setIsNotificationOpen(!isNotificationOpen)}
                                            className="relative p-2 text-foreground/60 hover:text-primary transition-colors"
                                        >
                                            <Bell className="w-5 h-5" />
                                            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-error rounded-full animate-pulse"></span>
                                        </button>
                                        <NotificationCenter isOpen={isNotificationOpen} onClose={() => setIsNotificationOpen(false)} />
                                    </div>

                                    <div className="relative">
                                        <button
                                            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                                            className="flex items-center space-x-3 p-1.5 pr-3 rounded-xl hover:bg-muted transition-all"
                                        >
                                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white font-bold text-xs">
                                                {user.first_name[0]}{user.last_name[0]}
                                            </div>
                                            <ChevronDown className={`w-4 h-4 text-foreground/40 transition-transform duration-300 ${isDropdownOpen ? "rotate-180" : ""}`} />
                                        </button>

                                        <AnimatePresence>
                                            {isDropdownOpen && (
                                                <motion.div
                                                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                                                    animate={{ opacity: 1, y: 0, scale: 1 }}
                                                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                                                    className="absolute right-0 mt-3 w-56 glass-panel rounded-2xl p-2 shadow-2xl border-white/50"
                                                >
                                                    <div className="px-4 py-3 border-b border-gray-200/50 mb-2">
                                                        <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Account</p>
                                                        <p className="text-sm font-semibold truncate">{user.first_name} {user.last_name}</p>
                                                    </div>
                                                    <Link href="/profile/edit" className="flex items-center space-x-2 px-3 py-2 rounded-xl text-sm font-medium hover:bg-muted transition-colors">
                                                        <UserIcon className="w-4 h-4" />
                                                        <span>My Profile</span>
                                                    </Link>
                                                    <Link href="/settings" className="flex items-center space-x-2 px-3 py-2 rounded-xl text-sm font-medium hover:bg-muted transition-colors">
                                                        <Settings className="w-4 h-4" />
                                                        <span>Settings</span>
                                                    </Link>
                                                    <div className="h-px bg-border/50 my-2"></div>
                                                    <button
                                                        onClick={logout}
                                                        className="w-full flex items-center space-x-2 px-3 py-2 rounded-xl text-sm font-medium text-error hover:bg-error/10 transition-colors"
                                                    >
                                                        <LogOut className="w-4 h-4" />
                                                        <span>Sign Out</span>
                                                    </button>
                                                </motion.div>
                                            )}
                                        </AnimatePresence>
                                    </div>
                                </div>
                            </>
                        ) : (
                            <div className="flex items-center space-x-4">
                                <Link href="/auth/login" className="text-sm font-bold text-foreground/70 hover:text-primary transition-colors">
                                    Login
                                </Link>
                                <Link href="/auth/signup" className="btn-primary">
                                    Get Started
                                </Link>
                            </div>
                        )}
                    </div>

                    {/* Mobile Menu Button */}
                    <div className="lg:hidden flex items-center">
                        <button
                            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                            className="p-2 text-foreground/60 hover:text-primary transition-colors"
                        >
                            {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            <AnimatePresence>
                {isMobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="lg:hidden glass-panel mt-2 mx-4 rounded-2xl overflow-hidden shadow-2xl border-white/50"
                    >
                        <div className="px-4 py-6 space-y-4">
                            {user ? (
                                <>
                                    <div className="flex items-center space-x-3 pb-4 mb-4 border-b border-gray-200">
                                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white font-bold text-lg">
                                            {user.first_name[0]}{user.last_name[0]}
                                        </div>
                                        <div>
                                            <p className="font-bold">{user.first_name} {user.last_name}</p>
                                            <p className="text-sm text-primary font-semibold capitalize">{user.current_role} Mode</p>
                                        </div>
                                    </div>
                                    <div className="space-y-1">
                                        {currentLinks.map((link) => (
                                            <Link
                                                key={link.name}
                                                href={link.href}
                                                onClick={() => setIsMobileMenuOpen(false)}
                                                className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-muted transition-all"
                                            >
                                                <link.icon className="w-5 h-5 text-foreground/40" />
                                                <span className="font-semibold">{link.name}</span>
                                            </Link>
                                        ))}
                                    </div>

                                    {user.is_student && user.is_coach && (
                                        <button
                                            onClick={() => {
                                                switchRole(user.current_role === "coach" ? "student" : "coach");
                                                setIsMobileMenuOpen(false);
                                            }}
                                            className="w-full flex items-center justify-center space-x-2 p-4 mt-4 bg-primary text-white rounded-xl font-bold shadow-lg"
                                        >
                                            <RefreshCw className="w-5 h-5" />
                                            <span>Switch to {user.current_role === "coach" ? "Student" : "Coach"} Mode</span>
                                        </button>
                                    )}

                                    <button
                                        onClick={logout}
                                        className="w-full flex items-center justify-center space-x-2 p-4 text-error font-bold"
                                    >
                                        <LogOut className="w-5 h-5" />
                                        <span>Sign Out</span>
                                    </button>
                                </>
                            ) : (
                                <div className="flex flex-col space-y-4">
                                    <Link href="/auth/login" className="w-full p-4 text-center font-bold text-foreground/70" onClick={() => setIsMobileMenuOpen(false)}>
                                        Login
                                    </Link>
                                    <Link href="/auth/signup" className="btn-primary w-full text-center" onClick={() => setIsMobileMenuOpen(false)}>
                                        Get Started
                                    </Link>
                                </div>
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </nav>
    );
}
