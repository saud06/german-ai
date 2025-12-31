'use client';

import { useRouter } from 'next/navigation';
import { useJourney } from '@/contexts/JourneyContext';
import { useEffect } from 'react';

export default function OnboardingWelcome() {
  const router = useRouter();
  const { activeJourney, loading } = useJourney();

  // If user already has a journey, redirect to dashboard
  useEffect(() => {
    if (!loading && activeJourney) {
      window.location.href = '/dashboard';
    }
  }, [loading, activeJourney]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full animate-fade-in">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 md:p-12 border border-gray-200 dark:border-gray-700">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-block mb-4">
              <div className="text-6xl">🎯</div>
            </div>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Welcome to Your German Learning Journey!
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              Let's personalize your experience to match your goals
            </p>
          </div>

          {/* Content */}
          <div className="space-y-6 mb-8">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                <span className="text-xl">✨</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                  Tailored Content
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Get lessons, scenarios, and exercises that match your specific learning goals
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-10 h-10 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
                <span className="text-xl">🎯</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                  Multiple Journeys
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Start with one goal and add more anytime - learn for travel, work, exams, or fun
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-10 h-10 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
                <span className="text-xl">📊</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                  Track Your Progress
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  See your advancement with journey-specific milestones and achievements
                </p>
              </div>
            </div>
          </div>

          {/* CTA */}
          <div>
            <button
              onClick={() => router.push('/onboarding/select-purpose')}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-200 transform hover:scale-105 shadow-lg"
            >
              Let's Get Started →
            </button>
            <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-4">
              Takes less than 2 minutes
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
