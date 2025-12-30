"use client"
import { useEffect, useState } from 'react'
import { useAuth } from '@/store/auth'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

interface ReviewCard {
  card_id: string
  card_type: string
  content: {
    // Vocabulary
    word?: string
    translation?: string
    // Grammar
    rule?: string
    explanation?: string
    // Quiz Mistake
    question?: string
    correct_answer?: string
    user_answer?: string
    skill?: string
    // Scenario
    scenario_name?: string
    objective?: string
    hint?: string
    keywords?: string[]
    scenario_id?: string
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

type ReviewTab = 'vocabulary' | 'grammar' | 'quiz_mistake' | 'scenario'

export default function ReviewsPage() {
  const { token } = useAuth()
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<ReviewTab>('vocabulary')
  const [stats, setStats] = useState<DailyStats | null>(null)
  const [dueCards, setDueCards] = useState<ReviewCard[]>([])
  const [currentCard, setCurrentCard] = useState<ReviewCard | null>(null)
  const [loading, setLoading] = useState(true)
  const [reviewing, setReviewing] = useState(false)
  const [reviewedInSession, setReviewedInSession] = useState<Set<string>>(new Set())

  useEffect(() => {
    if (!token) {
      router.push('/login')
      return
    }
    fetchStats()
    fetchDueCards()
  }, [token, activeTab])

  const fetchStats = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/reviews/stats?card_type=${activeTab}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setStats(data)
      }
    } catch (err) {
    }
  }

  const fetchDueCards = async () => {
    try {
      setLoading(true)
      const res = await fetch(`http://localhost:8000/api/v1/reviews/due?limit=20&card_type=${activeTab}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        // Filter out cards reviewed in this session
        const filteredData = data.filter((card: ReviewCard) => !reviewedInSession.has(card.card_id))
        setDueCards(filteredData)
        if (filteredData.length > 0) {
          setCurrentCard(filteredData[0])
        } else {
          setCurrentCard(null)
        }
      }
    } catch (err) {
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
        // Mark card as reviewed in this session
        setReviewedInSession(prev => new Set(prev).add(currentCard.card_id))
        
        // Move to next card
        const nextCards = dueCards.slice(1)
        setDueCards(nextCards)
        setCurrentCard(nextCards.length > 0 ? nextCards[0] : null)
        
        // Refresh stats
        fetchStats()
      }
    } catch (err) {
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
    }
  }

  const addGrammarCards = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/reviews/bulk-add?card_type=grammar', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        fetchStats()
        fetchDueCards()
      }
    } catch (err) {
    }
  }

  const addQuizMistakes = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/reviews/add-quiz-mistakes', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        fetchStats()
        fetchDueCards()
      }
    } catch (err) {
    }
  }

  const addScenarioObjectives = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/reviews/add-scenario-objectives', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        fetchStats()
        fetchDueCards()
      }
    } catch (err) {
    }
  }

  const renderCardContent = () => {
    if (!currentCard) return null

    switch (activeTab) {
      case 'vocabulary':
        return (
          <>
            <div className="text-sm text-gray-500 mb-2">📖 Vocabulary</div>
            <div className="text-4xl font-bold mb-4">{currentCard.content.word}</div>
            <div className="text-xl text-gray-600 dark:text-gray-400">{currentCard.content.translation}</div>
          </>
        )
      case 'grammar':
        return (
          <>
            <div className="text-sm text-gray-500 mb-2">📝 Grammar Rule</div>
            <div className="text-2xl font-bold mb-4">{currentCard.content.rule}</div>
            <div className="text-base text-gray-600 dark:text-gray-400">{currentCard.content.explanation}</div>
          </>
        )
      case 'quiz_mistake':
        return (
          <>
            <div className="text-sm text-gray-500 mb-2">❌ Quiz Mistake - {currentCard.content.skill}</div>
            <div className="text-xl font-bold mb-4">{currentCard.content.question}</div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg mb-3">
              <div className="text-sm text-red-700 dark:text-red-300 mb-1">Your answer:</div>
              <div className="font-medium text-red-600 dark:text-red-400">{currentCard.content.user_answer}</div>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg mb-3">
              <div className="text-sm text-green-700 dark:text-green-300 mb-1">Correct answer:</div>
              <div className="font-medium text-green-600 dark:text-green-400">{currentCard.content.correct_answer}</div>
            </div>
            {currentCard.content.explanation && (
              <div className="text-sm text-gray-600 dark:text-gray-400 italic">{currentCard.content.explanation}</div>
            )}
          </>
        )
      case 'scenario':
        return (
          <>
            <div className="text-sm text-gray-500 mb-2">🎭 {currentCard.content.scenario_name}</div>
            <div className="text-2xl font-bold mb-4">{currentCard.content.objective}</div>
            {currentCard.content.hint && (
              <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg mb-3">
                <div className="text-sm text-blue-700 dark:text-blue-300 mb-1">💡 Hint:</div>
                <div className="text-blue-600 dark:text-blue-400">{currentCard.content.hint}</div>
              </div>
            )}
            {currentCard.content.keywords && currentCard.content.keywords.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-3">
                {currentCard.content.keywords.map((keyword: string, i: number) => (
                  <span key={i} className="px-3 py-1 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded-full text-sm">
                    {keyword}
                  </span>
                ))}
              </div>
            )}
            <Link 
              href={`/scenarios/${currentCard.content.scenario_id}`}
              className="text-sm text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300"
            >
              → Practice this scenario
            </Link>
          </>
        )
    }
  }

  const getEmptyStateContent = () => {
    switch (activeTab) {
      case 'vocabulary':
        return {
          title: 'No Vocabulary Cards',
          description: 'Add vocabulary words to start reviewing',
          action: addVocabularyCards,
          buttonText: 'Add Vocabulary Cards'
        }
      case 'grammar':
        return {
          title: 'No Grammar Cards',
          description: 'Add grammar rules to start reviewing',
          action: addGrammarCards,
          buttonText: 'Add Grammar Cards'
        }
      case 'quiz_mistake':
        return {
          title: 'No Quiz Mistakes',
          description: 'Take some quizzes to generate review cards from your mistakes',
          action: addQuizMistakes,
          buttonText: 'Import Quiz Mistakes'
        }
      case 'scenario':
        return {
          title: 'No Scenario Objectives',
          description: 'Practice scenarios to generate review cards from incomplete objectives',
          action: addScenarioObjectives,
          buttonText: 'Import Scenario Objectives'
        }
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

      {/* Tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto">
        <button
          onClick={() => { setActiveTab('vocabulary'); setReviewedInSession(new Set()) }}
          className={`px-4 py-2 rounded-lg font-semibold transition-all whitespace-nowrap ${
            activeTab === 'vocabulary'
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
          }`}
        >
          📖 Vocabulary
        </button>
        <button
          onClick={() => { setActiveTab('grammar'); setReviewedInSession(new Set()) }}
          className={`px-4 py-2 rounded-lg font-semibold transition-all whitespace-nowrap ${
            activeTab === 'grammar'
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
          }`}
        >
          📝 Grammar
        </button>
        <button
          onClick={() => { setActiveTab('quiz_mistake'); setReviewedInSession(new Set()) }}
          className={`px-4 py-2 rounded-lg font-semibold transition-all whitespace-nowrap ${
            activeTab === 'quiz_mistake'
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
          }`}
        >
          ❌ Quiz Mistakes
        </button>
        <button
          onClick={() => { setActiveTab('scenario'); setReviewedInSession(new Set()) }}
          className={`px-4 py-2 rounded-lg font-semibold transition-all whitespace-nowrap ${
            activeTab === 'scenario'
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
          }`}
        >
          🎭 Scenarios
        </button>
      </div>

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
            {renderCardContent()}
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
          <h2 className="text-2xl font-bold mb-4">{stats && stats.total_cards === 0 ? getEmptyStateContent().title : 'All Done!'}</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {stats && stats.total_cards === 0 ? getEmptyStateContent().description : 'No cards due for review right now. Great job!'}
          </p>
          {stats && stats.total_cards === 0 && (
            <button
              onClick={getEmptyStateContent().action}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              {getEmptyStateContent().buttonText}
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
