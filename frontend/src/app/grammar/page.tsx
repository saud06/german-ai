"use client"
import React, { useEffect, useState } from 'react'
import RequireAuth from '@/components/RequireAuth'
import api from '@/lib/api'
import { useAuth } from '@/store/auth'
import { useSearchParams } from 'next/navigation'
import * as learningPathApi from '@/lib/learningPathApi'

export default function GrammarCoach() {
  const { userId } = useAuth()
  const searchParams = useSearchParams()
  const activityId = searchParams.get('activity_id')
  const [sentence, setSentence] = useState('')
  const [res, setRes] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState<{original:string, corrected:string, explanation:string, ts:string}[]>([])
  const [saving, setSaving] = useState(false)
  const [examples, setExamples] = useState<{text:string, source:string}[]>([])
  const [loadingExamples, setLoadingExamples] = useState(false)
  const [levelFilter, setLevelFilter] = useState('')
  const [trackFilter, setTrackFilter] = useState('')
  const [loadingUnifiedHistory, setLoadingUnifiedHistory] = useState(false)
  const [activityCompleted, setActivityCompleted] = useState(false)
  const [checksCount, setChecksCount] = useState(0)
  const [activeTab, setActiveTab] = useState<'check' | 'practice' | 'history'>('check')

  const check = async () => {
    setLoading(true)
    try {
      const endpoint = userId ? '/grammar/check' : '/grammar/check-public'
      const r = await api.post(endpoint, { user_id: userId || undefined, sentence })
      setRes(r.data)
    } catch (e) {
      setRes(null)
    } finally {
      setLoading(false)
    }
  }

  const saveAttemptServer = async () => {
    if (!userId || !res) return
    try {
      setSaving(true)
      await api.post('/grammar/save', {
        original: res.original,
        corrected: res.corrected,
        explanation: res.explanation,
        suggested_variation: res.suggested_variation,
      })
      await loadUnifiedHistory()
      
      const newCount = checksCount + 1
      setChecksCount(newCount)
      if (activityId && !activityCompleted && newCount >= 3) {
        try {
          await learningPathApi.completeActivity(activityId, 'grammar', 60)
          setActivityCompleted(true)
        } catch (error) {
          console.error('Failed to mark activity complete:', error)
        }
      }
    } catch {}
    finally { setSaving(false) }
  }

  const loadUnifiedHistory = async () => {
    if (userId) {
      try {
        setLoadingUnifiedHistory(true)
        const r = await api.get('/grammar/history', { params: { limit: 10 } })
        setHistory(r.data || [])
      } catch {}
      finally { setLoadingUnifiedHistory(false) }
    }
  }
  useEffect(() => { loadUnifiedHistory() }, [userId])

  const loadExamples = async () => {
    try {
      setLoadingExamples(true)
      const params: any = { size: 10 }
      if (levelFilter) params.level = levelFilter
      if (trackFilter) params.track = trackFilter
      const r = await api.get('/grammar/examples', { params })
      setExamples(r.data || [])
    } catch {
      setExamples([])
    } finally {
      setLoadingExamples(false)
    }
  }
  useEffect(() => { loadExamples() }, [levelFilter, trackFilter])

  return (
    <main className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
      <RequireAuth />
      
      {/* Header */}
      <div className="max-w-6xl mx-auto mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="text-4xl">📝</div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Grammar Coach</h1>
        </div>
        <p className="text-gray-600 dark:text-gray-400">Perfect your German grammar with AI-powered corrections and explanations</p>
      </div>

      {/* Tabs */}
      <div className="max-w-6xl mx-auto mb-6">
        <div className="flex gap-2 bg-white dark:bg-gray-800 p-1 rounded-lg shadow-sm">
          <button
            onClick={() => setActiveTab('check')}
            className={`flex-1 px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === 'check'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            ✍️ Check Grammar
          </button>
          <button
            onClick={() => setActiveTab('practice')}
            className={`flex-1 px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === 'practice'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            🎯 Practice
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`flex-1 px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === 'history'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            📚 History
          </button>
        </div>
      </div>

      {/* Check Grammar Tab */}
      {activeTab === 'check' && (
        <div className="max-w-6xl mx-auto space-y-6">
          {/* Input Card */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Enter your German sentence
            </label>
            <textarea
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none transition-all"
              rows={4}
              value={sentence}
              onChange={(e)=>setSentence(e.target.value)}
              placeholder="Type or paste your German sentence here..."
            />
            <div className="flex items-center justify-between mt-4">
              <button
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md flex items-center gap-2"
                onClick={check}
                disabled={loading || !sentence.trim()}
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </svg>
                    Checking...
                  </>
                ) : (
                  <>🔍 Check Grammar</>
                )}
              </button>
              {!userId && (
                <p className="text-sm text-gray-500 dark:text-gray-400">💡 Login for personalized features</p>
              )}
            </div>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 animate-pulse">
              <div className="h-6 w-1/3 rounded bg-gray-200 dark:bg-gray-700 mb-4" />
              <div className="h-4 w-full rounded bg-gray-200 dark:bg-gray-700 mb-3" />
              <div className="h-4 w-5/6 rounded bg-gray-200 dark:bg-gray-700 mb-3" />
              <div className="h-4 w-2/3 rounded bg-gray-200 dark:bg-gray-700" />
            </div>
          )}

          {/* Result Card */}
          {res && (
            res.source === 'ok' ? (
              <div className="bg-gradient-to-r from-green-500 to-teal-600 rounded-xl shadow-lg p-6 text-white">
                <div className="flex items-center gap-3 mb-3">
                  <div className="text-4xl">✅</div>
                  <div>
                    <h3 className="text-2xl font-bold">Perfect Grammar!</h3>
                    <p className="text-green-100 text-sm">No errors detected</p>
                  </div>
                </div>
                <div className="bg-white bg-opacity-20 rounded-lg p-4 mb-3">
                  <p className="text-lg font-medium">{res.original}</p>
                </div>
                <p className="text-green-50">{res.explanation || 'Your sentence is grammatically correct. Great job!'}</p>
              </div>
            ) : (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
                {/* Header */}
                <div className="bg-gradient-to-r from-red-500 to-orange-600 p-6 text-white">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="text-4xl">❌</div>
                    <div>
                      <h3 className="text-2xl font-bold">Grammar Error Found</h3>
                      <p className="text-red-100 text-sm">Correction suggested below</p>
                    </div>
                  </div>
                  <div className="bg-white bg-opacity-20 rounded-lg p-4">
                    <p className="text-sm text-white text-opacity-80 mb-1">✅ Corrected sentence:</p>
                    <p className="text-xl font-medium">{res.corrected}</p>
                  </div>
                </div>

                {/* Body */}
                <div className="p-6 space-y-4">
                  {/* Explanation */}
                  <div className="bg-blue-50 dark:bg-blue-900 dark:bg-opacity-20 rounded-lg p-4">
                    <p className="text-sm font-medium text-blue-900 dark:text-blue-200 mb-1">📖 Explanation</p>
                    <p className="text-gray-700 dark:text-gray-300">{res.explanation}</p>
                  </div>

                  {/* Suggested Variation */}
                  {res.suggested_variation && (
                    <div className="bg-purple-50 dark:bg-purple-900 dark:bg-opacity-20 rounded-lg p-4">
                      <p className="text-sm font-medium text-purple-900 dark:text-purple-200 mb-1">💭 Try this variation</p>
                      <p className="text-gray-700 dark:text-gray-300 italic">{res.suggested_variation}</p>
                    </div>
                  )}

                  {/* Tips */}
                  {res.tips?.length > 0 && (
                    <div className="bg-yellow-50 dark:bg-yellow-900 dark:bg-opacity-20 rounded-lg p-4">
                      <p className="text-sm font-medium text-yellow-900 dark:text-yellow-200 mb-2">💡 Tips</p>
                      <ul className="list-disc pl-5 space-y-1">
                        {res.tips.map((t: string, i: number) => (
                          <li key={i} className="text-gray-700 dark:text-gray-300 text-sm">{t}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex items-center gap-3 pt-2">
                    {userId && (
                      <button
                        className="px-6 py-2.5 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 transition-all shadow-md"
                        onClick={saveAttemptServer}
                        disabled={saving}
                      >
                        {saving ? 'Saving...' : '💾 Save to History'}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )
          )}
        </div>
      )}

      {/* Practice Tab */}
      {activeTab === 'practice' && (
        <div className="max-w-6xl mx-auto">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-1">Practice Sentences</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Try checking these example sentences</p>
              </div>
              <button
                className="px-4 py-2 bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 rounded-lg font-medium hover:bg-indigo-200 dark:hover:bg-indigo-800 transition-all flex items-center gap-2"
                onClick={loadExamples}
                disabled={loadingExamples}
              >
                {loadingExamples ? (
                  <>
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </svg>
                    Loading...
                  </>
                ) : (
                  <>🔄 Refresh</>
                )}
              </button>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-4 mb-6">
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Level:</label>
                <select
                  className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  value={levelFilter}
                  onChange={(e)=>setLevelFilter(e.target.value)}
                >
                  <option value="">All Levels</option>
                  <option value="A1">A1 - Beginner</option>
                  <option value="A2">A2 - Elementary</option>
                  <option value="B1">B1 - Intermediate</option>
                  <option value="B2">B2 - Upper Intermediate</option>
                </select>
              </div>
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Topic:</label>
                <select
                  className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  value={trackFilter}
                  onChange={(e)=>setTrackFilter(e.target.value)}
                >
                  <option value="">All Topics</option>
                  <option value="articles">Articles (der/die/das)</option>
                  <option value="verbs">Verb Conjugation</option>
                  <option value="nouns">Nouns</option>
                  <option value="cases">Cases (Nominativ/Akkusativ/Dativ)</option>
                  <option value="pluralization">Pluralization</option>
                </select>
              </div>
            </div>

            {/* Example Sentences Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {examples.map((ex, i) => (
                <button
                  key={i}
                  className="text-left p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-indigo-500 dark:hover:border-indigo-500 hover:shadow-md transition-all bg-gray-50 dark:bg-gray-700"
                  onClick={() => {
                    setSentence(ex.text)
                    setActiveTab('check')
                  }}
                >
                  <p className="text-gray-900 dark:text-white font-medium">{ex.text}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{ex.source}</p>
                </button>
              ))}
              {examples.length === 0 && !loadingExamples && (
                <div className="col-span-2 text-center py-8 text-gray-500 dark:text-gray-400">
                  No examples available. Try adjusting the filters.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <div className="max-w-6xl mx-auto">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-1">Your Grammar History</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Review your past corrections and progress</p>
              </div>
              <button
                className="px-4 py-2 bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 rounded-lg font-medium hover:bg-indigo-200 dark:hover:bg-indigo-800 transition-all flex items-center gap-2"
                onClick={loadUnifiedHistory}
                disabled={loadingUnifiedHistory}
              >
                {loadingUnifiedHistory ? (
                  <>
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </svg>
                    Loading...
                  </>
                ) : (
                  <>🔄 Refresh</>
                )}
              </button>
            </div>

            {/* History Items */}
            <div className="space-y-4">
              {history.length === 0 && !loadingUnifiedHistory && (
                <div className="text-center py-12">
                  <div className="text-5xl mb-3">��</div>
                  <p className="text-gray-500 dark:text-gray-400">No grammar checks saved yet.</p>
                  <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">Start checking sentences to build your history!</p>
                </div>
              )}
              {history.map((h, i) => (
                <div key={i} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {new Date(h.ts).toLocaleDateString()} at {new Date(h.ts).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="space-y-2">
                    <div>
                      <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Original:</p>
                      <p className="text-gray-900 dark:text-white">{h.original}</p>
                    </div>
                    <div>
                      <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Corrected:</p>
                      <p className="text-green-700 dark:text-green-400 font-medium">{h.corrected}</p>
                    </div>
                    <div>
                      <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Explanation:</p>
                      <p className="text-sm text-gray-700 dark:text-gray-300">{h.explanation}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </main>
  )
}
