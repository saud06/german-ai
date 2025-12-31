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
    // Get token from localStorage
    const storedToken = localStorage.getItem("token");
    console.log('🔑 Token found:', storedToken ? 'Yes' : 'No');
    if (!storedToken) {
      console.log('⚠️ No token, redirecting to login');
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
      console.log('🔍 Fetching achievements data...');
      
      // Fetch stats
      const statsRes = await fetch("http://localhost:8000/api/v1/achievements/stats", {
        headers: { Authorization: `Bearer ${token}` }
      });
      console.log('📊 Stats response status:', statsRes.status);
      if (statsRes.ok) {
        const statsData = await statsRes.json();
        console.log('📊 Stats data:', statsData);
        setStats(statsData);
      } else {
        const errorText = await statsRes.text();
        console.error('❌ Stats error:', statsRes.status, errorText);
      }

      // Fetch achievements
      const achievementsRes = await fetch("http://localhost:8000/api/v1/achievements/list", {
        headers: { Authorization: `Bearer ${token}` }
      });
      console.log('🏆 Achievements response status:', achievementsRes.status);
      if (achievementsRes.ok) {
        const achievementsData = await achievementsRes.json();
        console.log('🏆 Achievements data:', achievementsData);
        setAchievements(achievementsData.achievements || []);
      } else {
        const errorText = await achievementsRes.text();
        console.error('❌ Achievements error:', achievementsRes.status, errorText);
      }

      // Fetch leaderboard
      const leaderboardRes = await fetch("http://localhost:8000/api/v1/achievements/leaderboard/xp", {
        headers: { Authorization: `Bearer ${token}` }
      });
      console.log('👑 Leaderboard response status:', leaderboardRes.status);
      if (leaderboardRes.ok) {
        const leaderboardData = await leaderboardRes.json();
        console.log('👑 Leaderboard data:', leaderboardData);
        setLeaderboard(leaderboardData.leaderboard || []);
        setUserRank(leaderboardData.user_rank);
      } else {
        const errorText = await leaderboardRes.text();
        console.error('❌ Leaderboard error:', leaderboardRes.status, errorText);
      }
    } catch (error) {
      console.error('❌ Fetch error:', error);
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
                          : "bg-gray-50 dark:bg-gray-700 border-gray-200 dark:border-gray-600 opacity-60"
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <span className="text-4xl">{achievement.achievement.icon}</span>
                        <span className={`text-xs font-bold uppercase ${getTierColor(achievement.achievement.tier)}`}>
                          {achievement.achievement.tier}
                        </span>
                      </div>
                      <h3 className="font-bold text-lg mb-1 dark:text-white">{achievement.achievement.name}</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">{achievement.achievement.description}</p>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-indigo-600 dark:text-indigo-400">
                          +{achievement.achievement.xp_reward} XP
                        </span>
                        {achievement.unlocked ? (
                          <span className="text-green-600 font-bold">✓ Unlocked</span>
                        ) : (
                          <span className="text-gray-400 dark:text-gray-500">🔒 Locked</span>
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
              <div>
                {userRank && (
                  <div className="bg-gradient-to-r from-yellow-100 to-orange-100 dark:from-yellow-900/30 dark:to-orange-900/30 rounded-lg p-4 mb-6 border-2 border-yellow-300 dark:border-yellow-700">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-lg dark:text-white">Your Rank: #{userRank}</span>
                      <span className="text-2xl">🏅</span>
                    </div>
                  </div>
                )}

                <div className="space-y-2">
                  {leaderboard.map((entry, index) => (
                    <div
                      key={entry.user_id}
                      className={`flex items-center justify-between p-4 rounded-lg ${
                        index < 3
                          ? "bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 border-2 border-yellow-300 dark:border-yellow-700"
                          : "bg-gray-50 dark:bg-gray-700"
                      }`}
                    >
                      <div className="flex items-center space-x-4">
                        <span className="text-2xl font-bold w-8 dark:text-white">
                          {index === 0 ? "🥇" : index === 1 ? "🥈" : index === 2 ? "🥉" : `#${index + 1}`}
                        </span>
                        <div>
                          <div className="font-medium dark:text-white">User {entry.user_id.slice(0, 8)}...</div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">Level {entry.level}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-indigo-600 dark:text-indigo-400">{entry.total_xp} XP</div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">{entry.current_streak} day streak 🔥</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
