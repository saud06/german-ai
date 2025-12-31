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
    if (!loading && !onboardingCompleted && !activeJourney) {
      router.push('/onboarding/welcome');
    }
  }, [loading, onboardingCompleted, activeJourney, router]);

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

  const config = activeJourney.configuration;

  return (
    <div className="space-y-6">
      {/* Journey-Specific Hero */}
      <section 
        className="rounded-xl border p-6 relative overflow-hidden"
        style={{
          background: `linear-gradient(135deg, ${config?.color}10 0%, ${config?.color}05 100%)`,
          borderColor: `${config?.color}40`
        }}
      >
        <div className="relative z-10">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center space-x-4">
              <div 
                className="w-16 h-16 rounded-xl flex items-center justify-center text-3xl"
                style={{ backgroundColor: `${config?.color}20` }}
              >
                {config?.icon}
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                  {config?.dashboard_config.hero_title}
                </h1>
                <p className="text-gray-600 dark:text-gray-300 mt-1">
                  {config?.dashboard_config.hero_subtitle}
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500 dark:text-gray-400">Your Level</div>
              <div 
                className="text-xl font-bold px-3 py-1 rounded-lg mt-1"
                style={{ 
                  backgroundColor: `${config?.color}20`,
                  color: config?.color
                }}
              >
                {activeJourney.level}
              </div>
            </div>
          </div>

          {/* Journey-Specific CTA */}
          <div className="flex flex-wrap gap-3 mt-6">
            <Link
              href={getJourneyPrimaryCTA(activeJourney.type)}
              className="inline-flex items-center px-6 py-3 rounded-xl font-semibold text-white transition-all hover:scale-105 shadow-lg"
              style={{ backgroundColor: config?.color }}
            >
              {config?.dashboard_config.primary_cta} →
            </Link>
            <Link
              href="/settings"
              className="inline-flex items-center px-6 py-3 rounded-xl font-semibold bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all"
            >
              Manage Journeys
            </Link>
          </div>
        </div>

        {/* Decorative Background Pattern */}
        <div 
          className="absolute top-0 right-0 w-64 h-64 opacity-5"
          style={{
            background: `radial-gradient(circle, ${config?.color} 0%, transparent 70%)`
          }}
        />
      </section>

      {/* Journey-Specific Sections */}
      <JourneySections journey={activeJourney} />

      {/* Original Dashboard Content */}
      {children}
    </div>
  );
}

function JourneySections({ journey }: { journey: any }) {
  const config = journey.configuration;
  
  if (!config) return null;

  return (
    <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {config.dashboard_config.sections
        .sort((a: any, b: any) => a.order - b.order)
        .slice(0, 6) // Show top 6 sections
        .map((section: any) => (
          <Link
            key={section.id}
            href={getSectionLink(section.id, journey.type)}
            className="group p-6 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600 transition-all hover:shadow-lg"
          >
            <div className="flex items-start justify-between mb-3">
              <div 
                className="w-12 h-12 rounded-lg flex items-center justify-center text-2xl"
                style={{ backgroundColor: `${config.color}15` }}
              >
                {getSectionIcon(section.id)}
              </div>
              <svg 
                className="w-5 h-5 text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300 transition-colors" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
              {section.title}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-300">
              {section.description}
            </p>
            <div className="mt-3 flex flex-wrap gap-1">
              {section.content_types.slice(0, 3).map((type: string) => (
                <span 
                  key={type}
                  className="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
                >
                  {type}
                </span>
              ))}
            </div>
          </Link>
        ))}
    </section>
  );
}

function getJourneyPrimaryCTA(journeyType: string): string {
  const ctas: Record<string, string> = {
    student: '/quiz',
    traveler: '/scenarios',
    professional: '/scenarios',
    hobby: '/vocab'
  };
  return ctas[journeyType] || '/quiz';
}

function getSectionLink(sectionId: string, journeyType: string): string {
  const links: Record<string, string> = {
    core_lessons: '/vocab',
    exam_practice: '/quiz',
    grammar_boosters: '/grammar',
    practice_scenarios: '/scenarios',
    progress_tracker: '/progress',
    essential_phrases: '/vocab',
    travel_scenarios: '/scenarios',
    culture_etiquette: '/vocab',
    pronunciation: '/speech',
    travel_readiness: '/progress',
    business_lessons: '/vocab',
    email_writing: '/writing',
    meetings_presentations: '/scenarios',
    job_interviews: '/scenarios',
    professional_culture: '/vocab',
    learn_through_media: '/reading',
    topics_you_like: '/vocab',
    light_practice: '/quiz',
    casual_conversations: '/scenarios',
    fun_stats: '/progress'
  };
  return links[sectionId] || '/dashboard';
}

function getSectionIcon(sectionId: string): string {
  const icons: Record<string, string> = {
    core_lessons: '📚',
    exam_practice: '✍️',
    grammar_boosters: '📖',
    practice_scenarios: '💬',
    progress_tracker: '📊',
    essential_phrases: '✈️',
    travel_scenarios: '🗺️',
    culture_etiquette: '🎭',
    pronunciation: '🎤',
    travel_readiness: '✅',
    business_lessons: '💼',
    email_writing: '📧',
    meetings_presentations: '👔',
    job_interviews: '🤝',
    professional_culture: '🏢',
    learn_through_media: '🎬',
    topics_you_like: '🎨',
    light_practice: '🎮',
    casual_conversations: '💭',
    fun_stats: '📈'
  };
  return icons[sectionId] || '📌';
}
