"use client";

import Link from "next/link";
import {
    Clock,
    ChevronRight,
    FileText,
    Calendar,
    CheckCircle2,
    RotateCcw
} from "lucide-react";

interface ContractCardProps {
    contract: {
        id: number;
        contract_number: string;
        learning_request: { title: string };
        status: string;
        total_amount: number;
        total_sessions: number;
        completed_sessions: number;
        created_at: string;
    };
}

export default function ContractCard({ contract }: ContractCardProps) {
    const progress = (contract.completed_sessions / contract.total_sessions) * 100;

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active': return 'bg-green-50 text-green-600 border-green-100';
            case 'awaiting_response': return 'bg-amber-50 text-amber-600 border-amber-100';
            case 'completed': return 'bg-primary-50 text-primary-600 border-primary-100';
            default: return 'bg-gray-50 text-gray-500 border-gray-100';
        }
    };

    return (
        <div className="bg-white p-8 rounded-[2.5rem] shadow-sm border border-gray-100 hover:shadow-xl hover:border-primary-100 transition-all group flex flex-col h-full relative overflow-hidden">
            {/* Minimal Header */}
            <div className="flex justify-between items-start mb-6">
                <div className="flex items-center gap-2">
                    <div className="p-2.5 bg-gray-50 text-gray-400 group-hover:text-primary-600 group-hover:bg-primary-50 rounded-xl transition-all">
                        <FileText size={20} />
                    </div>
                    <div>
                        <span className="text-[10px] font-black text-gray-300 uppercase tracking-widest block mb-0.5">Contract</span>
                        <span className="text-xs font-black text-gray-900">{contract.contract_number}</span>
                    </div>
                </div>
                <span className={`px-3 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest border transition-all ${getStatusColor(contract.status)}`}>
                    {contract.status.replace('_', ' ')}
                </span>
            </div>

            {/* Title & Date */}
            <div className="mb-8">
                <h3 className="text-2xl font-black text-gray-900 group-hover:text-primary-600 transition-colors leading-tight mb-2">
                    {contract.learning_request?.title || `Agreed Session #${contract.id}`}
                </h3>
                <div className="flex items-center gap-2 text-gray-400 text-xs font-bold">
                    <Calendar size={14} /> Created {new Date(contract.created_at).toLocaleDateString()}
                </div>
            </div>

            {/* Progress Section (V1 Mirror Core) */}
            <div className="space-y-3 mb-8">
                <div className="flex justify-between items-end">
                    <div className="flex items-center gap-2">
                        <Clock size={14} className="text-primary-400" />
                        <span className="text-sm font-bold text-gray-700">Journey Progress</span>
                    </div>
                    <span className="text-xs font-black text-primary-600 italic">
                        {contract.completed_sessions}/{contract.total_sessions} Sessions
                    </span>
                </div>
                <div className="h-2 w-full bg-gray-50 rounded-full overflow-hidden border border-gray-100">
                    <div
                        className="h-full bg-gradient-to-r from-primary-500 to-purple-600 rounded-full transition-all duration-1000 ease-out"
                        style={{ width: `${progress}%` }}
                    ></div>
                </div>
            </div>

            {/* Footer */}
            <div className="mt-auto pt-8 border-t border-gray-50 flex items-center justify-between">
                <div>
                    <span className="text-[10px] font-black text-gray-300 uppercase tracking-widest block mb-1">Agreement Total</span>
                    <span className="text-xl font-black text-gray-900">${contract.total_amount.toFixed(2)}</span>
                </div>
                <Link
                    href={`/dashboard/contracts/${contract.id}`}
                    className="py-3 px-6 bg-gray-900 text-white text-xs font-black rounded-2xl shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-1 active:scale-95 flex items-center gap-2"
                >
                    Management <ChevronRight size={14} />
                </Link>
            </div>
        </div>
    );
}
