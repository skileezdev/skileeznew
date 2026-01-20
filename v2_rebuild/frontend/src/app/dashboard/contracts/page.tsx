"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import ContractCard from "@/components/dashboard/ContractCard";
import {
    Search,
    Briefcase,
    ArrowLeft,
    Plus,
    Filter,
    LayoutGrid
} from "lucide-react";
import Link from "next/link";

export default function ContractsPage() {
    const [contracts, setContracts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");

    useEffect(() => {
        const fetchContracts = async () => {
            try {
                const res = await api.get("/contracts");
                setContracts(res.data);
            } catch (err) {
                console.error("Failed to fetch contracts", err);
            } finally {
                setLoading(false);
            }
        };
        fetchContracts();
    }, []);

    const filteredContracts = contracts.filter((c: any) =>
        c.contract_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.learning_request?.title.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="min-h-screen bg-[#FDFDFF] p-8 md:p-12 font-inter">
            <div className="max-w-7xl mx-auto">
                {/* Header Section */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-16">
                    <div>
                        <div className="flex items-center gap-2 text-primary-600 font-black text-[10px] uppercase tracking-widest mb-3">
                            <Briefcase size={14} /> Agreement Workspace
                        </div>
                        <h1 className="text-5xl font-black text-gray-900 tracking-tight leading-tight">
                            My Contracts
                        </h1>
                        <p className="text-gray-400 mt-2 text-lg font-medium max-w-xl leading-relaxed">
                            Manage your active learning journeys and track your session progress.
                        </p>
                    </div>
                    <Link
                        href="/marketplace"
                        className="group py-4 px-8 bg-gray-900 text-white font-black rounded-2xl shadow-xl hover:shadow-2xl transition-all transform hover:-translate-y-1 active:scale-95 flex items-center gap-2"
                    >
                        New Agreement <Plus size={18} />
                    </Link>
                </div>

                {/* Filter Row */}
                <div className="flex flex-col md:flex-row gap-4 mb-12">
                    <div className="relative flex-1 group">
                        <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-primary-500 transition-colors" size={20} />
                        <input
                            type="text"
                            placeholder="Search by contract number or title..."
                            className="w-full pl-14 pr-6 py-4 bg-white border border-gray-100 rounded-[2rem] shadow-sm outline-none focus:ring-2 focus:ring-primary-500 transition-all font-medium text-gray-700 placeholder:text-gray-300"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <button className="px-8 py-4 bg-white border border-gray-100 rounded-[2rem] shadow-sm font-bold text-gray-500 flex items-center gap-2 hover:bg-gray-50 transition-all active:scale-95">
                        <Filter size={18} /> Status
                    </button>
                    <button className="p-4 bg-white border border-gray-100 rounded-[1.5rem] shadow-sm text-gray-400 hover:text-primary-600 transition-all">
                        <LayoutGrid size={20} />
                    </button>
                </div>

                {loading ? (
                    <div className="flex flex-col items-center justify-center py-32 space-y-4">
                        <div className="w-12 h-12 border-4 border-primary-100 border-t-primary-600 rounded-full animate-spin"></div>
                        <p className="text-gray-400 font-black uppercase text-[10px] tracking-widest">Loading Agreements...</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {filteredContracts.map((contract: any) => (
                            <ContractCard key={contract.id} contract={contract} />
                        ))}
                        {filteredContracts.length === 0 && (
                            <div className="col-span-full text-center py-32 bg-white rounded-[3rem] border-2 border-dashed border-gray-100">
                                <div className="text-6xl mb-6 grayscale opacity-20">📂</div>
                                <h3 className="text-2xl font-black text-gray-300">No contracts found</h3>
                                <p className="text-gray-400 font-medium mt-2 mb-8">Ready to start your next learning adventure?</p>
                                <Link
                                    href="/marketplace"
                                    className="inline-block py-4 px-10 bg-primary-600 text-white font-black rounded-2xl shadow-lg hover:shadow-xl transition-all"
                                >
                                    Explore Marketplace
                                </Link>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
