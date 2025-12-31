'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

interface Journey {
  id: string;
  type: string;
  level: string;
  configuration?: {
    display_name: string;
    icon: string;
    color: string;
    dashboard_config: {
      hero_title: string;
      hero_subtitle: string;
    };
  };
}

export default function OnboardingConfirmation() {
  const router = useRouter();
  const [journey, setJourney] = useState<Journey | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchActiveJourney();
  }, []);

  const fetchActiveJourney = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/journeys/active', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setJourney(data.active_journey);
      }
    } catch (error) {
      console.error('Error fetching journey:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartJourney = () => {
    // Force full page reload to refresh journey context
    window.location.href = '/dashboard';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-300">Setting up your journey...</p>
        </div>
      </div>
    );
  }

  if (!journey || !journey.configuration) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 dark:text-red-400">Journey not found</p>
          <button
            onClick={() => router.push('/onboarding/select-purpose')}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg"
          >
            Start Over
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 md:p-12 border border-gray-200 dark:border-gray-700">
          {/* Success Icon */}
          <div className="text-center mb-8">
            <div className="inline-block mb-4">
              <div className="w-20 h-20 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
                <svg className="w-10 h-10 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Your Journey is Ready! 🎉
            </h1>
          </div>

          {/* Journey Summary */}
          <div className="mb-8">
            <div 
              className="p-6 rounded-xl border-2"
              style={{ 
                borderColor: journey.configuration.color,
                backgroundColor: `${journey.configuration.color}10`
              }}
            >
              <div className="flex items-center space-x-4 mb-4">
                <div 
                  className="w-16 h-16 rounded-xl flex items-center justify-center text-3xl"
                  style={{ backgroundColor: `${journey.configuration.color}20` }}
                >
                  {journey.configuration.icon}
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {journey.configuration.display_name}
                  </h2>
                  <p className="text-gray-600 dark:text-gray-300">
                    Level: <span className="font-semibold">{journey.level}</span>
                  </p>
                </div>
              </div>
              <div className="border-t border-gray-200 dark:border-gray-700 pt-4 mt-4">
                <p className="text-gray-700 dark:text-gray-300 mb-2">
                  <strong>Focus:</strong> {journey.configuration.dashboard_config.hero_subtitle}
                </p>
              </div>
            </div>
          </div>

          {/* What's Next */}
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-6 mb-8">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <span className="text-2xl mr-2">🚀</span>
              What's Next?
            </h3>
            <ul className="space-y-3">
              <li className="flex items-start space-x-3">
                <span className="text-green-600 dark:text-green-400 mt-1">✓</span>
                <span className="text-gray-700 dark:text-gray-300">
                  Access your personalized dashboard with tailored content
                </span>
              </li>
              <li className="flex items-start space-x-3">
                <span className="text-green-600 dark:text-green-400 mt-1">✓</span>
                <span className="text-gray-700 dark:text-gray-300">
                  Start with lessons and scenarios matched to your goals
                </span>
              </li>
              <li className="flex items-start space-x-3">
                <span className="text-green-600 dark:text-green-400 mt-1">✓</span>
                <span className="text-gray-700 dark:text-gray-300">
                  Add more journeys anytime from your settings
                </span>
              </li>
            </ul>
          </div>

          {/* CTA */}
          <button
            onClick={handleStartJourney}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-200 transform hover:scale-105 shadow-lg"
          >
            Start Your Tailored Journey →
          </button>

          {/* Progress Indicator */}
          <div className="mt-8 flex justify-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-blue-600"></div>
            <div className="w-2 h-2 rounded-full bg-blue-600"></div>
            <div className="w-2 h-2 rounded-full bg-blue-600"></div>
          </div>
        </div>
      </div>
    </div>
  );
}
