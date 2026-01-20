"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { FileText, CheckCircle, Clock, AlertCircle, ChevronRight } from "lucide-react";
import Link from "next/link";

export default function ContractsPage() {
    const [contracts, setContracts] = useState([]);
    const [loading, setLoading] = useState(true);

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

    const getStatusColor = (status: string) => {
        switch (status) {
            case "active": return "text-green-600 bg-green-50 border-green-200";
            case "completed": return "text-blue-600 bg-blue-50 border-blue-200";
            case "awaiting_response": return "text-amber-600 bg-amber-50 border-amber-200";
            default: return "text-gray-600 bg-gray-50 border-gray-200";
        }
    };

    return (
        <div className="min-h-screen bg-muted/30 pt-32 pb-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-end mb-8">
                    <div>
                        <h1 className="text-4xl font-black text-gray-900 tracking-tight">Contracts</h1>
                        <p className="text-muted-foreground mt-2 font-medium">Manage your learning agreements and progress.</p>
                    </div>
                </div>

                {loading ? (
                    <div className="space-y-4">
                        {[1, 2, 3].map(i => <div key={i} className="h-32 bg-white rounded-3xl animate-pulse" />)}
                    </div>
                ) : (
                    <div className="grid gap-6">
                        {contracts.map((contract: any) => (
                            <div
                                key={contract.id}
                                className="bg-white rounded-[2rem] p-6 shadow-sm border border-gray-100 hover:shadow-lg transition-all group"
                            >
                                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                                    <div className="flex items-start gap-4">
                                        <div className="w-12 h-12 bg-gray-100 rounded-2xl flex items-center justify-center text-gray-400 group-hover:bg-primary/10 group-hover:text-primary transition-colors">
                                            <FileText size={24} />
                                        </div>
                                        <div>
                                            <h3 className="text-xl font-bold text-gray-900">
                                                {contract.contract_number}
                                            </h3>
                                            <div className="flex items-center gap-3 mt-1 text-sm text-gray-500 font-medium">
                                                <span>Started {new Date(contract.created_at).toLocaleDateString()}</span>
                                                <span>•</span>
                                                <span>{contract.total_sessions} Sessions Total</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-6">
                                        <div className="flex flex-col items-end">
                                            <span className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider border ${getStatusColor(contract.status)}`}>
                                                {contract.status.replace("_", " ")}
                                            </span>
                                            <div className="mt-2 text-sm font-bold text-gray-700">
                                                {contract.completed_sessions} / {contract.total_sessions} Completed
                                            </div>
                                            <div className="w-32 h-2 bg-gray-100 rounded-full mt-1 overflow-hidden">
                                                <div
                                                    className="h-full bg-primary rounded-full"
                                                    style={{ width: `${(contract.completed_sessions / contract.total_sessions) * 100}%` }}
                                                />
                                            </div>
                                        </div>

                                        <Link
                                            href={`/contracts/${contract.id}`}
                                            className="p-3 bg-gray-50 hover:bg-primary hover:text-white rounded-2xl transition-all"
                                        >
                                            <ChevronRight size={20} />
                                        </Link>
                                    </div>
                                </div>
                            </div>
                        ))}

                        {contracts.length === 0 && (
                            <div className="text-center py-20 bg-white rounded-[3rem] border-2 border-dashed border-gray-200">
                                <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <FileText className="w-8 h-8 text-gray-400" />
                                </div>
                                <h3 className="text-xl font-bold text-gray-900">No contracts yet</h3>
                                <p className="text-gray-500 mt-2">Contracts will appear here once you accept a proposal.</p>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
