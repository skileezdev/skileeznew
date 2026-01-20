"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { JobCard } from "@/components/marketplace/JobCard";
import {
    Briefcase,
    Filter,
    Search,
    ChevronDown,
    Zap,
    LayoutGrid,
    List as ListIcon,
    Bookmark
} from "lucide-react";
import { motion } from "framer-motion";

export default function FindWorkPage() {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [keywords, setKeywords] = useState("");
    const [experienceLevel, setExperienceLevel] = useState("");

    const fetchJobs = async () => {
        setLoading(true);
        try {
            let url = "/marketplace/requests?";
            if (keywords) url += `keywords=${keywords}&`;
            if (experienceLevel) url += `experience_level=${experienceLevel}&`;

            const res = await api.get(url);
            setJobs(res.data);
        } catch (err) {
            console.error("Failed to fetch jobs", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchJobs();
    }, [keywords, experienceLevel]);

    return (
        <div className="min-h-screen bg-muted/30 pt-32 pb-20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Header (V1 Mirror) */}
                <div className="mb-12">
                    <div className="flex items-center space-x-6">
                        <div className="w-16 h-16 bg-gradient-to-br from-primary to-secondary rounded-[1.5rem] flex items-center justify-center shadow-2xl">
                            <Briefcase className="w-8 h-8 text-white" />
                        </div>
                        <div>
                            <h1 className="text-4xl font-black text-gray-900 tracking-tight">Find Work</h1>
                            <p className="text-muted-foreground mt-1 font-medium">Discover learning opportunities that match your skills</p>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-4 gap-12">
                    {/* Filters Sidebar (V1 Mirror) */}
                    <div className="lg:col-span-1">
                        <div className="glass-panel rounded-[2.5rem] p-8 sticky top-32 shadow-2xl border-white/50">
                            <div className="flex items-center justify-between mb-8">
                                <h3 className="text-lg font-black text-gray-900 flex items-center">
                                    <Filter className="w-5 h-5 mr-3 text-primary" />
                                    Filters
                                </h3>
                            </div>

                            <div className="space-y-8">
                                {/* Keywords */}
                                <div>
                                    <label className="block text-xs font-black uppercase tracking-widest text-muted-foreground mb-4">Keywords</label>
                                    <div className="relative">
                                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                                        <input
                                            type="text"
                                            placeholder="e.g., Python, Design"
                                            className="w-full pl-11 pr-4 py-3.5 bg-white border border-gray-200 rounded-2xl text-sm font-bold focus:ring-2 focus:ring-primary outline-none transition-all"
                                            value={keywords}
                                            onChange={(e) => setKeywords(e.target.value)}
                                        />
                                    </div>
                                </div>

                                {/* Experience Level */}
                                <div>
                                    <label className="block text-xs font-black uppercase tracking-widest text-muted-foreground mb-4">Experience Level</label>
                                    <div className="space-y-3">
                                        {["Beginner", "Intermediate", "Expert"].map((level) => (
                                            <label key={level} className="flex items-center group cursor-pointer">
                                                <input
                                                    type="radio"
                                                    name="experience"
                                                    className="hidden"
                                                    checked={experienceLevel === level.toLowerCase()}
                                                    onChange={() => setExperienceLevel(level.toLowerCase())}
                                                />
                                                <div className={`w-6 h-6 rounded-lg border-2 mr-3 flex items-center justify-center transition-all ${experienceLevel === level.toLowerCase()
                                                        ? "border-primary bg-primary text-white shadow-lg shadow-primary/20"
                                                        : "border-gray-200 bg-white group-hover:border-primary/50"
                                                    }`}>
                                                    {experienceLevel === level.toLowerCase() && <Zap size={10} className="fill-white" />}
                                                </div>
                                                <span className={`text-sm font-bold transition-colors ${experienceLevel === level.toLowerCase() ? "text-gray-900" : "text-muted-foreground group-hover:text-gray-700"
                                                    }`}>{level}</span>
                                            </label>
                                        ))}
                                    </div>
                                </div>

                                {/* Budget Range (Dummy for UI Mirror) */}
                                <div>
                                    <label className="block text-xs font-black uppercase tracking-widest text-muted-foreground mb-4">Budget Range</label>
                                    <select className="w-full px-4 py-3.5 bg-white border border-gray-200 rounded-2xl text-sm font-bold focus:ring-2 focus:ring-primary outline-none appearance-none">
                                        <option>Any Budget</option>
                                        <option>$0 - $100</option>
                                        <option>$100 - $500</option>
                                        <option>$500+</option>
                                    </select>
                                </div>

                                <button
                                    onClick={() => {
                                        setKeywords("");
                                        setExperienceLevel("");
                                    }}
                                    className="w-full py-4 text-sm font-black uppercase tracking-widest text-muted-foreground hover:text-error transition-colors text-center"
                                >
                                    Clear all filters
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Job Listings (V1 Mirror) */}
                    <div className="lg:col-span-3">
                        {/* Control Bar */}
                        <div className="glass-panel rounded-[1.5rem] p-4 mb-8 flex flex-col md:flex-row items-center justify-between gap-4 border-white/50">
                            <div className="flex items-center space-x-2">
                                <span className="text-sm font-bold text-muted-foreground uppercase tracking-widest mr-4">Sort by:</span>
                                <select className="px-5 py-2.5 bg-white border border-gray-200 rounded-xl text-sm font-bold outline-none focus:ring-2 focus:ring-primary cursor-pointer mb-0">
                                    <option>Most Recent</option>
                                    <option>Best Match</option>
                                    <option>Highest Budget</option>
                                </select>
                            </div>
                            <div className="flex items-center space-x-2">
                                <button className="p-2.5 bg-primary/10 text-primary rounded-xl border border-primary/20">
                                    <LayoutGrid className="w-5 h-5" />
                                </button>
                                <button className="p-2.5 text-muted-foreground hover:bg-muted rounded-xl transition-all">
                                    <ListIcon className="w-5 h-5" />
                                </button>
                            </div>
                        </div>

                        {/* Jobs Grid */}
                        {loading ? (
                            <div className="space-y-6">
                                {[1, 2, 3].map(i => (
                                    <div key={i} className="bg-white rounded-[2rem] h-[250px] animate-pulse"></div>
                                ))}
                            </div>
                        ) : (
                            <div className="space-y-8">
                                {jobs.map((job: any) => (
                                    <JobCard key={job.id} job={job} />
                                ))}

                                {jobs.length === 0 && (
                                    <div className="text-center py-32 glass-panel rounded-[3rem] border-2 border-dashed border-gray-200/50">
                                        <div className="w-20 h-20 bg-muted rounded-[1.5rem] flex items-center justify-center mx-auto mb-6">
                                            <Briefcase className="w-10 h-10 text-muted-foreground/30" />
                                        </div>
                                        <h3 className="text-2xl font-black text-gray-900 mb-2">No learning requests found</h3>
                                        <p className="text-gray-500 font-medium max-w-sm mx-auto">Try adjusting your filters or search terms to find new coaching opportunities.</p>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Pagination (UI Mirror) */}
                        {jobs.length > 0 && (
                            <div className="mt-16 flex items-center justify-between px-4">
                                <p className="text-sm font-bold text-muted-foreground">Showing 1-{jobs.length} of {jobs.length} results</p>
                                <div className="flex space-x-2">
                                    <button className="w-10 h-10 flex items-center justify-center rounded-xl bg-white border border-gray-200 text-gray-400">&lt;</button>
                                    <button className="w-10 h-10 flex items-center justify-center rounded-xl bg-primary text-white font-black shadow-lg shadow-primary/20">1</button>
                                    <button className="w-10 h-10 flex items-center justify-center rounded-xl bg-white border border-gray-200 text-gray-400 font-bold">2</button>
                                    <button className="w-10 h-10 flex items-center justify-center rounded-xl bg-white border border-gray-200 text-gray-400">&gt;</button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
