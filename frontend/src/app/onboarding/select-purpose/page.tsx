'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface JourneyConfig {
  journey_type: string;
  display_name: string;
  description: string;
  icon: string;
  color: string;
  level_system: {
    type: string;
    levels: string[];
  };
}

export default function SelectPurpose() {
  const router = useRouter();
  const [configurations, setConfigurations] = useState<JourneyConfig[]>([]);
  const [selectedPurpose, setSelectedPurpose] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchConfigurations();
  }, []);

  const fetchConfigurations = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/journeys/configurations');
      if (response.ok) {
        const data = await response.json();
        setConfigurations(data.configurations || []);
      }
    } catch (error) {
      console.error('Error fetching configurations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPurpose = (journeyType: string) => {
    setSelectedPurpose(journeyType);
  };

  const handleContinue = () => {
    if (selectedPurpose) {
      localStorage.setItem('onboarding_journey_type', selectedPurpose);
      router.push('/onboarding/select-level');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-300">Loading journeys...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-12 px-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            What's your main goal with German?
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Choose your primary learning purpose. You can add more journeys later!
          </p>
        </div>

        {/* Journey Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {configurations.map((config) => (
            <button
              key={config.journey_type}
              onClick={() => handleSelectPurpose(config.journey_type)}
              className={`text-left p-6 rounded-2xl border-2 transition-all duration-200 transform hover:scale-105 ${
                selectedPurpose === config.journey_type
                  ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20 shadow-lg'
                  : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
            >
              <div className="flex items-start space-x-4">
                <div 
                  className="flex-shrink-0 w-16 h-16 rounded-xl flex items-center justify-center text-3xl"
                  style={{ backgroundColor: `${config.color}20` }}
                >
                  {config.icon}
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                    {config.display_name}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-3">
                    {config.description}
                  </p>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      Levels:
                    </span>
                    <div className="flex flex-wrap gap-1">
                      {config.level_system.levels.map((level) => (
                        <span
                          key={level}
                          className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
                        >
                          {level}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                {selectedPurpose === config.journey_type && (
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  </div>
                )}
              </div>
            </button>
          ))}
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <button
            onClick={() => router.push('/onboarding/welcome')}
            className="px-6 py-3 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            ← Back
          </button>
          <button
            onClick={handleContinue}
            disabled={!selectedPurpose}
            className={`px-8 py-3 rounded-xl font-semibold transition-all duration-200 ${
              selectedPurpose
                ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg transform hover:scale-105'
                : 'bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed'
            }`}
          >
            Continue →
          </button>
        </div>

        {/* Progress Indicator */}
        <div className="mt-8 flex justify-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-blue-600"></div>
          <div className="w-2 h-2 rounded-full bg-gray-300 dark:bg-gray-600"></div>
          <div className="w-2 h-2 rounded-full bg-gray-300 dark:bg-gray-600"></div>
        </div>
      </div>
    </div>
  );
}
