"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";

export default function CreateRequestPage() {
    const [formData, setFormData] = useState({
        title: "",
        description: "",
        budget: "",
        experience_level: "beginner",
        skill_type: "short_term",
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            await apiFetch("/marketplace/requests", {
                method: "POST",
                body: JSON.stringify({
                    ...formData,
                    budget: formData.budget ? parseFloat(formData.budget) : null,
                }),
            });
            router.push("/marketplace");
        } catch (err: any) {
            setError(err.message || "Failed to create request");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-2xl mx-auto bg-white p-10 rounded-2xl shadow-sm border border-gray-100">
                <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">What do you want to learn?</h1>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {error && <div className="text-red-500 text-sm">{error}</div>}

                    <div>
                        <label className="block text-sm font-medium text-gray-700">Project Title</label>
                        <input
                            type="text"
                            required
                            placeholder="e.g., Learn Python for Data Science"
                            className="mt-1 block w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
                            value={formData.title}
                            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700">Description (Be specific)</label>
                        <textarea
                            required
                            rows={5}
                            placeholder="Explain what you want to achieve, your current level, and any specific requirements..."
                            className="mt-1 block w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
                            value={formData.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Est. Budget ($)</label>
                            <input
                                type="number"
                                placeholder="Optional"
                                className="mt-1 block w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
                                value={formData.budget}
                                onChange={(e) => setFormData({ ...formData, budget: e.target.value })}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Experience Level</label>
                            <select
                                className="mt-1 block w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
                                value={formData.experience_level}
                                onChange={(e) => setFormData({ ...formData, experience_level: e.target.value })}
                            >
                                <option value="beginner">Beginner</option>
                                <option value="intermediate">Intermediate</option>
                                <option value="advanced">Advanced</option>
                            </select>
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full flex justify-center py-4 px-4 border border-transparent rounded-xl shadow-sm text-lg font-bold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 transition"
                    >
                        {loading ? "Posting..." : "Post Request to Marketplace"}
                    </button>
                </form>
            </div>
        </div>
    );
}
