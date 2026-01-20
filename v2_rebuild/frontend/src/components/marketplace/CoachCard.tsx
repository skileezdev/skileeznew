"use client";

import { Star, Heart, MessageCircle, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

interface Coach {
    user_id: number;
    first_name: string;
    last_name: string;
    coach_title?: string;
    bio?: string;
    skills?: string;
    rating?: number;
    hourly_rate?: number;
    profile_picture?: string;
}

export function CoachCard({ coach }: { coach: Coach }) {
    const skills = coach.skills ? coach.skills.split(",").slice(0, 2) : [];
    const extraSkillsCount = coach.skills ? coach.skills.split(",").length - 2 : 0;

    return (
        <motion.div
            whileHover={{ y: -8 }}
            className="premium-card flex flex-col h-full group"
        >
            {/* Coach Header */}
            <div className="flex items-start space-x-4 mb-4">
                {/* Profile Photo with Online Status */}
                <div className="relative flex-shrink-0">
                    {coach.profile_picture ? (
                        <img
                            src={coach.profile_picture}
                            alt={coach.first_name}
                            className="w-16 h-16 rounded-2xl object-cover border-2 border-gray-100 shadow-sm"
                        />
                    ) : (
                        <div className="w-16 h-16 bg-gradient-to-br from-primary to-secondary rounded-2xl flex items-center justify-center text-white text-xl font-bold shadow-lg">
                            {coach.first_name[0]}{coach.last_name[0]}
                        </div>
                    )}
                    {/* Online Status Dot */}
                    <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-success border-2 border-white rounded-full animate-pulse"></div>
                </div>

                {/* Coach Info */}
                <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-bold text-gray-900 truncate group-hover:text-primary transition-colors">
                        {coach.first_name} {coach.last_name}
                    </h3>
                    {coach.coach_title && (
                        <p className="text-xs text-muted-foreground truncate font-medium">{coach.coach_title}</p>
                    )}

                    {/* Rating */}
                    <div className="flex items-center mt-2">
                        <div className="flex items-center">
                            {[...Array(5)].map((_, i) => (
                                <Star
                                    key={i}
                                    size={14}
                                    className={`${i < (coach.rating || 0) ? "text-amber-400 fill-amber-400" : "text-gray-200"}`}
                                />
                            ))}
                        </div>
                        <span className="ml-2 text-xs font-bold text-gray-900">
                            {(coach.rating || 0).toFixed(1)}
                        </span>
                    </div>
                </div>
            </div>

            {/* Bio Preview */}
            <p className="text-sm text-gray-500 mb-6 line-clamp-2 leading-relaxed">
                {coach.bio || "No bio available."}
            </p>

            {/* Skills Tags */}
            <div className="mb-6 flex-grow">
                <div className="flex flex-wrap gap-1.5">
                    {skills.map((skill, i) => (
                        <span key={i} className="px-3 py-1 text-[10px] font-bold bg-muted text-muted-foreground rounded-full border border-gray-200">
                            {skill.trim()}
                        </span>
                    ))}
                    {extraSkillsCount > 0 && (
                        <span className="px-3 py-1 text-[10px] font-bold bg-muted text-muted-foreground/60 rounded-full border border-gray-200">
                            +{extraSkillsCount}
                        </span>
                    )}
                </div>
            </div>

            {/* Price and Actions */}
            <div className="flex items-center justify-between pt-5 border-t border-gray-200 mt-auto">
                <div>
                    {coach.hourly_rate && (
                        <div className="flex flex-col">
                            <span className="text-2xl font-black text-gray-900">${coach.hourly_rate}</span>
                            <span className="text-[10px] text-muted-foreground font-bold uppercase tracking-widest">per hour</span>
                        </div>
                    )}
                </div>

                <div className="flex items-center space-x-2">
                    <button className="p-2.5 text-gray-400 hover:text-error hover:bg-error/5 rounded-xl transition-all">
                        <Heart size={20} />
                    </button>

                    <Link
                        href={`/profile/${coach.user_id}`}
                        className="btn-primary !px-5 !py-2.5 !text-sm whitespace-nowrap"
                    >
                        Book trial
                    </Link>
                </div>
            </div>

            {/* Premium Badge Overlay (Soul of V1) */}
            <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
                <ShieldCheck className="w-5 h-5 text-primary fill-primary/10" />
            </div>
        </motion.div>
    );
}
