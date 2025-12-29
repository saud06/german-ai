'use client';

import { useLocation, useLocationActivities } from '@/hooks/useLearningPath';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeftIcon, MapPinIcon, ClockIcon, UsersIcon, PlayIcon, BookOpenIcon, PenToolIcon, FileTextIcon, GraduationCapIcon, MessageSquareIcon } from 'lucide-react';

export default function LocationDetailPage() {
  const params = useParams();
  const locationId = params.id as string;
  
  const { data: locationData, isLoading: locationLoading } = useLocation(locationId);
  const { data: activities, isLoading: activitiesLoading } = useLocationActivities(locationId);

  const isLoading = locationLoading || activitiesLoading;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading location...</p>
        </div>
      </div>
    );
  }

  if (!locationData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Location not found</p>
          <Link href="/learning-path" className="text-indigo-600 hover:underline mt-2 inline-block">
            ← Back to Learning Path
          </Link>
        </div>
      </div>
    );
  }

  const { location, is_unlocked, is_completed, completion_percent } = locationData;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Back Button */}
        <Link 
          href={`/learning-path/${location.chapter_id}/map`}
          className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-700 mb-6"
        >
          <ArrowLeftIcon className="w-4 h-4" />
          Back to Map
        </Link>

        {/* Location Header */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <MapPinIcon className="w-5 h-5 text-indigo-600" />
                <span className="text-gray-500 text-sm">{location.type}</span>
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{location.name}</h1>
              <p className="text-gray-600">{location.description}</p>
            </div>
            <div className="text-right">
              {is_completed ? (
                <div className="text-green-500 text-4xl">✅</div>
              ) : is_unlocked ? (
                <div className="text-indigo-500 text-4xl">📍</div>
              ) : (
                <div className="text-gray-400 text-4xl">🔒</div>
              )}
            </div>
          </div>

          {/* Progress */}
          {is_unlocked && (
            <div className="mb-4">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Progress</span>
                <span className="font-semibold">{completion_percent}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full rounded-full transition-all"
                  style={{ width: `${completion_percent}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* Info */}
          <div className="flex items-center gap-6 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <ClockIcon className="w-4 h-4" />
              <span>{location.estimated_minutes} minutes</span>
            </div>
            <div className="flex items-center gap-2">
              <UsersIcon className="w-4 h-4" />
              <span>{location.characters.length} characters</span>
            </div>
            <div className="flex items-center gap-2">
              <PlayIcon className="w-4 h-4" />
              <span>{location.scenarios.length} scenarios</span>
            </div>
          </div>
        </div>

        {/* Activities */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Learning Activities</h2>
          
          {!is_unlocked ? (
            <div className="text-center py-8">
              <div className="text-4xl mb-4">🔒</div>
              <p className="text-gray-600">Complete previous locations to unlock this area</p>
            </div>
          ) : activities && activities.length > 0 ? (
            <div className="space-y-3">
              {activities.map((activity) => {
                // Get icon and color based on activity type
                const getActivityIcon = (type: string) => {
                  switch (type) {
                    case 'scenario': return <MessageSquareIcon className="w-5 h-5" />;
                    case 'vocabulary': return <BookOpenIcon className="w-5 h-5" />;
                    case 'quiz': return <FileTextIcon className="w-5 h-5" />;
                    case 'grammar': return <GraduationCapIcon className="w-5 h-5" />;
                    case 'reading': return <BookOpenIcon className="w-5 h-5" />;
                    case 'writing': return <PenToolIcon className="w-5 h-5" />;
                    default: return <PlayIcon className="w-5 h-5" />;
                  }
                };

                const getActivityColor = (type: string) => {
                  switch (type) {
                    case 'scenario': return 'indigo';
                    case 'vocabulary': return 'blue';
                    case 'quiz': return 'purple';
                    case 'grammar': return 'green';
                    case 'reading': return 'orange';
                    case 'writing': return 'pink';
                    default: return 'gray';
                  }
                };

                const getActivityLink = (activity: any) => {
                  // Use unified activity page for all types
                  return `/activities/${activity.id}?type=${activity.type}`;
                };

                const color = getActivityColor(activity.type);
                const isCompleted = activity.completed;

                return (
                  <Link
                    key={activity.id}
                    href={getActivityLink(activity)}
                    className={`block border-2 rounded-lg p-4 hover:shadow-md transition-all ${
                      isCompleted 
                        ? 'border-green-200 bg-green-50' 
                        : `border-${color}-200 hover:border-${color}-400`
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3 flex-1">
                        <div className={`p-2 rounded-lg ${isCompleted ? 'bg-green-100 text-green-600' : `bg-${color}-100 text-${color}-600`}`}>
                          {getActivityIcon(activity.type)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold text-gray-900">{activity.name}</h3>
                            <span className={`text-xs px-2 py-0.5 rounded-full ${isCompleted ? 'bg-green-100 text-green-700' : `bg-${color}-100 text-${color}-700`}`}>
                              {activity.type}
                            </span>
                            {isCompleted && <span className="text-green-500">✓</span>}
                          </div>
                          <p className="text-sm text-gray-600 mb-2">{activity.description}</p>
                          <div className="flex items-center gap-4 text-xs text-gray-500">
                            <span>⏱️ {activity.estimated_minutes} min</span>
                            <span>⭐ {activity.xp_reward} XP</span>
                            <span className="capitalize">{activity.difficulty}</span>
                          </div>
                        </div>
                      </div>
                      <ArrowLeftIcon className={`w-5 h-5 rotate-180 flex-shrink-0 ${isCompleted ? 'text-green-600' : `text-${color}-600`}`} />
                    </div>
                  </Link>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>No activities available yet</p>
              <p className="text-sm mt-2">Check back soon for new content!</p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
