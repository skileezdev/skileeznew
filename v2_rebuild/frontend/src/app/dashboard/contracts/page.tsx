"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import ContractCard from "@/components/dashboard/ContractCard";

export default function ContractsPage() {
    const [contracts, setContracts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        apiFetch("/contracts")
            .then(data => setContracts(data))
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    }, []);

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-6xl mx-auto">
                <h1 className="text-3xl font-bold text-gray-900 mb-8">My Contracts</h1>

                {loading ? (
                    <p>Loading your learning agreements...</p>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {contracts.map((contract: any) => (
                            <ContractCard key={contract.id} contract={contract} />
                        ))}
                        {contracts.length === 0 && (
                            <div className="col-span-full py-20 text-center bg-white rounded-2xl border-2 border-dashed border-gray-200">
                                <p className="text-gray-400">No active contracts found. Head to the marketplace to get started!</p>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
