'use client';

import { useJourney } from '@/contexts/JourneyContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import Link from 'next/link';

interface JourneyDashboardProps {
  children: React.ReactNode;
}

export default function JourneyDashboard({ children }: JourneyDashboardProps) {
  const { activeJourney, loading, onboardingCompleted } = useJourney();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !activeJourney) {
      window.location.href = '/onboarding/welcome';
    }
  }, [loading, activeJourney]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-300">Loading your journey...</p>
        </div>
      </div>
    );
  }

  if (!activeJourney) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">🎯</div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            No Active Journey
          </h2>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Start your personalized learning experience by selecting a journey.
          </p>
          <Link
            href="/onboarding/welcome"
            className="inline-block px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all"
          >
            Get Started
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {children}
    </div>
  );
}
