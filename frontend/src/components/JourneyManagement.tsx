'use client';

import { useState } from 'react';
import { useJourney } from '@/contexts/JourneyContext';
import type { Journey, JourneyConfiguration, JourneyType } from '@/contexts/JourneyContext';

export default function JourneyManagement() {
  const { activeJourney, allJourneys, configurations, switchJourney, addJourney, removeJourney, refreshJourneys } = useJourney();
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedType, setSelectedType] = useState<JourneyType | null>(null);
  const [selectedLevel, setSelectedLevel] = useState<string>('');
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const availableConfigs = configurations.filter(
    config => !allJourneys.some(j => j.type === config.journey_type)
  );

  const handleAddJourney = async () => {
    if (!selectedType || !selectedLevel) {
      setError('Please select a journey type and level');
      return;
    }

    setAdding(true);
    setError(null);

    try {
      await addJourney(selectedType, selectedLevel, false);
      setShowAddModal(false);
      setSelectedType(null);
      setSelectedLevel('');
      await refreshJourneys();
    } catch (err: any) {
      setError(err.message || 'Failed to add journey');
    } finally {
      setAdding(false);
    }
  };

  const handleRemoveJourney = async (journeyId: string) => {
    if (allJourneys.length === 1) {
      setError('You must have at least one active journey');
      setTimeout(() => setError(null), 3000);
      return;
    }

    if (!confirm('Are you sure you want to remove this journey? Your progress will be saved.')) {
      return;
    }

    try {
      await removeJourney(journeyId);
      await refreshJourneys();
    } catch (err: any) {
      setError(err.message || 'Failed to remove journey');
      setTimeout(() => setError(null), 3000);
    }
  };

  const handleSwitchJourney = async (journeyId: string) => {
    try {
      await switchJourney(journeyId);
      await refreshJourneys();
    } catch (err: any) {
      setError(err.message || 'Failed to switch journey');
      setTimeout(() => setError(null), 3000);
    }
  };

  const selectedConfig = selectedType 
    ? configurations.find(c => c.journey_type === selectedType)
    : null;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-medium">Learning Journeys</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Manage your active learning journeys
          </p>
        </div>
        {availableConfigs.length > 0 && (
          <button
            onClick={() => setShowAddModal(true)}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Journey
          </button>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-700 dark:text-red-400">
          {error}
        </div>
      )}

      {/* Journey Cards */}
      <div className="space-y-3">
        {allJourneys.map((journey) => {
          const config = journey.configuration;
          const isActive = activeJourney?.id === journey.id;

          return (
            <div
              key={journey.id}
              className={`p-4 rounded-lg border-2 transition-all ${
                isActive
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  {/* Journey Icon */}
                  <div
                    className="w-12 h-12 rounded-lg flex items-center justify-center text-2xl flex-shrink-0"
                    style={{ backgroundColor: `${config?.color}20` }}
                  >
                    {config?.icon}
                  </div>

                  {/* Journey Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <h3 className="font-semibold text-gray-900 dark:text-white">
                        {config?.display_name}
                      </h3>
                      {isActive && (
                        <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-xs font-medium rounded">
                          Active
                        </span>
                      )}
                      {journey.is_primary && (
                        <span className="px-2 py-0.5 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 text-xs font-medium rounded">
                          Primary
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      {config?.description}
                    </p>
                    <div className="flex items-center space-x-4 text-sm">
                      <div className="flex items-center space-x-1">
                        <span className="text-gray-500 dark:text-gray-400">Level:</span>
                        <span
                          className="font-semibold px-2 py-0.5 rounded"
                          style={{
                            backgroundColor: `${config?.color}20`,
                            color: config?.color
                          }}
                        >
                          {journey.level}
                        </span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <span className="text-gray-500 dark:text-gray-400">Progress:</span>
                        <span className="font-medium text-gray-700 dark:text-gray-300">
                          {journey.progress?.lessons_completed || 0} lessons
                        </span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <span className="text-gray-500 dark:text-gray-400">XP:</span>
                        <span className="font-medium text-gray-700 dark:text-gray-300">
                          {journey.progress?.total_xp || 0}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center space-x-2 ml-4">
                  {!isActive && (
                    <button
                      onClick={() => handleSwitchJourney(journey.id)}
                      className="px-3 py-1.5 text-sm font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
                    >
                      Switch
                    </button>
                  )}
                  {allJourneys.length > 1 && (
                    <button
                      onClick={() => handleRemoveJourney(journey.id)}
                      className="px-3 py-1.5 text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                    >
                      Remove
                    </button>
                  )}
                </div>
              </div>

              {/* Progress Bar */}
              {journey.progress && (
                <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
                    <span>Journey Progress</span>
                    <span>{Math.round(((journey.progress.lessons_completed || 0) / 50) * 100)}%</span>
                  </div>
                  <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all"
                      style={{
                        width: `${Math.min(100, ((journey.progress.lessons_completed || 0) / 50) * 100)}%`,
                        backgroundColor: config?.color
                      }}
                    />
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Add Journey Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              {/* Modal Header */}
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                  Add New Journey
                </h3>
                <button
                  onClick={() => {
                    setShowAddModal(false);
                    setSelectedType(null);
                    setSelectedLevel('');
                    setError(null);
                  }}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Journey Type Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Select Journey Type
                </label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {availableConfigs.map((config) => (
                    <button
                      key={config.journey_type}
                      onClick={() => {
                        setSelectedType(config.journey_type as JourneyType);
                        setSelectedLevel('');
                      }}
                      className={`p-4 rounded-lg border-2 text-left transition-all ${
                        selectedType === config.journey_type
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <div
                          className="w-10 h-10 rounded-lg flex items-center justify-center text-xl"
                          style={{ backgroundColor: `${config.color}20` }}
                        >
                          {config.icon}
                        </div>
                        <div>
                          <div className="font-semibold text-gray-900 dark:text-white">
                            {config.display_name}
                          </div>
                          <div className="text-xs text-gray-600 dark:text-gray-400">
                            {config.description}
                          </div>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Level Selection */}
              {selectedType && selectedConfig && (
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Select Starting Level
                  </label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {selectedConfig.level_system.levels.map((level) => (
                      <button
                        key={level}
                        onClick={() => setSelectedLevel(level)}
                        className={`p-3 rounded-lg border-2 text-center transition-all ${
                          selectedLevel === level
                            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                            : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                        }`}
                      >
                        <div className="font-semibold text-gray-900 dark:text-white">
                          {level}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Error in Modal */}
              {error && (
                <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-700 dark:text-red-400">
                  {error}
                </div>
              )}

              {/* Modal Actions */}
              <div className="flex items-center justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowAddModal(false);
                    setSelectedType(null);
                    setSelectedLevel('');
                    setError(null);
                  }}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddJourney}
                  disabled={!selectedType || !selectedLevel || adding}
                  className="px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {adding ? 'Adding...' : 'Add Journey'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Info Box */}
      <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
        <div className="flex items-start space-x-3">
          <svg className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div className="text-sm text-blue-800 dark:text-blue-200">
            <p className="font-medium mb-1">About Learning Journeys</p>
            <p>
              You can have multiple active journeys simultaneously. Switch between them anytime to focus on different learning goals. 
              Your progress is saved separately for each journey.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
