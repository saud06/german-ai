import { Journey } from '@/contexts/JourneyContext';

/**
 * Get the available levels for the active journey
 * Returns CEFR levels for student journey, difficulty levels for others
 */
export function getJourneyLevels(journey: Journey | null): string[] {
  if (!journey?.configuration?.level_system) {
    return ['Beginner', 'Intermediate', 'Advanced'];
  }
  return journey.configuration.level_system.levels;
}

/**
 * Get the level system type (cefr or difficulty)
 */
export function getLevelSystemType(journey: Journey | null): 'cefr' | 'difficulty' {
  if (!journey?.configuration?.level_system) {
    return 'difficulty';
  }
  return journey.configuration.level_system.type;
}

/**
 * Map any level to the journey's level system
 * E.g., "beginner" -> "A1" for CEFR, or "a1" -> "Beginner" for difficulty
 */
export function mapToJourneyLevel(level: string, journey: Journey | null): string {
  const systemType = getLevelSystemType(journey);
  const normalized = level.toLowerCase();

  if (systemType === 'cefr') {
    // Map difficulty to CEFR
    if (normalized === 'beginner') return 'A1';
    if (normalized === 'intermediate') return 'B1';
    if (normalized === 'advanced') return 'C1';
    // Already CEFR
    if (['a1', 'a2', 'b1', 'b2', 'c1'].includes(normalized)) {
      return level.toUpperCase();
    }
  } else {
    // Map CEFR to difficulty
    if (['a1', 'a2'].includes(normalized)) return 'Beginner';
    if (['b1', 'b2'].includes(normalized)) return 'Intermediate';
    if (['c1', 'c2'].includes(normalized)) return 'Advanced';
    // Already difficulty
    if (['beginner', 'intermediate', 'advanced'].includes(normalized)) {
      return level.charAt(0).toUpperCase() + level.slice(1).toLowerCase();
    }
  }

  return level;
}

/**
 * Get display name for a level
 */
export function getLevelDisplayName(level: string, journey: Journey | null): string {
  const systemType = getLevelSystemType(journey);
  
  if (systemType === 'cefr') {
    const descriptions: Record<string, string> = {
      'A1': 'A1 - Beginner',
      'A2': 'A2 - Elementary',
      'B1': 'B1 - Intermediate',
      'B2': 'B2 - Upper Intermediate',
      'C1': 'C1 - Advanced',
    };
    return descriptions[level.toUpperCase()] || level;
  } else {
    return level.charAt(0).toUpperCase() + level.slice(1).toLowerCase();
  }
}

/**
 * Get color classes for a level badge
 */
export function getLevelColor(level: string | undefined, journey: Journey | null): string {
  if (!level) return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300';
  const systemType = getLevelSystemType(journey);
  const normalized = level.toLowerCase();

  if (systemType === 'cefr') {
    if (['a1', 'a2'].includes(normalized)) return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
    if (['b1', 'b2'].includes(normalized)) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300';
    if (['c1', 'c2'].includes(normalized)) return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
  } else {
    if (normalized === 'beginner') return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
    if (normalized === 'intermediate') return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300';
    if (normalized === 'advanced') return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
  }

  return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300';
}

/**
 * Get icon for a level
 */
export function getLevelIcon(level: string, journey: Journey | null): string {
  const systemType = getLevelSystemType(journey);
  const normalized = level.toLowerCase();

  if (systemType === 'cefr') {
    const icons: Record<string, string> = {
      'a1': '🌱',
      'a2': '🌿',
      'b1': '🌳',
      'b2': '🎯',
      'c1': '🏆',
    };
    return icons[normalized] || '📚';
  } else {
    const icons: Record<string, string> = {
      'beginner': '🌱',
      'intermediate': '🎯',
      'advanced': '🏆',
    };
    return icons[normalized] || '📚';
  }
}

/**
 * Get filter button color for level filters
 */
export function getLevelFilterColor(level: string, journey: Journey | null, isActive: boolean): string {
  const systemType = getLevelSystemType(journey);
  const normalized = level.toLowerCase();

  if (isActive) {
    if (systemType === 'cefr') {
      if (['a1', 'a2'].includes(normalized)) return 'bg-green-600 text-white';
      if (['b1', 'b2'].includes(normalized)) return 'bg-yellow-600 text-white';
      if (['c1', 'c2'].includes(normalized)) return 'bg-red-600 text-white';
    } else {
      if (normalized === 'beginner') return 'bg-green-600 text-white';
      if (normalized === 'intermediate') return 'bg-yellow-600 text-white';
      if (normalized === 'advanced') return 'bg-red-600 text-white';
    }
  }

  return 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700';
}
