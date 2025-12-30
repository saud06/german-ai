'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

interface Character {
  id: string;
  name: string;
  role: string;
  personality: string;
  description: string;
}

interface Objective {
  id: string;
  description: string;
  required: boolean;
  completed: boolean;
}

interface Scenario {
  _id: string;
  name: string;
  title_en: string;
  description: string;
  description_en: string;
  difficulty: string;
  category: string;
  estimated_duration: number;
  icon: string;
  characters: Character[];
  objectives: Objective[];
  xp_reward?: number;
  bonus_xp?: number;
}

interface UserProgress {
  completed: boolean;
  attempts: number;
  best_score: number;
  current_active: boolean;
}

export default function ScenariosPage() {
  const router = useRouter();
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState<string>('all');
  const [userProgress, setUserProgress] = useState<Record<string, UserProgress>>({});

  const formatText = (text: string) => {
    return text.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase());
  };

  useEffect(() => {
    fetchScenarios();
    fetchUserProgress();
  }, []);

  const fetchScenarios = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
        return;
      }

      const response = await fetch('http://localhost:8000/api/v1/scenarios/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch scenarios');
      }

      const data = await response.json();
      setScenarios(data.scenarios);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load scenarios');
    } finally {
      setLoading(false);
    }
  };

  const fetchUserProgress = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch('http://localhost:8000/api/v1/scenarios/progress', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUserProgress(data.progress || {});
      }
    } catch (err) {
    }
  };

  const filteredScenarios = scenarios.filter(s => 
    filter === 'all' || s.difficulty === filter
  );

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'restaurant': return '🍽️';
      case 'hotel': return '🏨';
      case 'shopping': return '🛒';
      case 'doctor': return '🏥';
      case 'transport': return '🚌';
      default: return '🎭';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading scenarios...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/dashboard')}
            className="mb-4 text-indigo-600 hover:text-indigo-800 flex items-center"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            🎭 Life Simulation
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Practice German in real-world scenarios
          </p>
        </div>

        {/* Filter */}
        <div className="mb-6 flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              filter === 'all'
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('beginner')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              filter === 'beginner'
                ? 'bg-green-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            Beginner
          </button>
          <button
            onClick={() => setFilter('intermediate')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              filter === 'intermediate'
                ? 'bg-yellow-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            Intermediate
          </button>
          <button
            onClick={() => setFilter('advanced')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              filter === 'advanced'
                ? 'bg-red-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            Advanced
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Scenarios Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredScenarios.map((scenario) => (
            <div
              key={scenario._id}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow cursor-pointer"
              onClick={() => router.push(`/scenarios/${scenario._id}`)}
            >
              {/* Card Header */}
              <div className="bg-gradient-to-r from-indigo-500 to-purple-600 p-6 text-white relative">
                {userProgress[scenario._id]?.completed && (
                  <div className="absolute top-4 right-4 bg-green-500 text-white px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1">
                    ✓ Completed
                  </div>
                )}
                <div className="text-5xl mb-2">{getCategoryIcon(scenario.category)}</div>
                <h3 className="text-2xl font-bold mb-1">{scenario.name}</h3>
                <p className="text-indigo-100 text-sm">{scenario.title_en}</p>
              </div>

              {/* Card Body */}
              <div className="p-6">
                <p className="text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
                  {scenario.description_en}
                </p>

                {/* Meta Info */}
                <div className="flex items-center gap-2 mb-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getDifficultyColor(scenario.difficulty)}`}>
                    {scenario.difficulty.charAt(0).toUpperCase() + scenario.difficulty.slice(1)}
                  </span>
                  <span className="text-gray-500 dark:text-gray-400 text-sm">
                    ⏱️ {scenario.estimated_duration} min
                  </span>
                </div>

                {/* Character */}
                {scenario.characters[0] && (
                  <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      👤 {scenario.characters[0].name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {formatText(scenario.characters[0].role)} • {formatText(scenario.characters[0].personality)}
                    </p>
                  </div>
                )}

                {/* Objectives Count & XP */}
                <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400 mb-4">
                  <span>📋 {scenario.objectives.length} objectives</span>
                  {scenario.xp_reward && (
                    <span className="text-indigo-600 dark:text-indigo-400 font-bold">
                      ⭐ +{scenario.xp_reward} XP
                    </span>
                  )}
                </div>

                {/* Action Button */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    router.push(`/scenarios/${scenario._id}`);
                  }}
                  className="w-full bg-indigo-600 text-white py-3 rounded-lg font-medium hover:bg-indigo-700 transition"
                >
                  Start Scenario →
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {filteredScenarios.length === 0 && !loading && (
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-400 text-lg">No scenarios found for this difficulty level.</p>
          </div>
        )}
      </div>
    </div>
  );
}
