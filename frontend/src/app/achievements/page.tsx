"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface Achievement {
  achievement: {
    code: string;
    name: string;
    description: string;
    icon: string;
    category: string;
    tier: string;
    xp_reward: number;
  };
  unlocked: boolean;
  progress: number;
  unlocked_at?: string;
}

interface UserStats {
  total_xp: number;
  level: number;
  xp_to_next_level: number;
  current_streak: number;
  longest_streak: number;
  scenarios_completed: number;
  words_learned: number;
  quizzes_completed: number;
  quiz_accuracy: number;
}

interface LeaderboardEntry {
  user_id: string;
  total_xp: number;
  level: number;
  current_streak: number;
}

export default function AchievementsPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  
  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    if (!storedToken) {
      router.push("/login");
      return;
    }
    setToken(storedToken);
  }, [router]);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [userRank, setUserRank] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<"achievements" | "stats" | "leaderboard">("achievements");
  const [filterCategory, setFilterCategory] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      fetchData();
    }
  }, [token]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      const statsRes = await fetch("http://localhost:8000/api/v1/achievements/stats", {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
      }

      const achievementsRes = await fetch("http://localhost:8000/api/v1/achievements/list", {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (achievementsRes.ok) {
        const achievementsData = await achievementsRes.json();
        setAchievements(achievementsData.achievements || []);
      }

      const leaderboardRes = await fetch("http://localhost:8000/api/v1/achievements/leaderboard/xp", {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (leaderboardRes.ok) {
        const leaderboardData = await leaderboardRes.json();
        setLeaderboard(leaderboardData.leaderboard || []);
        setUserRank(leaderboardData.user_rank);
      }
    } catch (error) {
      console.error('Error fetching achievements data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTierColor = (tier: string) => {
    const colors: Record<string, string> = {
      bronze: "text-amber-600",
      silver: "text-gray-400",
      gold: "text-yellow-500",
      platinum: "text-cyan-400",
      diamond: "text-purple-500"
    };
    return colors[tier] || "text-gray-500";
  };

  const getTierBg = (tier: string) => {
    const colors: Record<string, string> = {
      bronze: "bg-amber-100 border-amber-300",
      silver: "bg-gray-100 border-gray-300",
      gold: "bg-yellow-100 border-yellow-300",
      platinum: "bg-cyan-100 border-cyan-300",
      diamond: "bg-purple-100 border-purple-300"
    };
    return colors[tier] || "bg-gray-100 border-gray-300";
  };

  const filteredAchievements = achievements.filter(a => 
    filterCategory === "all" || a.achievement.category === filterCategory
  );

  const categories = ["all", "scenarios", "vocabulary", "grammar", "quiz", "streak", "special"];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-300">Loading achievements...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">🏆 Achievements & Progress</h1>
          <p className="text-gray-600 dark:text-gray-300">Track your learning journey and unlock rewards!</p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {/* Level Card */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border-2 border-indigo-200 dark:border-indigo-700">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-600 dark:text-gray-300 font-medium">Level</span>
                <span className="text-3xl">⭐</span>
              </div>
              <div className="text-4xl font-bold text-indigo-600 dark:text-indigo-400 mb-2">{stats.level}</div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-2">
                <div 
                  className="bg-indigo-600 h-2 rounded-full transition-all"
                  style={{ width: `${((stats.total_xp % stats.xp_to_next_level) / stats.xp_to_next_level) * 100}%` }}
                ></div>
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400">{stats.total_xp} XP / {stats.xp_to_next_level} to next level</p>
            </div>

            {/* Streak Card */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border-2 border-orange-200 dark:border-orange-700">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-600 dark:text-gray-300 font-medium">Streak</span>
                <span className="text-3xl">🔥</span>
              </div>
              <div className="text-4xl font-bold text-orange-600 dark:text-orange-400 mb-2">{stats.current_streak}</div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Longest: {stats.longest_streak} days</p>
            </div>

            {/* Scenarios Card */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border-2 border-cyan-200 dark:border-cyan-700">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-600 dark:text-gray-300 font-medium">Scenarios</span>
                <span className="text-3xl">🎭</span>
              </div>
              <div className="text-4xl font-bold text-cyan-600 dark:text-cyan-400 mb-2">{stats.scenarios_completed}</div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Completed</p>
            </div>

            {/* Words Card */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border-2 border-emerald-200 dark:border-emerald-700">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-600 dark:text-gray-300 font-medium">Words</span>
                <span className="text-3xl">📚</span>
              </div>
              <div className="text-4xl font-bold text-emerald-600 dark:text-emerald-400 mb-2">{stats.words_learned}</div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Learned</p>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg mb-8">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <div className="flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab("achievements")}
                className={`py-4 px-2 border-b-2 font-medium transition-colors ${
                  activeTab === "achievements"
                    ? "border-indigo-600 text-indigo-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                🏆 Achievements
              </button>
              <button
                onClick={() => setActiveTab("stats")}
                className={`py-4 px-2 border-b-2 font-medium transition-colors ${
                  activeTab === "stats"
                    ? "border-indigo-600 text-indigo-600"
                    : "border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
                }`}
              >
                📊 Statistics
              </button>
              <button
                onClick={() => setActiveTab("leaderboard")}
                className={`py-4 px-2 border-b-2 font-medium transition-colors ${
                  activeTab === "leaderboard"
                    ? "border-indigo-600 text-indigo-600"
                    : "border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
                }`}
              >
                👑 Leaderboard
              </button>
            </div>
          </div>

          <div className="p-6">
            {/* Achievements Tab */}
            {activeTab === "achievements" && (
              <div>
                {/* Category Filter */}
                <div className="flex flex-wrap gap-2 mb-6">
                  {categories.map(cat => (
                    <button
                      key={cat}
                      onClick={() => setFilterCategory(cat)}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        filterCategory === cat
                          ? "bg-indigo-600 text-white"
                          : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
                      }`}
                    >
                      {cat.charAt(0).toUpperCase() + cat.slice(1)}
                    </button>
                  ))}
                </div>

                {/* Achievements Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredAchievements.map((achievement) => (
                    <div
                      key={achievement.achievement.code}
                      className={`rounded-lg border-2 p-4 transition-all ${
                        achievement.unlocked
                          ? `${getTierBg(achievement.achievement.tier)} shadow-md`
                          : "bg-gray-100 dark:bg-gray-800 border-gray-300 dark:border-gray-600 opacity-70"
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <span className="text-4xl">{achievement.achievement.icon}</span>
                        <span className={`text-xs font-bold uppercase ${getTierColor(achievement.achievement.tier)}`}>
                          {achievement.achievement.tier}
                        </span>
                      </div>
                      <h3 className="font-bold text-lg mb-1 text-gray-900 dark:text-white">{achievement.achievement.name}</h3>
                      <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">{achievement.achievement.description}</p>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-indigo-600 dark:text-indigo-400">
                          +{achievement.achievement.xp_reward} XP
                        </span>
                        {achievement.unlocked ? (
                          <span className="text-green-600 dark:text-green-400 font-bold">✓ Unlocked</span>
                        ) : (
                          <span className="text-gray-600 dark:text-gray-400">🔒 Locked</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Statistics Tab */}
            {activeTab === "stats" && stats && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-lg p-6">
                    <h3 className="font-bold text-lg mb-4 dark:text-white">Learning Progress</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-300">Scenarios Completed:</span>
                        <span className="font-bold dark:text-white">{stats.scenarios_completed}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-300">Words Learned:</span>
                        <span className="font-bold dark:text-white">{stats.words_learned}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-300">Quizzes Completed:</span>
                        <span className="font-bold dark:text-white">{stats.quizzes_completed}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-300">Quiz Accuracy:</span>
                        <span className="font-bold dark:text-white">{(stats.quiz_accuracy * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 rounded-lg p-6">
                    <h3 className="font-bold text-lg mb-4 dark:text-white">Streak Information</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-300">Current Streak:</span>
                        <span className="font-bold text-orange-600 dark:text-orange-400">{stats.current_streak} days 🔥</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-300">Longest Streak:</span>
                        <span className="font-bold dark:text-white">{stats.longest_streak} days</span>
                      </div>
                      <div className="mt-4 p-3 bg-white dark:bg-gray-800 rounded-lg">
                        <p className="text-sm text-gray-600 dark:text-gray-300">
                          Keep your streak alive by completing at least one activity every day!
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Leaderboard Tab */}
            {activeTab === "leaderboard" && (
              <div className="space-y-6">
                <div className="text-center">
                  <h2 className="text-2xl font-bold mb-2 dark:text-white">🏆 XP Leaderboard</h2>
                  <p className="text-gray-600 dark:text-gray-300">Top learners ranked by total experience points</p>
                </div>

                {/* Current User Rank Card */}
                {userRank && stats && (
                  <div className="rounded-xl border-2 border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20 p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-indigo-600 text-white font-bold text-lg">
                          👤
                        </div>
                        <div>
                          <div className="font-semibold dark:text-white">Your Rank</div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            Level {stats.level}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-2xl font-bold ${
                          userRank === 1 ? 'text-yellow-600 dark:text-yellow-400' :
                          userRank === 2 ? 'text-gray-500 dark:text-gray-400' :
                          userRank === 3 ? 'text-amber-700 dark:text-amber-500' :
                          'text-gray-600 dark:text-gray-400'
                        }`}>
                          {userRank === 1 ? '🥇' : userRank === 2 ? '🥈' : userRank === 3 ? '🥉' : `#${userRank}`}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                          {stats.total_xp.toLocaleString()} XP
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Leaderboard List */}
                <div className="space-y-2">
                  <div className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Top {leaderboard.length} learners
                  </div>
                  
                  {leaderboard.map((entry, index) => (
                    <div
                      key={entry.user_id}
                      className={`rounded-lg border p-4 transition hover:shadow-md ${
                        index < 3
                          ? "border-yellow-300 dark:border-yellow-700 bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20"
                          : "bg-white dark:bg-zinc-900 border-gray-200 dark:border-zinc-800"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        {/* Left: Rank + Avatar + Name */}
                        <div className="flex items-center gap-4">
                          <div className={`text-2xl font-bold w-12 text-center ${
                            index === 0 ? 'text-yellow-600 dark:text-yellow-400' :
                            index === 1 ? 'text-gray-500 dark:text-gray-400' :
                            index === 2 ? 'text-amber-700 dark:text-amber-500' :
                            'text-gray-600 dark:text-gray-400'
                          }`}>
                            {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`}
                          </div>
                          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-200 dark:bg-zinc-700 font-semibold text-gray-700 dark:text-gray-300">
                            {entry.user_id.slice(0, 1).toUpperCase()}
                          </div>
                          <div>
                            <div className="font-semibold dark:text-white">
                              User {entry.user_id.slice(0, 8)}...
                            </div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">
                              Level {entry.level}
                            </div>
                          </div>
                        </div>

                        {/* Right: Stats */}
                        <div className="flex items-center gap-6">
                          <div className="text-right">
                            <div className="text-lg font-bold dark:text-white">{entry.total_xp.toLocaleString()}</div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">XP</div>
                          </div>
                          <div className="text-right">
                            <div className="text-lg font-bold dark:text-white">{entry.current_streak}</div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">Streak</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Link to Full Leaderboard */}
                <div className="text-center pt-4">
                  <a
                    href="/leaderboard"
                    className="inline-flex items-center gap-2 text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-medium"
                  >
                    View Full Leaderboard with More Rankings →
                  </a>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                    See streak rankings, scenario rankings, and time-based leaderboards
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
