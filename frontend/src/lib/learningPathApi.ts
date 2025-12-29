/**
 * Learning Path API Client
 * Handles all API calls for the story-driven learning system
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface LearningPath {
  _id: string;
  chapter: number;
  level: string;
  title: string;
  description: string;
  story: string;
  image: string;
  locations: string[];
  characters: string[];
  estimated_hours: number;
  completion_reward: {
    xp: number;
    badge?: string;
    unlock?: string;
  };
}

export interface Location {
  _id: string;
  chapter_id: string;
  name: string;
  type: string;
  description: string;
  image: string;
  position: { x: number; y: number };
  scenarios: string[];
  characters: string[];
  estimated_minutes: number;
}

export interface Character {
  _id: string;
  name: string;
  role: string;
  personality: string;
  age: number;
  occupation: string;
  avatar: string;
  appears_in_chapters: number[];
  relationship_levels: Record<string, string>;
}

export interface ChapterProgress {
  started_at?: string;
  completed_at?: string;
  progress_percent: number;
  locations_completed: string[];
  scenarios_completed: string[];
  xp_earned: number;
  time_spent_minutes: number;
}

export interface CharacterRelationship {
  character_id: string;
  level: number;
  conversations: number;
  last_interaction?: string;
  unlocked_topics: string[];
}

export interface LifeStats {
  housing: string;
  job: string;
  friends: number;
  cities_visited: number;
  certifications: string[];
}

export interface ProgressSummary {
  current_chapter: number;
  current_location?: string;
  total_xp: number;
  level: number;
  chapters_completed: number;
  scenarios_completed: number;
  words_learned: number;
  conversations_held: number;
  daily_streak: number;
  life_stats: LifeStats;
  next_milestone?: string;
}

export interface RecommendedAction {
  type: string;
  title: string;
  description: string;
  estimated_minutes: number;
  xp_reward: number;
  priority: string;
  reason: string;
}

export interface DailyChallenge {
  id: string;
  title: string;
  description: string;
  type: string;
  target: number;
  progress: number;
  xp_reward: number;
  expires_at: string;
}

export interface LearningPathResponse {
  path: LearningPath;
  progress?: ChapterProgress;
  is_unlocked: boolean;
  is_completed: boolean;
}

export interface LocationResponse {
  location: Location;
  is_unlocked: boolean;
  is_completed: boolean;
  completion_percent: number;
}

export interface Activity {
  id: string;
  type: 'scenario' | 'vocabulary' | 'quiz' | 'grammar' | 'reading' | 'writing';
  name: string;
  description: string;
  xp_reward: number;
  estimated_minutes: number;
  icon: string;
  difficulty: string;
  completed: boolean;
}

export interface CharacterResponse {
  character: Character;
  relationship?: CharacterRelationship;
  available_topics: string[];
}

/**
 * Get authentication token from localStorage
 */
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('token');
}

/**
 * Make authenticated API request
 */
async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// ============================================================================
// LEARNING PATHS
// ============================================================================

export async function getAllLearningPaths(): Promise<LearningPathResponse[]> {
  return apiRequest('/learning-paths');
}

export async function getLearningPath(pathId: string): Promise<LearningPathResponse> {
  return apiRequest(`/learning-paths/${pathId}`);
}

// ============================================================================
// LOCATIONS
// ============================================================================

export async function getPathLocations(pathId: string): Promise<LocationResponse[]> {
  return apiRequest(`/learning-paths/${pathId}/locations`);
}

export async function getLocation(locationId: string): Promise<LocationResponse> {
  return apiRequest(`/learning-paths/locations/${locationId}`);
}

export async function getLocationActivities(locationId: string): Promise<Activity[]> {
  const response: any = await apiRequest(`/learning-paths/locations/${locationId}/activities`);
  return response.activities || [];
}

// ============================================================================
// CHARACTERS
// ============================================================================

export async function getAllCharacters(): Promise<CharacterResponse[]> {
  return apiRequest('/learning-paths/characters');
}

export async function getCharacter(characterId: string): Promise<CharacterResponse> {
  return apiRequest(`/learning-paths/characters/${characterId}`);
}

// ============================================================================
// PROGRESS
// ============================================================================

export async function getProgressSummary(): Promise<ProgressSummary> {
  return apiRequest('/learning-paths/progress/summary');
}

export async function getRecommendations(): Promise<RecommendedAction[]> {
  return apiRequest('/learning-paths/recommendations');
}

export async function getDailyChallenges(): Promise<DailyChallenge[]> {
  return apiRequest('/learning-paths/challenges/daily');
}

// ============================================================================
// UPDATES
// ============================================================================

export async function completeScenario(
  scenarioId: string,
  xpEarned: number
): Promise<{ success: boolean; xp_earned: number; chapter_progress: number }> {
  return apiRequest('/learning-paths/progress/scenario-complete', {
    method: 'POST',
    body: JSON.stringify({ scenario_id: scenarioId, xp_earned: xpEarned }),
  });
}

export async function recordCharacterInteraction(
  characterId: string
): Promise<{ success: boolean; relationship_level: number }> {
  return apiRequest('/learning-paths/progress/character-interaction', {
    method: 'POST',
    body: JSON.stringify({ character_id: characterId }),
  });
}

export async function updateLearningProfile(profile: {
  style?: string;
  pace?: string;
  strengths?: string[];
  weaknesses?: string[];
  interests?: string[];
  goals?: string[];
  preferred_time?: string;
  session_length?: number;
}): Promise<{ success: boolean }> {
  return apiRequest('/learning-paths/progress/update-profile', {
    method: 'POST',
    body: JSON.stringify(profile),
  });
}

/**
 * Mark an activity as complete in the learning path
 */
export async function completeActivity(
  activityId: string,
  activityType: 'vocabulary' | 'quiz' | 'grammar' | 'reading' | 'writing' | 'scenario',
  xpEarned: number = 50
): Promise<{ success: boolean; xp_earned: number; level_up?: boolean }> {
  return apiRequest('/learning-paths/progress/activity-complete', {
    method: 'POST',
    body: JSON.stringify({
      activity_id: activityId,
      activity_type: activityType,
      xp_earned: xpEarned,
    }),
  });
}
