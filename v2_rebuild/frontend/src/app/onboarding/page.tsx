'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import CoachWizard from './components/CoachWizard';
import StudentWizard from './components/StudentWizard';

export default function OnboardingPage() {
    const { user, loading: authLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!authLoading && !user) {
            router.push('/login');
        }
        // Note: AuthContext already redirects to /dashboard if onboarding_completed is true
    }, [user, authLoading, router]);

    if (authLoading || !user) {
        return (
            <div className="flex justify-center items-center h-screen bg-gray-50">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-600"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl mx-auto text-center mb-10">
                <h1 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
                    Welcome, {user.first_name}!
                </h1>
                <p className="mt-4 text-xl text-gray-500">
                    Let's get your profile set up so you can start {user.current_role === 'coach' ? 'teaching' : 'learning'}.
                </p>
            </div>

            {user.current_role === 'coach' ? (
                <CoachWizard />
            ) : (
                <StudentWizard />
            )}
        </div>
    );
}
