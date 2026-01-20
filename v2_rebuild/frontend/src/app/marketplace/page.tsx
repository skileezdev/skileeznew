"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import Link from "next/link";
import ProposalModal from "@/components/marketplace/ProposalModal";

interface LearningRequest {
    id: number;
    title: string;
    description: string;
    budget: number | null;
    experience_level: string | null;
    student: {
        first_name: string;
        last_name: string;
    };
    created_at: string;
}

export default function MarketplacePage() {
    const [requests, setRequests] = useState<LearningRequest[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedRequest, setSelectedRequest] = useState<LearningRequest | null>(null);
    const [success, setSuccess] = useState(false);

    const fetchRequests = () => {
        setLoading(true);
        apiFetch("/marketplace/requests")
            .then((data) => setRequests(data))
            .catch((err) => console.error(err))
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        fetchRequests();
    }, []);

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-6xl mx-auto">
                {success && (
                    <div className="mb-6 p-4 bg-green-100 text-green-700 rounded-lg text-center font-bold animate-bounce">
                        Proposal sent successfully! 🚀
                    </div>
                )}

                <div className="flex justify-between items-center mb-10">
                    <div>
                        <h1 className="text-4xl font-extrabold text-gray-900">Learning Marketplace</h1>
                        <p className="text-gray-500 mt-2">Browse requests and share your knowledge</p>
                    </div>
                    <Link href="/marketplace/create" className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition">
                        Post a Request
                    </Link>
                </div>

                {loading ? (
                    <p className="text-center py-20 text-indigo-500 font-medium">Searching for requests...</p>
                ) : (
                    <div className="grid grid-cols-1 gap-6">
                        {requests.map((req) => (
                            <div key={req.id} className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition group">
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h3 className="text-2xl font-bold text-gray-900 group-hover:text-indigo-600 transition">{req.title}</h3>
                                        <p className="text-sm text-gray-400 mt-1">
                                            Posted by {req.student.first_name} {req.student.last_name} • {new Date(req.created_at).toLocaleDateString()}
                                        </p>
                                    </div>
                                    {req.budget && (
                                        <span className="bg-green-100 text-green-700 px-4 py-1 rounded-full font-bold">
                                            ${req.budget}
                                        </span>
                                    )}
                                </div>
                                <p className="text-gray-600 mt-4 line-clamp-3">{req.description}</p>

                                <div className="mt-6 flex items-center justify-between">
                                    <div className="flex gap-2">
                                        {req.experience_level && (
                                            <span className="bg-gray-100 text-gray-600 px-3 py-1 rounded-md text-sm capitalize">
                                                {req.experience_level}
                                            </span>
                                        )}
                                    </div>
                                    <button
                                        onClick={() => setSelectedRequest(req)}
                                        className="text-indigo-600 font-bold border-2 border-indigo-600 px-6 py-2 rounded-lg hover:bg-indigo-50 transition"
                                    >
                                        Submit Proposal
                                    </button>
                                </div>
                            </div>
                        ))}
                        {requests.length === 0 && (
                            <div className="text-center py-20 bg-white rounded-2xl border-2 border-dashed border-gray-200">
                                <p className="text-gray-400 font-medium">No active learning requests at the moment.</p>
                            </div>
                        )}
                    </div>
                )}

                {selectedRequest && (
                    <ProposalModal
                        requestId={selectedRequest.id}
                        requestTitle={selectedRequest.title}
                        onClose={() => setSelectedRequest(null)}
                        onSuccess={() => {
                            setSelectedRequest(null);
                            setSuccess(true);
                            setTimeout(() => setSuccess(false), 5000);
                            fetchRequests();
                        }}
                    />
                )}
            </div>
        </div>
    );
}
