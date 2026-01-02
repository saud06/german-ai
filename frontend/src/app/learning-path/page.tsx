'use client';

import { useLearningPaths, useProgressSummary, useRecommendations, useDailyChallenges } from '@/hooks/useLearningPath';
import { useJourney } from '@/contexts/JourneyContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { MapIcon, TrophyIcon, FlameIcon, MessageCircleIcon, BookOpenIcon, UsersIcon, TargetIcon } from 'lucide-react';

export default function LearningPathPage() {
  const router = useRouter();
  const { activeJourney } = useJourney();
  
  // For Student journey, filter by their level (B1)
  // For other journeys, show all levels
  const journeyLevel = activeJourney?.type === 'student' ? activeJourney.level : undefined;
  
  const { data: paths, isLoading: pathsLoading } = useLearningPaths(journeyLevel);
  const { data: progress, isLoading: progressLoading } = useProgressSummary();
  const { data: recommendations } = useRecommendations(journeyLevel);
  const { data: challenges } = useDailyChallenges(journeyLevel);

  if (pathsLoading || progressLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading your journey...</p>
        </div>
      </div>
    );
  }

  const currentPath = paths?.find(p => p.path.chapter === progress?.current_chapter);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/dashboard')}
            className="mb-4 text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300 flex items-center"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            🗺️ Your German Journey
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Learn German by living a virtual life in Germany
          </p>
          {activeJourney && (
            <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Current Journey:</span>
              <span className="text-sm font-bold text-indigo-600 dark:text-indigo-400">
                {activeJourney.type.charAt(0).toUpperCase() + activeJourney.type.slice(1)} • {activeJourney.level.toUpperCase()}
              </span>
            </div>
          )}
        </div>

        {/* Current Chapter Card */}
        {currentPath && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-8 border-2 border-indigo-200 dark:border-indigo-800">
            <div className="flex items-start justify-between mb-6">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-semibold">
                    {currentPath.path.level}
                  </span>
                  <span className="text-gray-500">Chapter {currentPath.path.chapter}</span>
                </div>
                <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">{currentPath.path.title}</h2>
                <p className="text-gray-600 dark:text-gray-400">{currentPath.path.description}</p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">
                  {currentPath.progress?.progress_percent || 0}%
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">Complete</div>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="mb-6">
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 overflow-hidden">
                <div 
                  className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${currentPath.progress?.progress_percent || 0}%` }}
                ></div>
              </div>
            </div>

            {/* Story */}
            <div className="bg-indigo-50 dark:bg-indigo-900/20 rounded-lg p-4 mb-6">
              <p className="text-gray-700 dark:text-gray-300 italic">{currentPath.path.story}</p>
            </div>

            {/* Action Button */}
            <Link 
              href={`/learning-path/${currentPath.path._id}/map`}
              className="inline-flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-semibold"
            >
              <MapIcon className="w-5 h-5" />
              Continue Learning →
            </Link>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          
          {/* Stats Card */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <TrophyIcon className="w-5 h-5 text-yellow-500" />
              Your Stats
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">XP</span>
                <span className="font-bold text-indigo-600 dark:text-indigo-400">{progress?.total_xp || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400 flex items-center gap-1">
                  <FlameIcon className="w-4 h-4 text-orange-500" />
                  Streak
                </span>
                <span className="font-bold text-orange-600 dark:text-orange-400">{progress?.daily_streak || 0} days</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400 flex items-center gap-1">
                  <MessageCircleIcon className="w-4 h-4 text-blue-500" />
                  Conversations
                </span>
                <span className="font-bold text-gray-900 dark:text-white">{progress?.conversations_held || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400 flex items-center gap-1">
                  <BookOpenIcon className="w-4 h-4 text-green-500" />
                  Words Learned
                </span>
                <span className="font-bold text-gray-900 dark:text-white">{progress?.words_learned || 0}</span>
              </div>
            </div>
          </div>

          {/* Life Stats Card */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <UsersIcon className="w-5 h-5 text-purple-500" />
              Your Life in Germany
            </h3>
            <div className="space-y-3">
              <div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Housing</div>
                <div className="font-semibold text-gray-900 dark:text-white capitalize">
                  🏨 {progress?.life_stats.housing || 'Hotel'}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Job</div>
                <div className="font-semibold text-gray-900 dark:text-white capitalize">
                  💼 {progress?.life_stats.job || 'Unemployed'}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Friends</div>
                <div className="font-semibold text-gray-900 dark:text-white">
                  👥 {progress?.life_stats.friends || 0} friends
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Cities Visited</div>
                <div className="font-semibold text-gray-900 dark:text-white">
                  🌍 {progress?.life_stats.cities_visited || 1} cities
                </div>
              </div>
            </div>
          </div>

          {/* Recommendations Card */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <TargetIcon className="w-5 h-5 text-indigo-500" />
              Recommended
            </h3>
            <div className="space-y-3">
              {recommendations?.slice(0, 3).map((rec, idx) => (
                <div key={idx} className="border-l-4 border-indigo-500 dark:border-indigo-400 pl-3 py-2">
                  <div className="font-semibold text-sm text-gray-900 dark:text-white">{rec.title}</div>
                  <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">{rec.description}</div>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-xs text-gray-500 dark:text-gray-400">⏱️ {rec.estimated_minutes} min</span>
                    <span className="text-xs text-indigo-600 dark:text-indigo-400 font-semibold">+{rec.xp_reward} XP</span>
                  </div>
                </div>
              ))}
              {(!recommendations || recommendations.length === 0) && (
                <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                  Complete more scenarios to get recommendations!
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Daily Challenges */}
        {challenges && challenges.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">🎯 Today's Challenges</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {challenges.map((challenge) => (
                <div key={challenge.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="font-semibold text-gray-900 dark:text-white">{challenge.title}</div>
                    <div className="text-sm font-bold text-indigo-600 dark:text-indigo-400">+{challenge.xp_reward} XP</div>
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400 mb-3">{challenge.description}</div>
                  <div className="mb-2">
                    <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
                      <span>{challenge.progress} / {challenge.target}</span>
                      <span>{Math.round((challenge.progress / challenge.target) * 100)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-indigo-600 h-2 rounded-full transition-all"
                        style={{ width: `${Math.min((challenge.progress / challenge.target) * 100, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* All Chapters */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">All Chapters</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {paths?.map((pathData) => {
              const { path, progress: pathProgress, is_unlocked, is_completed } = pathData;
              
              return (
                <Link
                  key={path._id}
                  href={is_unlocked ? `/learning-path/${path._id}/map` : '#'}
                  className={`border-2 rounded-lg p-4 transition-all ${
                    is_unlocked 
                      ? 'border-indigo-200 dark:border-indigo-800 hover:border-indigo-400 dark:hover:border-indigo-600 hover:shadow-md cursor-pointer bg-white dark:bg-gray-800' 
                      : 'border-gray-200 dark:border-gray-700 opacity-50 cursor-not-allowed bg-gray-50 dark:bg-gray-900'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <span className="px-2 py-1 bg-indigo-100 text-indigo-700 rounded text-xs font-semibold">
                        {path.level}
                      </span>
                    </div>
                    <div className="text-right">
                      {is_completed && <span className="text-green-500">✅</span>}
                      {!is_unlocked && <span className="text-gray-400">🔒</span>}
                    </div>
                  </div>
                  <h4 className="font-bold text-gray-900 dark:text-white mb-1">Chapter {path.chapter}: {path.title}</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{path.description}</p>
                  {is_unlocked && (
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-indigo-600 h-2 rounded-full"
                        style={{ width: `${pathProgress?.progress_percent || 0}%` }}
                      ></div>
                    </div>
                  )}
                  <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                    ⏱️ {path.estimated_hours} hours
                  </div>
                </Link>
              );
            })}
          </div>
        </div>

      </div>
    </div>
  );
}
