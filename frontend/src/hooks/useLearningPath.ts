/**
 * React hooks for Learning Path system
 */
import { useState, useEffect, useCallback } from 'react';
import * as api from '@/lib/learningPathApi';

// ============================================================================
// LEARNING PATHS
// ============================================================================

export function useLearningPaths(journeyLevel?: string) {
  const [data, setData] = useState<api.LearningPathResponse[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    api.getAllLearningPaths(journeyLevel)
      .then(setData)
      .catch(setError)
      .finally(() => setIsLoading(false));
  }, [journeyLevel]);

  return { data, isLoading, error, refetch: () => window.location.reload() };
}

export function useLearningPath(pathId: string) {
  const [data, setData] = useState<api.LearningPathResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!pathId) return;
    
    api.getLearningPath(pathId)
      .then(setData)
      .catch(setError)
      .finally(() => setIsLoading(false));
  }, [pathId]);

  return { data, isLoading, error };
}

// ============================================================================
// LOCATIONS
// ============================================================================

export function usePathLocations(pathId: string) {
  const [data, setData] = useState<api.LocationResponse[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!pathId) return;
    
    api.getPathLocations(pathId)
      .then(setData)
      .catch(setError)
      .finally(() => setIsLoading(false));
  }, [pathId]);

  return { data, isLoading, error };
}

export function useLocation(locationId: string) {
  const [data, setData] = useState<api.LocationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!locationId) return;
    
    api.getLocation(locationId)
      .then(setData)
      .catch(setError)
      .finally(() => setIsLoading(false));
  }, [locationId]);

  return { data, isLoading, error };
}

export function useLocationActivities(locationId: string) {
  const [data, setData] = useState<api.Activity[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!locationId) return;
    
    api.getLocationActivities(locationId)
      .then(setData)
      .catch(setError)
      .finally(() => setIsLoading(false));
  }, [locationId]);

  return { data, isLoading, error };
}

// ============================================================================
// CHARACTERS
// ============================================================================

export function useCharacters() {
  const [data, setData] = useState<api.CharacterResponse[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    api.getAllCharacters()
      .then(setData)
      .catch(setError)
      .finally(() => setIsLoading(false));
  }, []);

  return { data, isLoading, error };
}

export function useCharacter(characterId: string) {
  const [data, setData] = useState<api.CharacterResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!characterId) return;
    
    api.getCharacter(characterId)
      .then(setData)
      .catch(setError)
      .finally(() => setIsLoading(false));
  }, [characterId]);

  return { data, isLoading, error };
}

// ============================================================================
// PROGRESS
// ============================================================================

export function useProgressSummary() {
  const [data, setData] = useState<api.ProgressSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const refetch = useCallback(() => {
    setIsLoading(true);
    api.getProgressSummary()
      .then(setData)
      .catch(setError)
      .finally(() => setIsLoading(false));
  }, []);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { data, isLoading, error, refetch };
}

export function useRecommendations(journeyLevel?: string) {
  const [data, setData] = useState<api.RecommendedAction[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    api.getRecommendations(journeyLevel)
      .then(setData)
      .catch(setError)
      .finally(() => setIsLoading(false));
  }, [journeyLevel]);

  return { data, isLoading, error };
}

export function useDailyChallenges(journeyLevel?: string) {
  const [data, setData] = useState<api.DailyChallenge[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    api.getDailyChallenges(journeyLevel)
      .then(setData)
      .catch(setError)
      .finally(() => setIsLoading(false));
  }, [journeyLevel]);

  return { data, isLoading, error };
}
