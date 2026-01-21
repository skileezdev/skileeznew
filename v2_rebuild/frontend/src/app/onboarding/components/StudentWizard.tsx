'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/services/api';
import { COUNTRIES, LANGUAGES, PROFICIENCIES } from '@/data/onboarding_constants';

interface StudentLanguage {
    language: string;
    proficiency: string;
}

export default function StudentWizard() {
    const router = useRouter();
    const { user, refreshUser } = useAuth();
    const profile = user?.student_profile;

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const [formData, setFormData] = useState({
        bio: '',
        age: '', // Input as string for easier handling, convert to int for API
        country: '',
        student_languages: [] as StudentLanguage[]
    });

    useEffect(() => {
        if (profile) {
            setFormData(prev => ({
                ...prev,
                bio: profile.bio || '',
                age: profile.age?.toString() || '',
                country: profile.country || '',
                student_languages: profile.languages || [] // Note: API maps this relationship
            }));
        }
    }, [profile]);

    const handleSubmit = async () => {
        setLoading(true);
        setError('');

        if (!formData.bio || formData.bio.length < 50) {
            setError('Bio must be at least 50 characters');
            setLoading(false);
            return;
        }
        if (!formData.age) {
            setError('Age is required');
            setLoading(false);
            return;
        }
        if (!formData.country) {
            setError('Country is required');
            setLoading(false);
            return;
        }

        try {
            await api.patch('/profiles/me', {
                bio: formData.bio,
                age: parseInt(formData.age),
                country: formData.country,
                student_languages: formData.student_languages,
                onboarding_completed: true
            });

            await refreshUser();
            router.push('/dashboard');

        } catch (err: any) {
            setError(err.message || 'Failed to populate profile');
        } finally {
            setLoading(false);
        }
    };

    const addLanguage = () => {
        setFormData(prev => ({
            ...prev,
            student_languages: [...prev.student_languages, { language: '', proficiency: '' }]
        }));
    };

    const removeLanguage = (index: number) => {
        const newLangs = [...formData.student_languages];
        newLangs.splice(index, 1);
        setFormData(prev => ({ ...prev, student_languages: newLangs }));
    };

    return (
        <div className="max-w-2xl mx-auto p-8 bg-white rounded-lg shadow-lg my-10 border border-gray-100">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Student Profile Setup</h2>

            {error && (
                <div className="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm">
                    {error}
                </div>
            )}

            <div className="space-y-6">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Tell us about yourself (Bio)</label>
                    <textarea
                        value={formData.bio}
                        onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                        className="w-full p-3 border border-gray-300 rounded h-32 focus:ring-purple-500 focus:border-purple-500"
                        placeholder="What are your learning goals? What interests you? (Min 50 chars)"
                    />
                </div>

                <div className="grid grid-cols-2 gap-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Age</label>
                        <input
                            type="number"
                            min="13"
                            max="100"
                            value={formData.age}
                            onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                            className="w-full p-3 border border-gray-300 rounded focus:ring-purple-500 focus:border-purple-500"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
                        <select
                            value={formData.country}
                            onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                            className="w-full p-3 border border-gray-300 rounded focus:ring-purple-500 focus:border-purple-500"
                        >
                            <option value="">Select Country</option>
                            {COUNTRIES.map(c => <option key={c} value={c}>{c}</option>)}
                        </select>
                    </div>
                </div>

                {/* Languages Section */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Languages You Speak</label>
                    <div className="space-y-3 mb-3">
                        {formData.student_languages.map((lang, index) => (
                            <div key={index} className="flex gap-3">
                                <select
                                    className="flex-1 p-2 border rounded"
                                    value={lang.language}
                                    onChange={(e) => {
                                        const newLangs = [...formData.student_languages];
                                        newLangs[index].language = e.target.value;
                                        setFormData({ ...formData, student_languages: newLangs });
                                    }}
                                >
                                    <option value="">Select Language</option>
                                    {LANGUAGES.map(l => <option key={l} value={l}>{l}</option>)}
                                </select>
                                <select
                                    className="flex-1 p-2 border rounded"
                                    value={lang.proficiency}
                                    onChange={(e) => {
                                        const newLangs = [...formData.student_languages];
                                        newLangs[index].proficiency = e.target.value;
                                        setFormData({ ...formData, student_languages: newLangs });
                                    }}
                                >
                                    <option value="">Proficiency</option>
                                    {PROFICIENCIES.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
                                </select>
                                <button onClick={() => removeLanguage(index)} className="text-red-500 font-bold px-2">X</button>
                            </div>
                        ))}
                    </div>
                    <button onClick={addLanguage} className="text-purple-600 text-sm font-medium hover:underline">+ Add Language</button>
                </div>

                <button
                    onClick={handleSubmit}
                    disabled={loading}
                    className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 rounded-lg shadow-md transition-all mt-6"
                >
                    {loading ? 'Saving Profile...' : 'Complete Profile'}
                </button>
            </div>
        </div>
    );
}
