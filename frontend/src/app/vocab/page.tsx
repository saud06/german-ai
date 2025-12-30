"use client"
import React, { useEffect, useMemo, useState } from 'react'
import RequireAuth from '@/components/RequireAuth'
import api from '@/lib/api'
import { useAuth } from '@/store/auth'
import { useSearchParams } from 'next/navigation'
import * as learningPathApi from '@/lib/learningPathApi'

type SeedWord = { _id?: string, word: string, translation?: string, example?: string, level?: string }
type UserVocab = { _id: string, word: string, translation?: string, example?: string, level?: string, status?: string, srs?: any }

// Map difficulty levels
const getLevelName = (level?: string) => {
  if (!level) return 'Beginner'
  const normalized = level.toLowerCase()
  if (normalized === 'beginner' || normalized === 'a1' || normalized === 'a2') return 'Beginner'
  if (normalized === 'intermediate' || normalized === 'b1' || normalized === 'b2') return 'Intermediate'
  if (normalized === 'advanced' || normalized === 'c1' || normalized === 'c2') return 'Advanced'
  return 'Beginner'
}

const getLevelColor = (level?: string) => {
  const name = getLevelName(level)
  if (name === 'Beginner') return 'bg-green-100 text-green-800'
  if (name === 'Intermediate') return 'bg-yellow-100 text-yellow-800'
  return 'bg-red-100 text-red-800'
}

function SoundIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" className="h-5 w-5" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
    </svg>
  )
}

function useSpeak() {
  const [speaking, setSpeaking] = useState<string | null>(null)
  const speak = (text?: string) => {
    if (!text) return
    try {
      const synth = typeof window !== 'undefined' ? window.speechSynthesis : null
      if (!synth) return
      setSpeaking(text)
      const u = new SpeechSynthesisUtterance(text)
      const de = synth.getVoices().find(v => /de(-|_)?DE/i.test(v.lang))
      if (de) u.voice = de
      u.lang = de?.lang || 'de-DE'
      u.onend = () => setSpeaking(prev => (prev === text ? null : prev))
      u.onerror = () => setSpeaking(prev => (prev === text ? null : prev))
      synth.cancel()
      synth.speak(u)
    } catch {
      setSpeaking(null)
    }
  }
  return { speaking, speak }
}

