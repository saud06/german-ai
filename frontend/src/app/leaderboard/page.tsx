"use client"

import { useState, useEffect } from 'react'
import RequireAuth from '@/components/RequireAuth'
import api from '@/lib/api'

interface LeaderboardEntry {
  user_id: string
  name: string
  rank: number
  total_xp: number
  level: number
  streak: number
  scenarios_completed: number
  achievements_unlocked: number
  avatar?: string
  is_current_user: boolean
}

interface LeaderboardData {
  entries: LeaderboardEntry[]
  current_user_entry?: LeaderboardEntry
  total_users: number
  period: string
  last_updated: string
}

type LeaderboardType = 'global' | 'streak' | 'scenarios'
type Period = 'all_time' | 'weekly' | 'monthly'

export default function LeaderboardPage() {
  const [type, setType] = useState<LeaderboardType>('global')
  const [period, setPeriod] = useState<Period>('all_time')
  const [data, setData] = useState<LeaderboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchLeaderboard()
  }, [type, period])

  const fetchLeaderboard = async () => {
    try {
      setLoading(true)
      setError(null)
      
      let endpoint = ''
      if (type === 'global') {
        endpoint = `/leaderboard/global?period=${period}&limit=100`
      } else if (type === 'streak') {
        endpoint = `/leaderboard/streak?limit=100`
      } else if (type === 'scenarios') {
        endpoint = `/leaderboard/scenarios?limit=100`
      }
      
      const response = await api.get(endpoint)
      setData(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load leaderboard')
    } finally {
      setLoading(false)
    }
  }

  const getRankBadge = (rank: number) => {
    if (rank === 1) return '🥇'
    if (rank === 2) return '🥈'
    if (rank === 3) return '🥉'
    return `#${rank}`
  }

  const getRankColor = (rank: number) => {
    if (rank === 1) return 'text-yellow-600 dark:text-yellow-400'
    if (rank === 2) return 'text-gray-500 dark:text-gray-400'
    if (rank === 3) return 'text-amber-700 dark:text-amber-500'
    return 'text-gray-600 dark:text-gray-400'
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <RequireAuth />
      
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">🏆 Leaderboard</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Compete with learners worldwide and climb the ranks!
        </p>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setType('global')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            type === 'global'
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-100 dark:bg-zinc-800 hover:bg-gray-200 dark:hover:bg-zinc-700'
          }`}
        >
          🌍 Global XP
        </button>
        <button
          onClick={() => setType('streak')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            type === 'streak'
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-100 dark:bg-zinc-800 hover:bg-gray-200 dark:hover:bg-zinc-700'
          }`}
        >
          🔥 Streak
        </button>
        <button
          onClick={() => setType('scenarios')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            type === 'scenarios'
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-100 dark:bg-zinc-800 hover:bg-gray-200 dark:hover:bg-zinc-700'
          }`}
        >
          🎭 Scenarios
        </button>
      </div>

      {/* Period selector (only for global) */}
      {type === 'global' && (
        <div className="flex gap-2">
          <button
            onClick={() => setPeriod('all_time')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition ${
              period === 'all_time'
                ? 'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300'
                : 'hover:bg-gray-100 dark:hover:bg-zinc-800'
            }`}
          >
            All Time
          </button>
          <button
            onClick={() => setPeriod('monthly')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition ${
              period === 'monthly'
                ? 'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300'
                : 'hover:bg-gray-100 dark:hover:bg-zinc-800'
            }`}
          >
            This Month
          </button>
          <button
            onClick={() => setPeriod('weekly')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition ${
              period === 'weekly'
                ? 'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300'
                : 'hover:bg-gray-100 dark:hover:bg-zinc-800'
            }`}
          >
            This Week
          </button>
        </div>
      )}

      {/* Current User Card */}
      {data?.current_user_entry && (
        <div className="rounded-xl border-2 border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-indigo-600 text-white font-bold text-lg">
                {data.current_user_entry.avatar ? (
                  <img src={data.current_user_entry.avatar} alt="Avatar" className="rounded-full" />
                ) : (
                  data.current_user_entry.name[0].toUpperCase()
                )}
              </div>
              <div>
                <div className="font-semibold">Your Rank</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {data.current_user_entry.name}
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className={`text-2xl font-bold ${getRankColor(data.current_user_entry.rank)}`}>
                {getRankBadge(data.current_user_entry.rank)}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {type === 'global' && `${data.current_user_entry.total_xp.toLocaleString()} XP`}
                {type === 'streak' && `${data.current_user_entry.streak} days`}
                {type === 'scenarios' && `${data.current_user_entry.scenarios_completed} completed`}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="space-y-3">
          {[...Array(10)].map((_, i) => (
            <div key={i} className="h-16 rounded-lg bg-gray-100 dark:bg-zinc-800 animate-pulse" />
          ))}
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="rounded-lg border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-900/20 p-4 text-red-600 dark:text-red-400">
          {error}
        </div>
      )}

      {/* Leaderboard List */}
      {!loading && !error && data && (
        <div className="space-y-2">
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Showing top {data.entries.length} of {data.total_users.toLocaleString()} learners
          </div>
          
          {data.entries.map((entry) => (
            <div
              key={entry.user_id}
              className={`rounded-lg border p-4 transition hover:shadow-md ${
                entry.is_current_user
                  ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20'
                  : 'bg-white dark:bg-zinc-900'
              }`}
            >
              <div className="flex items-center justify-between">
                {/* Left: Rank + Avatar + Name */}
                <div className="flex items-center gap-4">
                  <div className={`text-2xl font-bold w-12 text-center ${getRankColor(entry.rank)}`}>
                    {getRankBadge(entry.rank)}
                  </div>
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-200 dark:bg-zinc-700 font-semibold">
                    {entry.avatar ? (
                      <img src={entry.avatar} alt={entry.name} className="rounded-full" />
                    ) : (
                      entry.name[0].toUpperCase()
                    )}
                  </div>
                  <div>
                    <div className="font-semibold">
                      {entry.name}
                      {entry.is_current_user && (
                        <span className="ml-2 text-xs text-indigo-600 dark:text-indigo-400">(You)</span>
                      )}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      Level {entry.level}
                    </div>
                  </div>
                </div>

                {/* Right: Stats */}
                <div className="flex items-center gap-6">
                  {type === 'global' && (
                    <>
                      <div className="text-right">
                        <div className="text-lg font-bold">{entry.total_xp.toLocaleString()}</div>
                        <div className="text-xs text-gray-500">XP</div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold">{entry.streak}</div>
                        <div className="text-xs text-gray-500">Streak</div>
                      </div>
                    </>
                  )}
                  {type === 'streak' && (
                    <>
                      <div className="text-right">
                        <div className="text-lg font-bold">{entry.streak}</div>
                        <div className="text-xs text-gray-500">Days</div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold">{entry.total_xp.toLocaleString()}</div>
                        <div className="text-xs text-gray-500">XP</div>
                      </div>
                    </>
                  )}
                  {type === 'scenarios' && (
                    <>
                      <div className="text-right">
                        <div className="text-lg font-bold">{entry.scenarios_completed}</div>
                        <div className="text-xs text-gray-500">Scenarios</div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold">{entry.achievements_unlocked}</div>
                        <div className="text-xs text-gray-500">Achievements</div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && data && data.entries.length === 0 && (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">
          <div className="text-4xl mb-4">🏆</div>
          <div className="text-lg font-medium">No rankings yet</div>
          <div className="text-sm">Be the first to earn XP and climb the leaderboard!</div>
        </div>
      )}
    </div>
  )
}
