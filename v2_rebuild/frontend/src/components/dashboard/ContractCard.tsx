"use client";

import Link from "next/link";

interface ContractCardProps {
    contract: {
        id: number;
        title: string;
        status: string;
        total_amount: number;
        created_at: string;
    };
}

export default function ContractCard({ contract }: ContractCardProps) {
    return (
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition">
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h3 className="text-xl font-bold text-gray-900">{contract.title || `Contract #${contract.id}`}</h3>
                    <p className="text-sm text-gray-400">Created on {new Date(contract.created_at).toLocaleDateString()}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${contract.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                    }`}>
                    {contract.status}
                </span>
            </div>

            <div className="flex justify-between items-center mt-6">
                <div className="text-lg font-bold text-indigo-600">
                    ${contract.total_amount.toFixed(2)}
                </div>
                <Link
                    href={`/dashboard/contracts/${contract.id}`}
                    className="text-sm font-bold text-gray-600 hover:text-indigo-600 transition"
                >
                    View Details →
                </Link>
            </div>
        </div>
    );
}
