"use client";

import {
    DollarSign,
    Clock,
    BarChart,
    Target,
    Calendar,
    Users,
    Eye,
    Bookmark,
    ChevronRight,
    Zap
} from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";
import { useState } from "react";
import { ProposalModal } from "./ProposalModal";

interface Job {
    id: number;
    title: string;
    description: string;
    budget?: number;
    duration?: string;
    experience_level?: string;
    skill_type?: string;
    created_at: string;
    skills_needed?: string;
    proposals_count?: number;
}

export function JobCard({ job }: { job: Job }) {
    const [isProposalOpen, setIsProposalOpen] = useState(false);
    const skills = job.skills_needed ? job.skills_needed.split(",").slice(0, 5) : [];
    const extraSkillsCount = job.skills_needed ? job.skills_needed.split(",").length - 5 : 0;

    return (
        <motion.div
            whileHover={{ y: -4 }}
            className="bg-white rounded-[2rem] shadow-sm border border-border overflow-hidden hover:shadow-xl hover:border-primary/20 transition-all cursor-pointer group"
        >
            <div className="p-8">
                <div className="flex justify-between items-start mb-6">
                    <div className="flex-grow">
                        <h3 className="text-2xl font-black text-gray-900 mb-3 group-hover:text-primary transition-colors leading-tight">
                            {job.title}
                        </h3>

                        <div className="flex flex-wrap items-center gap-x-6 gap-y-3 text-sm text-gray-500 font-medium mb-5">
                            <span className="flex items-center">
                                <DollarSign className="w-4 h-4 mr-1.5 text-success" />
                                <span className="font-bold text-gray-700">${job.budget || 0}</span>
                            </span>
                            <span className="flex items-center">
                                <Clock className="w-4 h-4 mr-1.5 text-primary" />
                                {job.duration || "Short term"}
                            </span>
                            <span className="flex items-center capitalize">
                                <BarChart className="w-4 h-4 mr-1.5 text-secondary" />
                                {job.experience_level || "Beginner"} Level
                            </span>
                            <span className="flex items-center">
                                <Target className="w-4 h-4 mr-1.5 text-orange-500" />
                                {job.skill_type === "short_term" ? "Quick Skill" : "Deep Skill"}
                            </span>
                            <span className="flex items-center">
                                <Calendar className="w-4 h-4 mr-1.5 text-muted-foreground" />
                                {new Date(job.created_at).toLocaleDateString("en-US", { month: "long", day: "numeric" })}
                            </span>
                        </div>

                        <p className="text-gray-500 font-medium leading-relaxed mb-6 line-clamp-2">
                            {job.description}
                        </p>

                        <div className="flex flex-wrap gap-2 mb-8">
                            {skills.map((skill, i) => (
                                <span
                                    key={i}
                                    className="px-4 py-1.5 bg-muted text-muted-foreground rounded-full text-xs font-bold border border-border"
                                >
                                    {skill.trim()}
                                </span>
                            ))}
                            {extraSkillsCount > 0 && (
                                <span className="text-muted-foreground text-xs font-bold pt-1.5">
                                    +{extraSkillsCount} more
                                </span>
                            )}
                        </div>

                        <div className="flex flex-col sm:flex-row items-center justify-between gap-6 pt-6 border-t border-border">
                            <div className="flex items-center space-x-6 text-sm text-muted-foreground font-bold uppercase tracking-widest">
                                <span className="flex items-center">
                                    <Users className="w-4 h-4 mr-2" />
                                    {job.proposals_count || 0} proposals
                                </span>
                                <span className="flex items-center">
                                    <Eye className="w-4 h-4 mr-2" />
                                    156 views
                                </span>
                            </div>

                            <div className="flex items-center space-x-3 w-full sm:w-auto">
                                <Link
                                    href={`/marketplace/jobs/${job.id}`}
                                    className="px-6 py-3 bg-muted text-gray-700 rounded-xl font-bold text-sm hover:bg-muted/80 transition-all flex-1 sm:flex-none text-center"
                                >
                                    View Details
                                </Link>
                                <button
                                    onClick={() => setIsProposalOpen(true)}
                                    className="btn-primary !px-8 !py-3 !text-sm flex-1 sm:flex-none flex items-center justify-center gap-2"
                                >
                                    Submit Proposal <Zap size={16} className="fill-white" />
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center space-x-2 ml-4">
                        <button className="text-gray-300 hover:text-primary transition-all p-2.5 hover:bg-primary/5 rounded-xl">
                            <Bookmark className="w-6 h-6" />
                        </button>
                    </div>
                </div>
            </div>

            <ProposalModal
                isOpen={isProposalOpen}
                onClose={() => setIsProposalOpen(false)}
                requestId={job.id}
                requestTitle={job.title}
                onSuccess={() => {
                    // Optionally refresh the job list or show success message
                }}
            />
        </motion.div>
    );
}
