"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { Edit2, Save, MapPin, DollarSign, Award, Briefcase, Book, Folder, Star } from "lucide-react";
import { motion } from "framer-motion";

export default function ProfilePage() {
    const { user } = useAuth();
    const [profile, setProfile] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [editMode, setEditMode] = useState<string | null>(null);
    const [editValue, setEditValue] = useState("");
    const [activeTab, setActiveTab] = useState("overview");

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const res = await api.get("/profiles/me");
                setProfile(res.data);
            } catch (err) {
                console.error("Failed to fetch profile", err);
            } finally {
                setLoading(false);
            }
        };

        fetchProfile();
    }, []);

    const handleEdit = (field: string, currentValue: string) => {
        setEditMode(field);
        setEditValue(currentValue || "");
    };

    const handleSave = async (field: string) => {
        try {
            await api.patch("/profiles/me", { [field]: editValue });
            setProfile({ ...profile, [field]: editValue });
            setEditMode(null);
        } catch (err) {
            console.error("Failed to save", err);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-muted/30 pt-32 flex items-center justify-center">
                <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    const isCoach = user?.current_role === "coach";

    return (
        <div className="min-h-screen bg-muted/30 pt-32 pb-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Hero Header */}
                <div className="bg-white rounded-[2rem] shadow-lg border border-gray-100 p-8 mb-8">
                    <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
                        {/* Avatar */}
                        <div className="relative group">
                            {profile?.profile_picture ? (
                                <img src={profile.profile_picture} alt={user?.first_name} className="w-24 h-24 rounded-2xl object-cover shadow-md" />
                            ) : (
                                <div className="w-24 h-24 bg-gradient-to-br from-primary to-purple-600 rounded-2xl flex items-center justify-center text-white text-3xl font-black shadow-md">
                                    {user?.first_name?.[0]}
                                </div>
                            )}
                            <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 border-4 border-white rounded-full"></div>
                        </div>

                        {/* Name & Title */}
                        <div className="flex-1">
                            <h1 className="text-3xl font-black text-gray-900 mb-2">
                                {user?.first_name} {user?.last_name}
                            </h1>
                            {isCoach && (
                                <div className="flex items-center gap-2">
                                    {editMode === "coach_title" ? (
                                        <div className="flex items-center gap-2">
                                            <input
                                                type="text"
                                                value={editValue}
                                                onChange={(e) => setEditValue(e.target.value)}
                                                className="px-3 py-1 border border-primary rounded-lg text-lg font-semibold text-primary"
                                                autoFocus
                                            />
                                            <button onClick={() => handleSave("coach_title")} className="p-2 bg-primary text-white rounded-lg hover:bg-primary-700">
                                                <Save size={16} />
                                            </button>
                                        </div>
                                    ) : (
                                        <div className="flex items-center gap-2">
                                            <p className="text-lg font-semibold text-primary">{profile?.coach_title || "Add your title"}</p>
                                            <button onClick={() => handleEdit("coach_title", profile?.coach_title)} className="p-1.5 text-gray-400 hover:text-primary">
                                                <Edit2 size={16} />
                                            </button>
                                        </div>
                                    )}
                                </div>
                            )}
                            {profile?.country && (
                                <p className="text-sm text-gray-500 flex items-center mt-1">
                                    <MapPin size={14} className="mr-1" />
                                    {profile.country}
                                </p>
                            )}
                        </div>

                        {/* Stats (Coach Only) */}
                        {isCoach && (
                            <div className="flex gap-6">
                                <div className="text-center">
                                    <div className="text-2xl font-black bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
                                        ${profile?.hourly_rate || 0}
                                    </div>
                                    <div className="text-xs text-gray-500 font-medium">Per Hour</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-2xl font-black text-gray-900 flex items-center gap-1">
                                        {profile?.rating || 5.0}
                                        <Star size={16} className="text-yellow-400 fill-yellow-400" />
                                    </div>
                                    <div className="text-xs text-gray-500 font-medium">Rating</div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                    {/* Sidebar */}
                    <div className="lg:col-span-1 space-y-6">
                        {/* Skills Card */}
                        {isCoach && (
                            <div className="bg-white rounded-[1.5rem] shadow-sm border border-gray-100 p-6">
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                                        <Award size={20} className="text-green-500" />
                                        Skills
                                    </h3>
                                    <button onClick={() => handleEdit("skills", profile?.skills)} className="p-1.5 text-gray-400 hover:text-green-600">
                                        <Edit2 size={16} />
                                    </button>
                                </div>
                                {editMode === "skills" ? (
                                    <div>
                                        <textarea
                                            value={editValue}
                                            onChange={(e) => setEditValue(e.target.value)}
                                            className="w-full px-3 py-2 border border-primary rounded-lg text-sm"
                                            rows={4}
                                            placeholder="Python, React, AI..."
                                            autoFocus
                                        />
                                        <button onClick={() => handleSave("skills")} className="mt-2 w-full py-2 bg-primary text-white rounded-lg hover:bg-primary-700 font-semibold">
                                            Save
                                        </button>
                                    </div>
                                ) : (
                                    <div className="flex flex-wrap gap-2">
                                        {profile?.skills?.split(",").map((skill: string, i: number) => (
                                            <span key={i} className="px-3 py-1.5 bg-green-50 text-green-700 rounded-full text-xs font-semibold border border-green-200">
                                                {skill.trim()}
                                            </span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Quick Info */}
                        <div className="bg-gradient-to-br from-primary/5 to-purple-500/5 rounded-[1.5rem] shadow-sm border border-primary/20 p-6">
                            <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Info</h3>
                            <div className="space-y-3 text-sm">
                                <div>
                                    <span className="text-gray-500 font-medium">Member Since</span>
                                    <p className="font-bold text-gray-900">January 2024</p>
                                </div>
                                <div>
                                    <span className="text-gray-500 font-medium">Response Time</span>
                                    <p className="font-bold text-gray-900">Within 1 hour</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Main Content */}
                    <div className="lg:col-span-3">
                        <div className="bg-white rounded-[2rem] shadow-lg border border-gray-100 overflow-hidden">
                            {/* Tabs */}
                            <div className="bg-gradient-to-r from-primary/5 to-purple-500/5 border-b border-gray-100">
                                <nav className="flex space-x-8 px-6">
                                    {["overview", "experience", "portfolio"].map((tab) => (
                                        <button
                                            key={tab}
                                            onClick={() => setActiveTab(tab)}
                                            className={`py-4 px-1 border-b-2 font-semibold capitalize transition-colors ${activeTab === tab ? "border-primary text-primary" : "border-transparent text-gray-600 hover:text-primary"
                                                }`}
                                        >
                                            {tab}
                                        </button>
                                    ))}
                                </nav>
                            </div>

                            {/* Tab Content */}
                            <div className="p-6">
                                {/* Overview Tab */}
                                {activeTab === "overview" && (
                                    <div className="space-y-8">
                                        {/* Bio */}
                                        <div>
                                            <div className="flex items-center justify-between mb-4">
                                                <h3 className="text-xl font-bold text-gray-900">About {user?.first_name}</h3>
                                                <button onClick={() => handleEdit("bio", profile?.bio)} className="p-2 text-gray-400 hover:text-primary">
                                                    <Edit2 size={18} />
                                                </button>
                                            </div>
                                            {editMode === "bio" ? (
                                                <div>
                                                    <textarea
                                                        value={editValue}
                                                        onChange={(e) => setEditValue(e.target.value)}
                                                        className="w-full px-4 py-3 border-2 border-primary rounded-xl text-gray-700"
                                                        rows={6}
                                                        placeholder="Tell us about yourself..."
                                                        autoFocus
                                                    />
                                                    <button onClick={() => handleSave("bio")} className="mt-3 px-6 py-2 bg-primary text-white rounded-xl hover:bg-primary-700 font-semibold">
                                                        Save Bio
                                                    </button>
                                                </div>
                                            ) : (
                                                <p className="text-gray-600 leading-relaxed whitespace-pre-line">
                                                    {profile?.bio || "Click edit to add your bio..."}
                                                </p>
                                            )}
                                        </div>

                                        {/* Stats Grid */}
                                        {isCoach && (
                                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                                <div className="bg-blue-50 rounded-xl p-4 border border-blue-100">
                                                    <div className="text-2xl font-black text-blue-600">24</div>
                                                    <div className="text-xs text-gray-600 font-medium">Sessions</div>
                                                </div>
                                                <div className="bg-green-50 rounded-xl p-4 border border-green-100">
                                                    <div className="text-2xl font-black text-green-600">12</div>
                                                    <div className="text-xs text-gray-600 font-medium">Students</div>
                                                </div>
                                                <div className="bg-purple-50 rounded-xl p-4 border border-purple-100">
                                                    <div className="text-2xl font-black text-purple-600">98%</div>
                                                    <div className="text-xs text-gray-600 font-medium">Success Rate</div>
                                                </div>
                                                <div className="bg-yellow-50 rounded-xl p-4 border border-yellow-100">
                                                    <div className="text-2xl font-black text-yellow-600 flex items-center gap-1">
                                                        5.0
                                                        <Star size={14} className="fill-yellow-600" />
                                                    </div>
                                                    <div className="text-xs text-gray-600 font-medium">Rating</div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {/* Experience Tab */}
                                {activeTab === "experience" && (
                                    <div className="space-y-6">
                                        <div className="flex items-center justify-between">
                                            <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                                                <Briefcase size={20} className="text-blue-500" />
                                                Work Experience
                                            </h3>
                                            <button className="px-4 py-2 bg-primary text-white rounded-xl hover:bg-primary-700 font-semibold text-sm">
                                                Add Experience
                                            </button>
                                        </div>

                                        {/* Sample Experience */}
                                        <div className="bg-blue-50 rounded-xl p-6 border border-blue-100">
                                            <h4 className="text-lg font-bold text-gray-900 mb-1">Senior Developer</h4>
                                            <p className="text-blue-600 font-semibold mb-2">Tech Company Inc.</p>
                                            <p className="text-sm text-gray-500 bg-white px-3 py-1 rounded-full inline-block">Jan 2020 - Present</p>
                                        </div>

                                        {/* Education */}
                                        <div className="mt-8">
                                            <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2 mb-4">
                                                <Book size={20} className="text-purple-500" />
                                                Education
                                            </h3>
                                            <div className="bg-purple-50 rounded-xl p-6 border border-purple-100">
                                                <h4 className="text-lg font-bold text-gray-900 mb-1">Computer Science</h4>
                                                <p className="text-purple-600 font-semibold mb-2">University Name</p>
                                                <p className="text-sm text-gray-500 bg-white px-3 py-1 rounded-full inline-block">2016 - 2020</p>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* Portfolio Tab */}
                                {activeTab === "portfolio" && (
                                    <div>
                                        <div className="flex items-center justify-between mb-6">
                                            <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                                                <Folder size={20} className="text-green-500" />
                                                Portfolio
                                            </h3>
                                            <button className="px-4 py-2 bg-primary text-white rounded-xl hover:bg-primary-700 font-semibold text-sm">
                                                Add Project
                                            </button>
                                        </div>

                                        <div className="grid md:grid-cols-2 gap-6">
                                            {/* Sample Portfolio Item */}
                                            <div className="bg-green-50 rounded-xl overflow-hidden border border-green-100 hover:shadow-lg transition-all">
                                                <div className="w-full h-48 bg-gradient-to-br from-green-200 to-emerald-200 flex items-center justify-center">
                                                    <Folder className="w-16 h-16 text-green-400" />
                                                </div>
                                                <div className="p-6">
                                                    <span className="inline-block px-3 py-1 bg-green-200 text-green-700 text-xs font-bold rounded-full uppercase mb-3">
                                                        Web Development
                                                    </span>
                                                    <h4 className="text-lg font-bold text-gray-900 mb-2">E-Commerce Platform</h4>
                                                    <p className="text-sm text-gray-600 mb-4">Built a full-stack e-commerce solution with React and Node.js</p>
                                                    <div className="flex flex-wrap gap-2">
                                                        <span className="px-2 py-1 bg-white text-gray-700 rounded-full text-xs font-medium border border-gray-200">React</span>
                                                        <span className="px-2 py-1 bg-white text-gray-700 rounded-full text-xs font-medium border border-gray-200">Node.js</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
