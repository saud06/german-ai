'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export type JourneyType = 'student' | 'traveler' | 'professional' | 'hobby';

export interface JourneyProgress {
  lessons_completed: number;
  scenarios_completed: number;
  quizzes_completed: number;
  total_xp: number;
  current_streak: number;
  milestones: Array<{
    id: string;
    completed: boolean;
    completed_at?: Date;
  }>;
}

export interface Journey {
  id: string;
  type: JourneyType;
  is_primary: boolean;
  level: string;
  created_at: Date;
  last_accessed: Date;
  progress: JourneyProgress;
  configuration?: JourneyConfiguration;
}

export interface LevelSystem {
  type: 'cefr' | 'difficulty';
  levels: string[];
}

export interface DashboardSection {
  id: string;
  title: string;
  description: string;
  content_types: string[];
  order: number;
}

export interface DashboardConfig {
  hero_title: string;
  hero_subtitle: string;
  primary_cta: string;
  sections: DashboardSection[];
}

export interface JourneyMilestone {
  id: string;
  title: string;
  description: string;
  criteria: Record<string, any>;
}

export interface JourneyConfiguration {
  journey_type: JourneyType;
  display_name: string;
  description: string;
  icon: string;
  color: string;
  level_system: LevelSystem;
  dashboard_config: DashboardConfig;
  milestones: JourneyMilestone[];
}

interface JourneyContextType {
  activeJourney: Journey | null;
  allJourneys: Journey[];
  configurations: JourneyConfiguration[];
  loading: boolean;
  onboardingCompleted: boolean;
  switchJourney: (journeyId: string) => Promise<void>;
  addJourney: (type: JourneyType, level: string, isPrimary?: boolean) => Promise<void>;
  removeJourney: (journeyId: string) => Promise<void>;
  refreshJourneys: () => Promise<void>;
}

const JourneyContext = createContext<JourneyContextType | undefined>(undefined);

export function JourneyProvider({ children }: { children: ReactNode }) {
  const [activeJourney, setActiveJourney] = useState<Journey | null>(null);
  const [allJourneys, setAllJourneys] = useState<Journey[]>([]);
  const [configurations, setConfigurations] = useState<JourneyConfiguration[]>([]);
  const [loading, setLoading] = useState(true);
  const [onboardingCompleted, setOnboardingCompleted] = useState(false);

  const fetchJourneys = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setLoading(false);
        return;
      }

      const response = await fetch('http://localhost:8000/api/v1/journeys/my-journeys', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAllJourneys(data.journeys || []);
        setOnboardingCompleted(data.onboarding_completed || false);

        const active = data.journeys?.find(
          (j: Journey) => j.id === data.active_journey_id
        );
        setActiveJourney(active || null);
      }
    } catch (error) {
      console.error('Error fetching journeys:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchConfigurations = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/journeys/configurations');
      if (response.ok) {
        const data = await response.json();
        setConfigurations(data.configurations || []);
      }
    } catch (error) {
      console.error('Error fetching configurations:', error);
    }
  };

  useEffect(() => {
    fetchJourneys();
    fetchConfigurations();
  }, []);

  const switchJourney = async (journeyId: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/journeys/switch', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ journey_id: journeyId }),
      });

      if (response.ok) {
        await fetchJourneys();
      }
    } catch (error) {
      console.error('Error switching journey:', error);
      throw error;
    }
  };

  const addJourney = async (type: JourneyType, level: string, isPrimary: boolean = false) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/journeys/select', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          journey_type: type,
          level,
          is_primary: isPrimary,
        }),
      });

      if (response.ok) {
        await fetchJourneys();
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to add journey');
      }
    } catch (error) {
      console.error('Error adding journey:', error);
      throw error;
    }
  };

  const removeJourney = async (journeyId: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/journeys/${journeyId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        await fetchJourneys();
      }
    } catch (error) {
      console.error('Error removing journey:', error);
      throw error;
    }
  };

  const refreshJourneys = async () => {
    await fetchJourneys();
  };

  return (
    <JourneyContext.Provider
      value={{
        activeJourney,
        allJourneys,
        configurations,
        loading,
        onboardingCompleted,
        switchJourney,
        addJourney,
        removeJourney,
        refreshJourneys,
      }}
    >
      {children}
    </JourneyContext.Provider>
  );
}

export function useJourney() {
  const context = useContext(JourneyContext);
  if (context === undefined) {
    throw new Error('useJourney must be used within a JourneyProvider');
  }
  return context;
}
