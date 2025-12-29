"use client"
import { useEffect, useState } from 'react'
import { useAuth } from '@/store/auth'
import { useRouter } from 'next/navigation'

interface ReviewCard {
  card_id: string
  card_type: string
  content: {
    word?: string
    translation?: string
    rule?: string
    explanation?: string
  }
  repetitions: number
  easiness_factor: number
  interval: number
  next_review_date: string
}

interface DailyStats {
  total_cards: number
  new_cards: number
  learning_cards: number
  mature_cards: number
  due_today: number
  reviewed_today: number
  retention_rate: number
}

export default function ReviewsPage() {
  const { token } = useAuth()
  const router = useRouter()
  const [stats, setStats] = useState<DailyStats | null>(null)
  const [dueCards, setDueCards] = useState<ReviewCard[]>([])
  const [currentCard, setCurrentCard] = useState<ReviewCard | null>(null)
  const [loading, setLoading] = useState(true)
  const [reviewing, setReviewing] = useState(false)

  useEffect(() => {
    if (!token) {
      router.push('/login')
      return
    }
    fetchStats()
    fetchDueCards()
  }, [token])

  const fetchStats = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/reviews/stats', {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setStats(data)
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err)
    }
  }

  const fetchDueCards = async () => {
    try {
      setLoading(true)
      const res = await fetch('http://localhost:8000/api/v1/reviews/due?limit=20', {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setDueCards(data)
        if (data.length > 0) {
          setCurrentCard(data[0])
        }
      }
    } catch (err) {
      console.error('Failed to fetch due cards:', err)
    } finally {
      setLoading(false)
    }
  }

  const submitReview = async (quality: number) => {
    if (!currentCard) return
    
    setReviewing(true)
    try {
      const res = await fetch('http://localhost:8000/api/v1/reviews/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          card_id: currentCard.card_id,
          quality
        })
      })
      
      if (res.ok) {
        // Move to next card
        const nextCards = dueCards.slice(1)
        setDueCards(nextCards)
        setCurrentCard(nextCards.length > 0 ? nextCards[0] : null)
        
        // Refresh stats
        fetchStats()
      }
    } catch (err) {
      console.error('Failed to submit review:', err)
    } finally {
      setReviewing(false)
    }
  }

  const addVocabularyCards = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/reviews/bulk-add?card_type=vocabulary', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        fetchStats()
        fetchDueCards()
      }
    } catch (err) {
      console.error('Failed to add cards:', err)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading reviews...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">📚 Spaced Repetition Reviews</h1>

      {/* Stats Dashboard */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white dark:bg-zinc-800 rounded-lg p-4 shadow">
            <div className="text-2xl font-bold text-indigo-600">{stats.total_cards}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Total Cards</div>
          </div>
          <div className="bg-white dark:bg-zinc-800 rounded-lg p-4 shadow">
            <div className="text-2xl font-bold text-green-600">{stats.new_cards}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">New</div>
          </div>
          <div className="bg-white dark:bg-zinc-800 rounded-lg p-4 shadow">
            <div className="text-2xl font-bold text-amber-600">{stats.learning_cards}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Learning</div>
          </div>
          <div className="bg-white dark:bg-zinc-800 rounded-lg p-4 shadow">
            <div className="text-2xl font-bold text-purple-600">{stats.mature_cards}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Mature</div>
          </div>
          <div className="bg-white dark:bg-zinc-800 rounded-lg p-4 shadow">
            <div className="text-2xl font-bold text-rose-600">{stats.due_today}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Due Today</div>
          </div>
          <div className="bg-white dark:bg-zinc-800 rounded-lg p-4 shadow">
            <div className="text-2xl font-bold text-cyan-600">{stats.reviewed_today}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Reviewed</div>
          </div>
          <div className="bg-white dark:bg-zinc-800 rounded-lg p-4 shadow col-span-2">
            <div className="text-2xl font-bold text-teal-600">{stats.retention_rate.toFixed(1)}%</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Retention Rate</div>
          </div>
        </div>
      )}

      {/* Review Card */}
      {currentCard ? (
        <div className="bg-white dark:bg-zinc-800 rounded-lg shadow-lg p-8 mb-6">
          <div className="text-center mb-8">
            <div className="text-sm text-gray-500 mb-2">
              {currentCard.card_type === 'vocabulary' ? '📖 Vocabulary' : '📝 Grammar'}
            </div>
            <div className="text-4xl font-bold mb-4">
              {currentCard.content.word || currentCard.content.rule}
            </div>
            <div className="text-xl text-gray-600 dark:text-gray-400">
              {currentCard.content.translation || currentCard.content.explanation}
            </div>
          </div>

          <div className="text-center text-sm text-gray-500 mb-6">
            Repetitions: {currentCard.repetitions} | EF: {currentCard.easiness_factor.toFixed(2)}
          </div>

          {/* Quality Buttons */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            <button
              onClick={() => submitReview(0)}
              disabled={reviewing}
              className="px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
            >
              😵 Blackout
            </button>
            <button
              onClick={() => submitReview(1)}
              disabled={reviewing}
              className="px-4 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50"
            >
              ❌ Wrong
            </button>
            <button
              onClick={() => submitReview(2)}
              disabled={reviewing}
              className="px-4 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50"
            >
              😓 Hard
            </button>
            <button
              onClick={() => submitReview(3)}
              disabled={reviewing}
              className="px-4 py-3 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50"
            >
              🤔 Good
            </button>
            <button
              onClick={() => submitReview(4)}
              disabled={reviewing}
              className="px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              😊 Easy
            </button>
            <button
              onClick={() => submitReview(5)}
              disabled={reviewing}
              className="px-4 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50"
            >
              🎯 Perfect
            </button>
          </div>

          <div className="mt-6 text-center text-sm text-gray-500">
            {dueCards.length - 1} cards remaining
          </div>
        </div>
      ) : (
        <div className="bg-white dark:bg-zinc-800 rounded-lg shadow-lg p-12 text-center">
          <div className="text-6xl mb-4">🎉</div>
          <h2 className="text-2xl font-bold mb-4">All Done!</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            No cards due for review right now. Great job!
          </p>
          {stats && stats.total_cards === 0 && (
            <button
              onClick={addVocabularyCards}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Add Vocabulary Cards
            </button>
          )}
        </div>
      )}

      {/* Info Section */}
      <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-6">
        <h3 className="font-semibold mb-2">💡 How it works</h3>
        <p className="text-sm text-gray-700 dark:text-gray-300">
          This uses the SM-2 spaced repetition algorithm to optimize your learning. 
          Rate each card honestly - the algorithm will adjust review intervals based on your performance.
          Cards you find difficult will appear more frequently, while easy cards will have longer intervals.
        </p>
      </div>
    </div>
  )
}
