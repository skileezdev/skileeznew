"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import {
    User,
    Camera,
    Edit3,
    Plus,
    Briefcase,
    GraduationCap,
    Layout,
    Save,
    Trash2,
    CheckCircle2
} from "lucide-react";

export default function ProfilePage() {
    const [profile, setProfile] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [editMode, setEditMode] = useState(false);
    const [formData, setFormData] = useState({ first_name: "", last_name: "", bio: "", coach_title: "", hourly_rate: 0 });

    const fetchProfile = async () => {
        try {
            const res = await api.get("/profiles/me");
            setProfile(res.data);
            setFormData({
                first_name: res.data.first_name,
                last_name: res.data.last_name,
                bio: res.data.current_role === 'student' ? res.data.student_profile?.bio : res.data.coach_profile?.bio,
                coach_title: res.data.coach_profile?.coach_title || "",
                hourly_rate: res.data.coach_profile?.hourly_rate || 0
            });
        } catch (err) {
            console.error("Failed to fetch profile", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchProfile();
    }, []);

    const handleSave = async () => {
        setSaving(true);
        try {
            await api.post("/profiles/update", formData);
            setEditMode(false);
            await fetchProfile();
        } catch (err) {
            console.error("Save failed", err);
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <div className="min-h-screen flex items-center justify-center bg-[#FDFDFF]"><div className="w-12 h-12 border-4 border-primary-100 border-t-primary-600 rounded-full animate-spin"></div></div>;

    return (
        <div className="min-h-screen bg-[#FDFDFF] p-8 md:p-12 font-inter">
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-end mb-12">
                    <div>
                        <h1 className="text-4xl font-black text-gray-900 tracking-tighter italic underline decoration-primary-500 decoration-8 underline-offset-8">Account Settings.</h1>
                        <p className="text-gray-400 mt-2 font-bold uppercase text-[10px] tracking-widest">Manage your global Skileez identity</p>
                    </div>
                    {!editMode ? (
                        <button onClick={() => setEditMode(true)} className="py-3 px-8 bg-gray-900 text-white font-black text-xs rounded-2xl shadow-lg hover:shadow-xl transition-all flex items-center gap-2">
                            <Edit3 size={16} /> Edit Profile
                        </button>
                    ) : (
                        <div className="flex gap-2">
                            <button onClick={() => setEditMode(false)} className="py-3 px-6 bg-white border border-gray-100 text-gray-400 font-black text-xs rounded-2xl shadow-sm hover:text-gray-900 transition-all">Cancel</button>
                            <button onClick={handleSave} disabled={saving} className="py-3 px-8 bg-primary-600 text-white font-black text-xs rounded-2xl shadow-lg hover:shadow-xl transition-all flex items-center gap-2">
                                <Save size={16} /> {saving ? "Saving..." : "Save Changes"}
                            </button>
                        </div>
                    )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-12 gap-12">
                    {/* Sidebar: Profile Info */}
                    <div className="md:col-span-4 space-y-8">
                        <div className="bg-white p-8 rounded-[3rem] shadow-xl shadow-gray-100/50 border border-gray-100 text-center relative group">
                            <div className="w-32 h-32 bg-gray-50 rounded-full mx-auto mb-6 flex items-center justify-center border-4 border-white shadow-lg overflow-hidden relative">
                                <User size={48} className="text-gray-300" />
                                <div className="absolute inset-0 bg-primary-600/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center cursor-pointer">
                                    <Camera size={24} className="text-white" />
                                </div>
                            </div>
                            <h2 className="text-2xl font-black text-gray-900">{profile.first_name} {profile.last_name}</h2>
                            <p className="text-primary-600 font-black text-[10px] uppercase tracking-widest mt-1 italic">{profile.current_role}</p>

                            <div className="mt-8 pt-8 border-t border-gray-50 flex justify-between px-2">
                                <div><p className="text-xl font-black text-gray-900">100%</p><p className="text-[8px] font-black text-gray-300 uppercase tracking-widest">Status</p></div>
                                <div><p className="text-xl font-black text-gray-900">4.9</p><p className="text-[8px] font-black text-gray-300 uppercase tracking-widest">Rating</p></div>
                                <div><p className="text-xl font-black text-gray-900">22</p><p className="text-[8px] font-black text-gray-300 uppercase tracking-widest">Sessions</p></div>
                            </div>
                        </div>
                    </div>

                    {/* Main Content: Edit Fields */}
                    <div className="md:col-span-8 space-y-8">
                        {/* Identity Section */}
                        <div className="bg-white p-10 rounded-[3.5rem] shadow-sm border border-gray-50">
                            <h3 className="text-xl font-black text-gray-900 mb-8 flex items-center gap-2">
                                <Layout size={20} className="text-primary-600" /> Identity Details
                            </h3>
                            <div className="grid grid-cols-2 gap-6 mb-6">
                                <div>
                                    <label className="block text-[10px] font-black text-gray-300 uppercase tracking-widest mb-2 px-1">First Name</label>
                                    <input
                                        type="text"
                                        disabled={!editMode}
                                        className="w-full px-6 py-4 bg-gray-50 border border-transparent focus:border-primary-500 focus:bg-white rounded-2xl outline-none transition-all font-bold text-gray-900 disabled:opacity-50"
                                        value={formData.first_name}
                                        onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-[10px] font-black text-gray-300 uppercase tracking-widest mb-2 px-1">Last Name</label>
                                    <input
                                        type="text"
                                        disabled={!editMode}
                                        className="w-full px-6 py-4 bg-gray-50 border border-transparent focus:border-primary-500 focus:bg-white rounded-2xl outline-none transition-all font-bold text-gray-900 disabled:opacity-50"
                                        value={formData.last_name}
                                        onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                                    />
                                </div>
                            </div>

                            {profile.current_role === 'coach' && (
                                <div className="mb-6">
                                    <label className="block text-[10px] font-black text-gray-300 uppercase tracking-widest mb-2 px-1">Professional Title</label>
                                    <input
                                        type="text"
                                        disabled={!editMode}
                                        className="w-full px-6 py-4 bg-gray-50 border border-transparent focus:border-primary-500 focus:bg-white rounded-2xl outline-none transition-all font-bold text-gray-900 disabled:opacity-50"
                                        placeholder="e.g. Senior Machine Learning Architect"
                                        value={formData.coach_title}
                                        onChange={(e) => setFormData({ ...formData, coach_title: e.target.value })}
                                    />
                                </div>
                            )}

                            <div>
                                <label className="block text-[10px] font-black text-gray-300 uppercase tracking-widest mb-2 px-1">Biography</label>
                                <textarea
                                    rows={5}
                                    disabled={!editMode}
                                    placeholder="Tell the community about your journey and expertise..."
                                    className="w-full px-6 py-4 bg-gray-50 border border-transparent focus:border-primary-500 focus:bg-white rounded-[2rem] outline-none transition-all font-bold text-gray-900 resize-none disabled:opacity-50"
                                    value={formData.bio}
                                    onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                                />
                            </div>
                        </div>

                        {/* Experience/Portfolio Empty States (Mirroring V1 placeholder UX) */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div className="bg-white p-8 rounded-[3rem] border border-gray-50">
                                <div className="flex justify-between items-center mb-6">
                                    <h4 className="text-sm font-black text-gray-900 flex items-center gap-2 uppercase tracking-widest"><Briefcase size={16} className="text-primary-600" /> Experience</h4>
                                    <button className="p-2 bg-gray-50 text-gray-400 hover:text-primary-600 rounded-xl transition-all"><Plus size={16} /></button>
                                </div>
                                <div className="py-8 text-center border-2 border-dashed border-gray-50 rounded-[2rem]">
                                    <p className="text-[10px] font-black text-gray-300 uppercase tracking-widest">No history added yet</p>
                                </div>
                            </div>
                            <div className="bg-white p-8 rounded-[3rem] border border-gray-50">
                                <div className="flex justify-between items-center mb-6">
                                    <h4 className="text-sm font-black text-gray-900 flex items-center gap-2 uppercase tracking-widest"><GraduationCap size={16} className="text-primary-600" /> Education</h4>
                                    <button className="p-2 bg-gray-50 text-gray-400 hover:text-primary-600 rounded-xl transition-all"><Plus size={16} /></button>
                                </div>
                                <div className="py-8 text-center border-2 border-dashed border-gray-50 rounded-[2rem]">
                                    <p className="text-[10px] font-black text-gray-300 uppercase tracking-widest">Academic records empty</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
