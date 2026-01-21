"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import {
    ChevronLeft,
    Save,
    Plus,
    Trash2,
    Briefcase,
    Book,
    Globe,
    User as UserIcon,
    Camera,
    CheckCircle2,
    DollarSign,
    Target
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function ProfileEditPage() {
    const { user, refreshUser } = useAuth();
    const router = useRouter();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [success, setSuccess] = useState(false);

    // Form State
    const [formData, setFormData] = useState<any>({
        first_name: "",
        last_name: "",
        bio: "",
        country: "",
        coach_title: "",
        hourly_rate: 0,
        skills: "",
        experience: [],
        education: []
    });

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const res = await api.get("/profiles/me");
                const data = res.data;
                const isCoach = data.current_role === "coach";
                const profile = isCoach ? data.coach_profile : data.student_profile;

                setFormData({
                    first_name: data.first_name || "",
                    last_name: data.last_name || "",
                    bio: profile?.bio || "",
                    country: profile?.country || "",
                    coach_title: data.coach_profile?.coach_title || "",
                    hourly_rate: data.coach_profile?.hourly_rate || 0,
                    skills: data.coach_profile?.skills || "",
                    experience: data.coach_profile?.experience || [],
                    education: data.coach_profile?.education || []
                });
            } catch (err) {
                console.error("Failed to fetch profile", err);
            } finally {
                setLoading(false);
            }
        };

        fetchProfile();
    }, []);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData((prev: any) => ({ ...prev, [name]: value }));
    };

    const handleListChange = (type: 'experience' | 'education', index: number, field: string, value: any) => {
        setFormData((prev: any) => {
            const newList = [...prev[type]];
            newList[index] = { ...newList[index], [field]: value };
            return { ...prev, [type]: newList };
        });
    };

    const addItem = (type: 'experience' | 'education') => {
        const newItem = type === 'experience'
            ? { title: "", company: "", start_date: "", is_current: false, description: "" }
            : { degree: "", institution: "", start_date: "", end_date: "" };

        setFormData((prev: any) => ({ ...prev, [type]: [...prev[type], newItem] }));
    };

    const removeItem = (type: 'experience' | 'education', index: number) => {
        setFormData((prev: any) => ({ ...prev, [type]: prev[type].filter((_: any, i: number) => i !== index) }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);
        try {
            await api.patch("/profiles/me", formData);
            await refreshUser();
            setSuccess(true);
            setTimeout(() => setSuccess(false), 5000);
            router.push("/profile");
        } catch (err) {
            console.error("Failed to update profile", err);
            alert("Failed to update profile. Please check your inputs.");
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-[#FDFDFF] flex items-center justify-center">
                <div className="w-12 h-12 border-4 border-primary-100 border-t-primary-600 rounded-full animate-spin"></div>
            </div>
        );
    }

    const isCoach = user?.current_role === "coach";

    return (
        <div className="min-h-screen bg-[#FDFDFF] font-inter">
            <div className="max-w-4xl mx-auto p-8 md:p-12">
                <Link href="/profile" className="inline-flex items-center gap-2 text-gray-400 hover:text-primary-600 font-bold mb-12 transition-colors">
                    <ChevronLeft size={20} /> Back to Profile
                </Link>

                <div className="flex justify-between items-end mb-12">
                    <div>
                        <h1 className="text-5xl font-black text-gray-900 tracking-tight">Edit Profile</h1>
                        <p className="text-gray-400 mt-2 text-lg font-medium">Update your digital identity on Skileez.</p>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-12">
                    {/* Basic Info */}
                    <section className="bg-white p-10 rounded-[2.5rem] border border-gray-100 shadow-sm space-y-8">
                        <div className="flex items-center gap-3 mb-2">
                            <UserIcon size={20} className="text-primary-500" />
                            <h2 className="text-lg font-black text-gray-900 uppercase tracking-widest">Basic Information</h2>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="text-xs font-black text-gray-400 uppercase tracking-widest ml-1">First Name</label>
                                <input
                                    type="text"
                                    name="first_name"
                                    value={formData.first_name}
                                    onChange={handleChange}
                                    className="w-full px-6 py-4 bg-gray-50 border border-transparent rounded-2xl focus:bg-white focus:border-primary-500 outline-none transition-all font-bold text-gray-900"
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-black text-gray-400 uppercase tracking-widest ml-1">Last Name</label>
                                <input
                                    type="text"
                                    name="last_name"
                                    value={formData.last_name}
                                    onChange={handleChange}
                                    className="w-full px-6 py-4 bg-gray-50 border border-transparent rounded-2xl focus:bg-white focus:border-primary-500 outline-none transition-all font-bold text-gray-900"
                                    required
                                />
                            </div>
                        </div>

                        {isCoach && (
                            <div className="space-y-2">
                                <label className="text-xs font-black text-gray-400 uppercase tracking-widest ml-1">Professional Title</label>
                                <input
                                    type="text"
                                    name="coach_title"
                                    value={formData.coach_title}
                                    onChange={handleChange}
                                    placeholder="e.g. Senior Full Stack Engineer & Mentor"
                                    className="w-full px-6 py-4 bg-gray-50 border border-transparent rounded-2xl focus:bg-white focus:border-primary-500 outline-none transition-all font-bold text-gray-900"
                                />
                            </div>
                        )}

                        <div className="space-y-2">
                            <label className="text-xs font-black text-gray-400 uppercase tracking-widest ml-1">Bio</label>
                            <textarea
                                name="bio"
                                value={formData.bio}
                                onChange={handleChange}
                                rows={5}
                                placeholder="Tell us about your background, goals, and passions..."
                                className="w-full px-6 py-4 bg-gray-50 border border-transparent rounded-2xl focus:bg-white focus:border-primary-500 outline-none transition-all font-bold text-gray-900 resize-none"
                            />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="text-xs font-black text-gray-400 uppercase tracking-widest ml-1">Location / Country</label>
                                <input
                                    type="text"
                                    name="country"
                                    value={formData.country}
                                    onChange={handleChange}
                                    placeholder="e.g. United States"
                                    className="w-full px-6 py-4 bg-gray-50 border border-transparent rounded-2xl focus:bg-white focus:border-primary-500 outline-none transition-all font-bold text-gray-900"
                                />
                            </div>
                            {isCoach && (
                                <div className="space-y-2">
                                    <label className="text-xs font-black text-gray-400 uppercase tracking-widest ml-1">Hourly Rate ($)</label>
                                    <input
                                        type="number"
                                        name="hourly_rate"
                                        value={formData.hourly_rate}
                                        onChange={handleChange}
                                        className="w-full px-6 py-4 bg-gray-50 border border-transparent rounded-2xl focus:bg-white focus:border-primary-500 outline-none transition-all font-bold text-gray-900"
                                    />
                                </div>
                            )}
                        </div>
                    </section>

                    {/* Skills Section */}
                    {isCoach && (
                        <section className="bg-white p-10 rounded-[2.5rem] border border-gray-100 shadow-sm space-y-8">
                            <div className="flex items-center gap-3 mb-2">
                                <Target size={20} className="text-green-500" />
                                <h2 className="text-lg font-black text-gray-900 uppercase tracking-widest">Skills & Expertise</h2>
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-black text-gray-400 uppercase tracking-widest ml-1">Skills (comma separated)</label>
                                <input
                                    type="text"
                                    name="skills"
                                    value={formData.skills}
                                    onChange={handleChange}
                                    placeholder="Python, React, Machine Learning..."
                                    className="w-full px-6 py-4 bg-gray-50 border border-transparent rounded-2xl focus:bg-white focus:border-primary-500 outline-none transition-all font-bold text-gray-900"
                                />
                                <p className="text-[10px] text-gray-400 font-bold px-2 italic">These help students find you in the marketplace.</p>
                            </div>
                        </section>
                    )}

                    {/* Experience Section */}
                    {isCoach && (
                        <section className="bg-white p-10 rounded-[2.5rem] border border-gray-100 shadow-sm space-y-8">
                            <div className="flex justify-between items-center mb-2">
                                <div className="flex items-center gap-3">
                                    <Briefcase size={20} className="text-blue-500" />
                                    <h2 className="text-lg font-black text-gray-900 uppercase tracking-widest">Experience</h2>
                                </div>
                                <button
                                    type="button"
                                    onClick={() => addItem('experience')}
                                    className="p-2 bg-primary-50 text-primary-600 rounded-xl hover:bg-primary-100 transition-all"
                                >
                                    <Plus size={20} />
                                </button>
                            </div>

                            <div className="space-y-6">
                                {formData.experience.map((exp: any, index: number) => (
                                    <div key={index} className="p-8 bg-gray-50 rounded-[2rem] relative group border border-transparent hover:border-gray-200 transition-all">
                                        <button
                                            type="button"
                                            onClick={() => removeItem('experience', index)}
                                            className="absolute top-4 right-4 p-2 text-gray-300 hover:text-red-500 transition-colors"
                                        >
                                            <Trash2 size={18} />
                                        </button>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                                            <div className="space-y-2">
                                                <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Job Title</label>
                                                <input
                                                    type="text"
                                                    value={exp.title}
                                                    onChange={(e) => handleListChange('experience', index, 'title', e.target.value)}
                                                    className="w-full px-5 py-3 bg-white border border-gray-100 rounded-xl focus:border-primary-500 outline-none font-bold text-gray-900"
                                                    required
                                                />
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Company</label>
                                                <input
                                                    type="text"
                                                    value={exp.company}
                                                    onChange={(e) => handleListChange('experience', index, 'company', e.target.value)}
                                                    className="w-full px-5 py-3 bg-white border border-gray-100 rounded-xl focus:border-primary-500 outline-none font-bold text-gray-900"
                                                    required
                                                />
                                            </div>
                                        </div>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                                            <div className="space-y-2">
                                                <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Start Date</label>
                                                <input
                                                    type="date"
                                                    value={exp.start_date}
                                                    onChange={(e) => handleListChange('experience', index, 'start_date', e.target.value)}
                                                    className="w-full px-5 py-3 bg-white border border-gray-100 rounded-xl focus:border-primary-500 outline-none font-bold text-gray-900"
                                                    required
                                                />
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">End Date</label>
                                                <input
                                                    type="date"
                                                    value={exp.end_date}
                                                    onChange={(e) => handleListChange('experience', index, 'end_date', e.target.value)}
                                                    disabled={exp.is_current}
                                                    className="w-full px-5 py-3 bg-white border border-gray-100 rounded-xl focus:border-primary-500 outline-none font-bold text-gray-900 disabled:opacity-50"
                                                />
                                                <div className="flex items-center gap-2 mt-2 ml-1">
                                                    <input
                                                        type="checkbox"
                                                        checked={exp.is_current}
                                                        onChange={(e) => handleListChange('experience', index, 'is_current', e.target.checked)}
                                                        className="w-4 h-4 text-primary-600 rounded bg-white border-gray-300 focus:ring-primary-500"
                                                    />
                                                    <span className="text-[10px] font-black text-gray-400 uppercase">I currenty work here</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </section>
                    )}

                    {/* Education Section */}
                    {isCoach && (
                        <section className="bg-white p-10 rounded-[2.5rem] border border-gray-100 shadow-sm space-y-8">
                            <div className="flex justify-between items-center mb-2">
                                <div className="flex items-center gap-3">
                                    <Book size={20} className="text-purple-500" />
                                    <h2 className="text-lg font-black text-gray-900 uppercase tracking-widest">Education</h2>
                                </div>
                                <button
                                    type="button"
                                    onClick={() => addItem('education')}
                                    className="p-2 bg-primary-50 text-primary-600 rounded-xl hover:bg-primary-100 transition-all"
                                >
                                    <Plus size={20} />
                                </button>
                            </div>

                            <div className="space-y-6">
                                {formData.education.map((edu: any, index: number) => (
                                    <div key={index} className="p-8 bg-gray-50 rounded-[2rem] relative border border-transparent hover:border-gray-200 transition-all">
                                        <button
                                            type="button"
                                            onClick={() => removeItem('education', index)}
                                            className="absolute top-4 right-4 p-2 text-gray-300 hover:text-red-500 transition-colors"
                                        >
                                            <Trash2 size={18} />
                                        </button>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            <div className="space-y-2">
                                                <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Degree / Diploma</label>
                                                <input
                                                    type="text"
                                                    value={edu.degree}
                                                    onChange={(e) => handleListChange('education', index, 'degree', e.target.value)}
                                                    className="w-full px-5 py-3 bg-white border border-gray-100 rounded-xl focus:border-primary-500 outline-none font-bold text-gray-900"
                                                    required
                                                />
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Institution</label>
                                                <input
                                                    type="text"
                                                    value={edu.institution}
                                                    onChange={(e) => handleListChange('education', index, 'institution', e.target.value)}
                                                    className="w-full px-5 py-3 bg-white border border-gray-100 rounded-xl focus:border-primary-500 outline-none font-bold text-gray-900"
                                                    required
                                                />
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </section>
                    )}

                    {/* Footer / Save */}
                    <div className="flex items-center justify-between pt-8">
                        <p className="text-sm text-gray-400 font-medium italic flex items-center gap-2">
                            <CheckCircle2 size={16} className="text-green-500" />
                            Your changes are private until you save.
                        </p>
                        <div className="flex gap-4">
                            <Link href="/profile" className="px-8 py-4 text-gray-500 font-black rounded-2xl hover:bg-gray-100 transition-all">
                                Cancel
                            </Link>
                            <button
                                type="submit"
                                disabled={saving}
                                className="px-10 py-4 bg-gray-900 text-white font-black rounded-2xl shadow-xl hover:shadow-2xl transition-all transform hover:-translate-y-1 active:scale-95 flex items-center gap-2 disabled:opacity-50"
                            >
                                {saving ? "Saving..." : "Save Changes"} <Save size={20} />
                            </button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    );
}
