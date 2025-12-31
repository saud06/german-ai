'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface JourneyConfig {
  journey_type: string;
  display_name: string;
  icon: string;
  color: string;
  level_system: {
    type: string;
    levels: string[];
  };
}

export default function SelectLevel() {
  const router = useRouter();
  const [config, setConfig] = useState<JourneyConfig | null>(null);
  const [selectedLevel, setSelectedLevel] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    const journeyType = localStorage.getItem('onboarding_journey_type');
    if (!journeyType) {
      router.push('/onboarding/select-purpose');
      return;
    }
    fetchConfiguration(journeyType);
  }, []);

  const fetchConfiguration = async (journeyType: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/journeys/configurations');
      if (response.ok) {
        const data = await response.json();
        const foundConfig = data.configurations.find(
          (c: JourneyConfig) => c.journey_type === journeyType
        );
        setConfig(foundConfig);
      }
    } catch (error) {
      console.error('Error fetching configuration:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateJourney = async () => {
    if (!selectedLevel || !config) return;

    setCreating(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/journeys/select', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          journey_type: config.journey_type,
          level: selectedLevel,
          is_primary: true,
        }),
      });

      if (response.ok) {
        localStorage.removeItem('onboarding_journey_type');
        // Force refresh journey context before navigating
        window.location.href = '/onboarding/confirmation';
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to create journey');
      }
    } catch (error) {
      console.error('Error creating journey:', error);
      alert('Failed to create journey. Please try again.');
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-300">Loading...</p>
        </div>
      </div>
    );
  }

  if (!config) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 dark:text-red-400">Configuration not found</p>
          <button
            onClick={() => router.push('/onboarding/select-purpose')}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div 
            className="inline-block w-20 h-20 rounded-2xl flex items-center justify-center text-4xl mb-4"
            style={{ backgroundColor: `${config.color}20` }}
          >
            {config.icon}
          </div>
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Choose Your Starting Level
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            {config.display_name} • Select the level that best matches your current German skills
          </p>
        </div>

        {/* Level Cards */}
        <div className="grid grid-cols-1 gap-4 mb-8">
          {config.level_system.levels.map((level, index) => (
            <button
              key={level}
              onClick={() => setSelectedLevel(level)}
              className={`text-left p-6 rounded-xl border-2 transition-all duration-200 ${
                selectedLevel === level
                  ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20 shadow-lg'
                  : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div 
                    className="w-12 h-12 rounded-lg flex items-center justify-center font-bold text-lg"
                    style={{ 
                      backgroundColor: selectedLevel === level ? config.color : `${config.color}20`,
                      color: selectedLevel === level ? 'white' : config.color
                    }}
                  >
                    {level}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {level}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      {getLevelDescription(level, config.level_system.type)}
                    </p>
                  </div>
                </div>
                {selectedLevel === level && (
                  <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                )}
              </div>
            </button>
          ))}
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4 mb-8">
          <div className="flex items-start space-x-3">
            <span className="text-2xl">💡</span>
            <div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-1">
                Don't worry about being perfect!
              </h4>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                You can always adjust your level later as you progress. Choose what feels comfortable right now.
              </p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <button
            onClick={() => router.push('/onboarding/select-purpose')}
            className="px-6 py-3 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
            disabled={creating}
          >
            ← Back
          </button>
          <button
            onClick={handleCreateJourney}
            disabled={!selectedLevel || creating}
            className={`px-8 py-3 rounded-xl font-semibold transition-all duration-200 ${
              selectedLevel && !creating
                ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg transform hover:scale-105'
                : 'bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed'
            }`}
          >
            {creating ? 'Creating Journey...' : 'Create My Journey →'}
          </button>
        </div>

        {/* Progress Indicator */}
        <div className="mt-8 flex justify-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-blue-600"></div>
          <div className="w-2 h-2 rounded-full bg-blue-600"></div>
          <div className="w-2 h-2 rounded-full bg-gray-300 dark:bg-gray-600"></div>
        </div>
      </div>
    </div>
  );
}

function getLevelDescription(level: string, systemType: string): string {
  if (systemType === 'cefr') {
    const descriptions: Record<string, string> = {
      'A1': 'Complete beginner - Basic phrases and simple sentences',
      'A2': 'Elementary - Everyday expressions and simple conversations',
      'B1': 'Intermediate - Handle most situations while traveling',
      'B2': 'Upper intermediate - Understand complex texts and speak fluently',
      'C1': 'Advanced - Express yourself fluently and spontaneously',
    };
    return descriptions[level] || 'Select this level';
  } else {
    const descriptions: Record<string, string> = {
      'Beginner': 'Just starting out with German',
      'Intermediate': 'Can handle basic conversations',
      'Advanced': 'Comfortable with complex topics',
    };
    return descriptions[level] || 'Select this level';
  }
}
