"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { CoachCard } from "@/components/marketplace/CoachCard";
import {
    Search,
    Filter,
    MapPin,
    Globe,
    DollarSign,
    ChevronDown,
    X,
    RefreshCw,
    SlidersHorizontal
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function BrowseCoachesPage() {
    const [coaches, setCoaches] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [priceRange, setPriceRange] = useState("");
    const [sort, setSort] = useState("top");
    const [showFilters, setShowFilters] = useState(false);

    const fetchCoaches = async () => {
        setLoading(true);
        try {
            let url = "/marketplace/coaches?";
            if (searchTerm) url += `search=${searchTerm}&`;
            if (sort) url += `sort=${sort}&`;

            if (priceRange) {
                if (priceRange === "10-25") url += "price_min=10&price_max=25&";
                else if (priceRange === "25-50") url += "price_min=25&price_max=50&";
                else if (priceRange === "50-100") url += "price_min=50&price_max=100&";
                else if (priceRange === "100+") url += "price_min=100&";
            }

            const res = await api.get(url);
            setCoaches(res.data);
        } catch (err) {
            console.error("Failed to fetch coaches", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCoaches();
    }, [searchTerm, priceRange, sort]);

    return (
        <div className="min-h-screen bg-muted/30">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 pt-32">
                {/* Header (V1 Mirror) */}
                <div className="text-center mb-16">
                    <motion.h1
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-4xl md:text-5xl font-black text-gray-900 mb-6"
                    >
                        {searchTerm ? `Discover ${searchTerm} coaches` : "Expert coaches & mentors for personalized learning"}
                    </motion.h1>
                    <p className="text-xl text-muted-foreground max-w-2xl mx-auto font-medium">
                        Find the perfect coach to help you master new skills and achieve your learning goals effortlessly.
                    </p>
                </div>

                {/* Filter Bar (Premium V1 Translation) */}
                <div className="glass-panel rounded-[2rem] p-4 md:p-6 mb-12 shadow-2xl relative z-20">
                    <div className="flex flex-col lg:flex-row items-center gap-4">
                        {/* Search */}
                        <div className="relative flex-grow w-full lg:w-auto">
                            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground w-5 h-5" />
                            <input
                                type="text"
                                placeholder="Name, skills, or keywords"
                                className="w-full pl-12 pr-4 py-4 bg-white/50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-primary outline-none font-bold transition-all"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>

                        {/* Quick Filters */}
                        <div className="flex items-center gap-4 w-full lg:w-auto">
                            <select
                                className="flex-1 lg:flex-none px-6 py-4 bg-white border border-gray-200 rounded-2xl font-bold text-sm outline-none focus:ring-2 focus:ring-primary appearance-none cursor-pointer"
                                value={priceRange}
                                onChange={(e) => setPriceRange(e.target.value)}
                            >
                                <option value="">Any price</option>
                                <option value="10-25">$10 - $25</option>
                                <option value="25-50">$25 - $50</option>
                                <option value="50-100">$50 - $100</option>
                                <option value="100+">$100+</option>
                            </select>

                            <select
                                className="flex-1 lg:flex-none px-6 py-4 bg-white border border-gray-200 rounded-2xl font-bold text-sm outline-none focus:ring-2 focus:ring-primary appearance-none cursor-pointer"
                                value={sort}
                                onChange={(e) => setSort(e.target.value)}
                            >
                                <option value="top">Top Picks</option>
                                <option value="rating">Highest Rated</option>
                                <option value="price_low">Price: Low to High</option>
                                <option value="price_high">Price: High to Low</option>
                            </select>

                            <button
                                onClick={() => setShowFilters(!showFilters)}
                                className={`p-4 rounded-2xl border transition-all ${showFilters ? "bg-primary text-white border-primary" : "bg-white text-gray-700 border-gray-200"
                                    }`}
                            >
                                <SlidersHorizontal className="w-6 h-6" />
                            </button>
                        </div>
                    </div>

                    {/* Advanced Filters (Expandable) */}
                    <AnimatePresence>
                        {showFilters && (
                            <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: "auto", opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                className="overflow-hidden"
                            >
                                <div className="pt-6 mt-6 border-t border-gray-200 grid grid-cols-1 md:grid-cols-4 gap-6">
                                    <div>
                                        <label className="block text-xs font-black uppercase tracking-widest text-muted-foreground mb-3">Country</label>
                                        <select className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl font-bold text-sm">
                                            <option>Any Country</option>
                                            <option>United States</option>
                                            <option>United Kingdom</option>
                                            <option>Canada</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-xs font-black uppercase tracking-widest text-muted-foreground mb-3">Language</label>
                                        <select className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl font-bold text-sm">
                                            <option>Any Language</option>
                                            <option>English</option>
                                            <option>Spanish</option>
                                            <option>French</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-xs font-black uppercase tracking-widest text-muted-foreground mb-3">Experience</label>
                                        <select className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl font-bold text-sm">
                                            <option>Any Experience</option>
                                            <option>1-3 Years</option>
                                            <option>3-5 Years</option>
                                            <option>5+ Years</option>
                                        </select>
                                    </div>
                                    <div className="flex items-end">
                                        <button
                                            onClick={() => {
                                                setSearchTerm("");
                                                setPriceRange("");
                                                setSort("top");
                                            }}
                                            className="w-full py-3 text-sm font-bold text-error bg-error/5 hover:bg-error/10 rounded-xl transition-all"
                                        >
                                            Clear All Filters
                                        </button>
                                    </div>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                {/* Results Info */}
                <div className="flex items-center justify-between mb-8 px-4">
                    <p className="text-muted-foreground font-bold uppercase text-xs tracking-[0.2em]">
                        {coaches.length} Professional Coaches found
                    </p>
                </div>

                {/* Coach Grid */}
                {loading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                        {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
                            <div key={i} className="bg-white rounded-[2rem] h-[400px] animate-pulse"></div>
                        ))}
                    </div>
                ) : (
                    <>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                            {coaches.map((coach: any) => (
                                <CoachCard key={coach.id} coach={{ ...coach, ...coach.user }} />
                            ))}
                        </div>

                        {coaches.length === 0 && (
                            <div className="text-center py-24 bg-white rounded-[3rem] border-2 border-dashed border-gray-200">
                                <div className="w-20 h-20 bg-muted rounded-full flex items-center justify-center mx-auto mb-6">
                                    <Search className="w-10 h-10 text-muted-foreground/30" />
                                </div>
                                <h3 className="text-2xl font-black text-gray-900 mb-2">No coaches found</h3>
                                <p className="text-gray-500 font-medium">Try adjusting your filters or searching for something else.</p>
                                <button
                                    onClick={() => setSearchTerm("")}
                                    className="mt-8 px-8 py-3 bg-primary text-white rounded-xl font-bold shadow-lg"
                                >
                                    Browse All
                                </button>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}