export default function VocabPage() {
  const { userId } = useAuth()
  const searchParams = useSearchParams()
  const activityId = searchParams.get('activity_id')
  const [tab, setTab] = useState<'today'|'browse'|'saved'|'review'>('today')
  const [msg, setMsg] = useState<string | null>(null)
  const flash = (m: string) => { setMsg(m); setTimeout(() => setMsg(null), 2500) }
  const { speaking, speak } = useSpeak()
  const [activityCompleted, setActivityCompleted] = useState(false)

  // Today - with multiple words and navigation
  const [todayWords, setTodayWords] = useState<SeedWord[]>([])
  const [currentWordIndex, setCurrentWordIndex] = useState(0)
  const [completedWords, setCompletedWords] = useState<Set<string>>(new Set())
  const [tLoading, setTLoading] = useState(false)
  const [tSaving, setTSaving] = useState(false)
  
  // Load user's vocab progress from backend
  const loadVocabProgress = async () => {
    if (!userId) {
      console.log('[Vocab] No userId, skipping progress load')
      return new Set<string>()
    }
    try {
      console.log('[Vocab] Loading progress for user:', userId)
      const r = await api.get('/vocab/progress/today')
      console.log('[Vocab] Progress loaded:', r.data)
      return new Set(r.data.completed_words || [])
    } catch (err) {
      console.error('[Vocab] Failed to load progress:', err)
      return new Set<string>()
    }
  }
  
  const loadTodayWords = async () => {
    try {
      setTLoading(true)
      
      // Load progress first
      const progress = await loadVocabProgress()
      setCompletedWords(progress as Set<string>)
      
      const r = await api.get('/vocab/today/batch', { 
        params: { 
          count: 10,
          level: 'beginner',
          user_id: userId || undefined 
        } 
      })
      const words = r.data || []
      setTodayWords(words)
      
      // Set current index to first incomplete word
      const firstIncomplete = words.findIndex((w: SeedWord) => !progress.has(w.word))
      setCurrentWordIndex(firstIncomplete >= 0 ? firstIncomplete : words.length - 1)
    } catch (err) {
      setTodayWords([])
      flash('Failed to load vocabulary words')
    } finally { 
      setTLoading(false) 
    }
  }
  
  
  useEffect(() => { if (tab==='today') loadTodayWords() }, [tab, userId])
  
  const currentWord = todayWords[currentWordIndex]
  
  const nextWord = async () => {
    if (!currentWord) return
    
    // Mark current word as completed
    const newCompleted = new Set(completedWords)
    newCompleted.add(currentWord.word)
    setCompletedWords(newCompleted)
    
    // Save progress to backend
    if (userId) {
      try {
        console.log('[Vocab] Marking word complete:', currentWord.word)
        await api.post('/vocab/progress/mark-complete', { 
          word: currentWord.word,
          date: new Date().toISOString().split('T')[0]
        })
        console.log('[Vocab] Word marked complete successfully')
      } catch (err) {
        console.error('[Vocab] Failed to mark word complete:', err)
      }
    }
    
    // Move to next word
    if (currentWordIndex < todayWords.length - 1) {
      setCurrentWordIndex(currentWordIndex + 1)
    } else {
      // All words completed for today!
      flash('🎉 All words completed for today! Great job!')
    }
  }
  
  const prevWord = () => {
    if (currentWordIndex > 0) {
      setCurrentWordIndex(currentWordIndex - 1)
    }
  }
  
  const saveCurrentWord = async () => {
    if (!userId || !currentWord) return
    try {
      setTSaving(true)
      await api.post('/vocab/save', { word: currentWord.word, status: 'learning' })
      flash('💾 Saved to your vocab')
    } catch {}
    finally { setTSaving(false) }
  }

  // Browse
  const [q, setQ] = useState('')
  const [level, setLevel] = useState('')
  const [bLoading, setBLoading] = useState(false)
  const [results, setResults] = useState<SeedWord[]>([])
  const [bSavingId, setBSavingId] = useState<string | null>(null)
  
  const browseVocab = async () => {
    try {
      setBLoading(true)
      const r = await api.get('/vocab/search', { params: { q, level: level || undefined, limit: 30 } })
      setResults(r.data || [])
    } catch (err) {
      setResults([])
      flash('Failed to load vocabulary results')
    } finally { 
      setBLoading(false) 
    }
  }
  
  useEffect(() => { if (tab==='browse') browseVocab() }, [tab])
  
  const saveSeed = async (w: SeedWord) => {
    if (!userId) return
    try {
      setBSavingId(w.word)
      await api.post('/vocab/save', { word: w.word, status: 'learning' })
      flash(`Added "${w.word}"`)
    } catch (err) {
      flash('Failed to add word')
    } finally { 
      setBSavingId(null) 
    }
  }

  // Saved
  const [status, setStatus] = useState('')
  const [sLoading, setSLoading] = useState(false)
  const [saved, setSaved] = useState<UserVocab[]>([])
  
  const loadSaved = async () => {
    if (!userId) return
    try {
      setSLoading(true)
      const r = await api.get('/vocab/list', { params: { status: status || undefined, limit: 50 } })
      setSaved(r.data || [])
    } catch (err) {
      setSaved([])
      flash('Failed to load saved vocabulary')
    } finally { 
      setSLoading(false) 
    }
  }
  
  useEffect(() => { if (tab==='saved') loadSaved() }, [tab, status, userId])

  // Review
  const [rLoading, setRLoading] = useState(false)
  const [session, setSession] = useState<{items: any[], idx: number} | null>(null)
  const [submitting, setSubmitting] = useState(false)
  
  const startReview = async (size=10) => {
    try {
      setRLoading(true)
      const r = await api.post('/vocab/review/start', { size })
      setSession({ items: r.data.items || [], idx: 0 })
    } catch {}
    finally { setRLoading(false) }
  }
  
  const current = useMemo(() => session ? session.items[session.idx] : null, [session])
  const [showAns, setShowAns] = useState(false)
  const [grades, setGrades] = useState<{id:string, grade:number}[]>([])
  
  const grade = (g: number) => {
    if (!session || !current) return
    const nextGrades = [...grades.filter(x=>x.id!==current.id), { id: current.id, grade: g }]
    const nextIdx = session.idx + 1
    if (nextIdx >= session.items.length) {
      submitGrades(nextGrades)
    } else {
      setGrades(nextGrades)
      setSession({ ...session, idx: nextIdx })
      setShowAns(false)
    }
  }
  
  const submitGrades = async (all: {id:string,grade:number}[]) => {
    try {
      setSubmitting(true)
      await api.post('/vocab/review/submit', { results: all })
      
      if (activityId && !activityCompleted) {
        try {
          await learningPathApi.completeActivity(activityId, 'vocabulary', 50)
          setActivityCompleted(true)
          flash('Review completed! +50 XP earned')
        } catch (error) {
          flash('Review submitted')
        }
      } else {
        flash('Review submitted')
      }
      
      setSession(null)
      setGrades([])
    } catch {}
    finally { setSubmitting(false) }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-6">
      <RequireAuth />
      
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">📚 Vocabulary Builder</h1>
          <p className="text-gray-600 dark:text-gray-400">Expand your German vocabulary with smart learning</p>
        </div>

        {/* Success Message */}
        {msg && (
          <div className="mb-6 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg flex items-center gap-2">
            <span className="text-xl">✓</span>
            <span>{msg}</span>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex items-center gap-3 mb-8 overflow-x-auto">
          <button 
            className={`px-6 py-3 rounded-lg font-medium transition-all ${tab==='today' ? 'bg-indigo-600 text-white shadow-lg' : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'}`} 
            onClick={()=>setTab('today')}
          >
            Today
          </button>
          <button 
            className={`px-6 py-3 rounded-lg font-medium transition-all ${tab==='browse' ? 'bg-indigo-600 text-white shadow-lg' : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'}`} 
            onClick={()=>setTab('browse')}
          >
            Browse
          </button>
          <button 
            className={`px-6 py-3 rounded-lg font-medium transition-all ${tab==='saved' ? 'bg-indigo-600 text-white shadow-lg' : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'}`} 
            onClick={()=>setTab('saved')}
          >
            Saved
          </button>
          <button 
            className={`px-6 py-3 rounded-lg font-medium transition-all ${tab==='review' ? 'bg-indigo-600 text-white shadow-lg' : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'}`} 
            onClick={()=>setTab('review')}
          >
            Review
          </button>
        </div>

        {/* Today Tab */}
        {tab === 'today' && (
          <div className="space-y-6">
            {tLoading && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1,2,3,4,5,6].map((i) => (
                  <div key={i} className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden animate-pulse">
                    <div className="h-32 bg-gray-200 dark:bg-gray-700" />
                    <div className="p-4">
                      <div className="h-4 w-3/4 rounded bg-gray-200 dark:bg-gray-700 mb-2" />
                      <div className="h-3 w-full rounded bg-gray-200 dark:bg-gray-700" />
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {!tLoading && todayWords.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {todayWords.map((word, index) => {
                  const isCompleted = completedWords.has(word.word)
                  const isRevealed = index <= currentWordIndex || isCompleted
                  const isCurrent = index === currentWordIndex && !isCompleted
                  
                  return (
                    <div 
                      key={index} 
                      className={`relative rounded-xl shadow-lg overflow-hidden transition-all duration-300 ${
                        isRevealed ? 'opacity-100' : 'opacity-50'
                      } ${isCurrent ? 'ring-4 ring-indigo-500 scale-105' : ''}`}
                    >
                      {/* Blur overlay for unrevealed cards */}
                      {!isRevealed && (
                        <div className="absolute inset-0 backdrop-blur-md bg-white/30 dark:bg-gray-900/30 z-10 flex items-center justify-center">
                          <div className="text-center">
                            <div className="text-4xl mb-2">🔒</div>
                            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Complete previous words</p>
                          </div>
                        </div>
                      )}
                      
                      {/* Card Header */}
                      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 p-4 text-white relative">
                        <div className="flex items-center justify-between mb-3">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getLevelColor(word.level)}`}>
                            {getLevelName(word.level)}
                          </span>
                          <button 
                            className="p-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-full transition-all"
                            onClick={()=>speak(word.word)} 
                            disabled={speaking===word.word || !isRevealed}
                          >
                            <SoundIcon />
                          </button>
                        </div>
                        <h3 className="text-2xl font-bold mb-1">{word.word}</h3>
                        <p className="text-white text-opacity-90">{word.translation}</p>
                      </div>

                      {/* Card Body */}
                      <div className="bg-white dark:bg-gray-800 p-4">
                        <div className="mb-4">
                          <p className="text-sm text-gray-600 dark:text-gray-400 uppercase font-semibold mb-1">Example</p>
                          <div className="flex items-start gap-2">
                            <p className="text-sm italic text-gray-700 dark:text-gray-300 flex-1">
                              {word.example || 'No example available'}
                            </p>
                            {word.example && (
                              <button 
                                className="p-1.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-full transition-all flex-shrink-0"
                                onClick={()=>speak(word.example)} 
                                disabled={speaking===word.example || !isRevealed}
                                title="Listen to example"
                              >
                                <SoundIcon />
                              </button>
                            )}
                          </div>
                        </div>

                        {/* Actions */}
                        {isCurrent && (
                          <div className="space-y-2">
                            <button 
                              className="w-full px-4 py-2.5 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 transition-all shadow-md"
                              onClick={saveCurrentWord} 
                              disabled={!userId || tSaving}
                            >
                              {tSaving ? 'Saving...' : '💾 Save Word'}
                            </button>
                            <button 
                              className="w-full px-4 py-2.5 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-all shadow-md"
                              onClick={nextWord}
                            >
                              {index < todayWords.length - 1 ? 'Next →' : '✓ Done'}
                            </button>
                          </div>
                        )}
                        
                        {!isCurrent && isRevealed && (
                          <div className="flex items-center justify-center py-2">
                            <span className="text-green-600 dark:text-green-400 text-sm font-medium">
                              {isCompleted ? '✓ Completed' : '✓ Unlocked'}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}

            {!tLoading && todayWords.length > 0 && completedWords.size === todayWords.length && (
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-gray-800 dark:to-gray-700 rounded-xl shadow-lg p-8 text-center border-2 border-green-200 dark:border-green-800">
                <div className="text-5xl mb-4">🎉</div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">All Words Completed!</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">Excellent work! You've completed all {todayWords.length} words for today.</p>
                <p className="text-gray-500 dark:text-gray-500 text-sm">Come back tomorrow for new words! 🚀</p>
              </div>
            )}

            {!tLoading && todayWords.length === 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 text-center">
                <p className="text-gray-600 dark:text-gray-400">No words available right now. Please try again later.</p>
              </div>
            )}
            
            {!userId && todayWords.length > 0 && (
              <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded-lg text-center">
                Login to save words and track your progress
              </div>
            )}
          </div>
        )}

        {/* Browse Tab */}
        {tab === 'browse' && (
          <div className="space-y-6">
            {/* Search Bar */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <div className="flex flex-col md:flex-row gap-4">
                <input 
                  className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white" 
                  placeholder="Search word or translation..." 
                  value={q} 
                  onChange={(e)=>setQ(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && browseVocab()}
                />
                <select 
                  className="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white" 
                  value={level} 
                  onChange={(e)=>setLevel(e.target.value)}
                >
                  <option value="">All Levels</option>
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
                <button 
                  className="px-8 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 transition-all shadow-lg"
                  onClick={browseVocab} 
                  disabled={bLoading}
                >
                  {bLoading ? 'Searching...' : 'Search'}
                </button>
              </div>
            </div>

            {/* Results Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {results.map((w, i) => (
                <div key={i} className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
                  <div className="bg-gradient-to-r from-indigo-500 to-purple-600 p-4 relative">
                    <div className="flex items-center justify-between mb-2">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getLevelColor(w.level)}`}>
                        {getLevelName(w.level)}
                      </span>
                      <button 
                        className="p-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-full transition-all"
                        onClick={()=>speak(w.word)} 
                        disabled={speaking===w.word}
                      >
                        <SoundIcon />
                      </button>
                    </div>
                    <h3 className="text-2xl font-bold text-white">{w.word}</h3>
                  </div>
                  
                  <div className="p-4">
                    <p className="text-gray-700 dark:text-gray-300 font-medium mb-2">{w.translation}</p>
                    {w.example && (
                      <div className="flex items-start gap-2 mb-4">
                        <p className="text-sm italic text-gray-500 dark:text-gray-400 flex-1">{w.example}</p>
                        <button 
                          className="p-1.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-full transition-all flex-shrink-0"
                          onClick={()=>speak(w.example)} 
                          disabled={speaking===w.example}
                          title="Listen to example"
                        >
                          <SoundIcon />
                        </button>
                      </div>
                    )}
                    
                    <button 
                      className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 transition-all"
                      disabled={!userId || bSavingId===w.word} 
                      onClick={()=>saveSeed(w)}
                    >
                      {bSavingId===w.word ? 'Adding...' : '+ Add to Saved'}
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {results.length === 0 && !bLoading && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 text-center">
                <p className="text-gray-600 dark:text-gray-400">No results found. Try a different search term.</p>
              </div>
            )}
          </div>
        )}

        {/* Saved Tab */}
        {tab === 'saved' && (
          <div className="space-y-6">
            {/* Filter Bar */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <div className="flex gap-4">
                <select 
                  className="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white" 
                  value={status} 
                  onChange={(e)=>setStatus(e.target.value)}
                >
                  <option value="">All Words</option>
                  <option value="learning">Learning</option>
                  <option value="known">Known</option>
                  <option value="due">Due for Review</option>
                </select>
                <button 
                  className="px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 transition-all"
                  onClick={loadSaved} 
                  disabled={!userId || sLoading}
                >
                  {sLoading ? 'Loading...' : 'Refresh'}
                </button>
              </div>
            </div>

            {!userId && (
              <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded-lg">
                Login to view your saved words
              </div>
            )}

            {/* Saved Words Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {saved.map((w) => (
                <div key={w._id} className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
                  <div className="bg-gradient-to-r from-green-500 to-teal-600 p-4 relative">
                    <div className="flex items-center justify-between mb-2">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getLevelColor(w.level)}`}>
                        {getLevelName(w.level)}
                      </span>
                      <button 
                        className="p-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-full transition-all"
                        onClick={()=>speak(w.word)} 
                        disabled={speaking===w.word}
                      >
                        <SoundIcon />
                      </button>
                    </div>
                    <h3 className="text-2xl font-bold text-white">{w.word}</h3>
                  </div>
                  
                  <div className="p-4">
                    <p className="text-gray-700 dark:text-gray-300 font-medium mb-2">{w.translation}</p>
                    {w.example && (
                      <div className="flex items-start gap-2 mb-3">
                        <p className="text-sm italic text-gray-500 dark:text-gray-400 flex-1">{w.example}</p>
                        <button 
                          className="p-1.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-full transition-all flex-shrink-0"
                          onClick={()=>speak(w.example)} 
                          disabled={speaking===w.example}
                          title="Listen to example"
                        >
                          <SoundIcon />
                        </button>
                      </div>
                    )}
                    {w.srs?.due && (
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Due: {new Date(w.srs.due).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {saved.length === 0 && !sLoading && userId && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 text-center">
                <p className="text-gray-600 dark:text-gray-400">No saved words yet. Start adding words from the Browse tab!</p>
              </div>
            )}
          </div>
        )}

        {/* Review Tab */}
        {tab === 'review' && (
          <div className="space-y-6">
            {!session && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Start a Review Session</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-6">Practice your saved vocabulary with spaced repetition</p>
                
                <div className="flex gap-4">
                  <button 
                    className="px-8 py-4 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 transition-all shadow-lg"
                    onClick={()=>startReview(10)} 
                    disabled={!userId || rLoading}
                  >
                    {rLoading ? 'Starting...' : 'Start 10 Words'}
                  </button>
                  <button 
                    className="px-8 py-4 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50 transition-all shadow-lg"
                    onClick={()=>startReview(20)} 
                    disabled={!userId || rLoading}
                  >
                    Start 20 Words
                  </button>
                </div>
                
                {!userId && (
                  <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">Login to start reviewing</p>
                )}
              </div>
            )}
            
            {session && current && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8">
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      Question {session.idx+1} of {session.items.length}
                    </span>
                    <div className="w-full max-w-xs bg-gray-200 dark:bg-gray-700 rounded-full h-2 ml-4">
                      <div 
                        className="bg-indigo-600 h-2 rounded-full transition-all"
                        style={{width: `${((session.idx+1) / session.items.length) * 100}%`}}
                      />
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4 mb-4">
                    <h3 className="text-3xl font-bold text-gray-900 dark:text-white">{current.word}</h3>
                    <button 
                      className="p-3 bg-indigo-100 dark:bg-indigo-900 hover:bg-indigo-200 dark:hover:bg-indigo-800 rounded-full transition-all"
                      onClick={()=>speak(current.word)} 
                      disabled={speaking===current.word}
                    >
                      <SoundIcon />
                    </button>
                  </div>
                </div>

                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 mb-6">
                  {current.prompt.mode === 'fill_in' ? (
                    <div>
                      <p className="text-lg italic text-gray-700 dark:text-gray-300">{current.prompt.prompt}</p>
                      {showAns && (
                        <div className="mt-4 p-4 bg-green-100 dark:bg-green-900 rounded-lg">
                          <p className="text-green-800 dark:text-green-200">
                            Answer: <span className="font-bold">{current.prompt.answer}</span>
                          </p>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div>
                      <p className="text-lg text-gray-700 dark:text-gray-300 mb-4">{current.prompt.prompt}</p>
                      <div className="grid grid-cols-2 gap-3">
                        {current.prompt.options?.map((o: string) => (
                          <button 
                            key={o} 
                            className="px-4 py-3 bg-white dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-500 transition-all"
                            onClick={()=>setShowAns(true)}
                          >
                            {o}
                          </button>
                        ))}
                      </div>
                      {showAns && (
                        <div className="mt-4 p-4 bg-green-100 dark:bg-green-900 rounded-lg">
                          <p className="text-green-800 dark:text-green-200">
                            Answer: <span className="font-bold">{current.prompt.answer}</span>
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                <div className="space-y-4">
                  <button 
                    className="w-full px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-all"
                    onClick={()=>setShowAns(true)}
                  >
                    Show Answer
                  </button>
                  
                  <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">How well did you know this?</p>
                    <div className="grid grid-cols-6 gap-2">
                      {[
                        {grade: 0, label: 'Forgot', color: 'bg-red-500'},
                        {grade: 1, label: 'Hard', color: 'bg-orange-500'},
                        {grade: 2, label: 'OK', color: 'bg-yellow-500'},
                        {grade: 3, label: 'Good', color: 'bg-lime-500'},
                        {grade: 4, label: 'Easy', color: 'bg-green-500'},
                        {grade: 5, label: 'Perfect', color: 'bg-emerald-500'}
                      ].map(({grade: g, label, color}) => (
                        <button 
                          key={g} 
                          className={`px-3 py-2 ${color} text-white rounded-lg font-medium hover:opacity-90 disabled:opacity-50 transition-all text-sm`}
                          onClick={()=>grade(g)} 
                          disabled={submitting}
                        >
                          {label}
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  {submitting && (
                    <p className="text-center text-sm text-gray-500 dark:text-gray-400">Submitting results...</p>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  )
}
