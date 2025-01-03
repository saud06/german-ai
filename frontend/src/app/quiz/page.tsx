"use client"
import React, { useEffect, useState } from 'react'
import RequireAuth from '@/components/RequireAuth'
import api from '@/lib/api'
import { useAuth } from '@/store/auth'
import Link from 'next/link'

interface Q {
  id: string
  type: 'mcq' | 'fill_in'
  question?: string
  sentence?: string
  options?: string[]
  answer: string
}

export default function QuizPage() {
  const { userId } = useAuth()
  const [mounted, setMounted] = useState(false)
  const [quizId, setQuizId] = useState<string>('')
  const [qs, setQs] = useState<Q[]>([])
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [result, setResult] = useState<any>(null)
  const [loadingQs, setLoadingQs] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [track, setTrack] = useState<string>('')
  const [size, setSize] = useState<number>(5)
  const [source, setSource] = useState<string>('')
  const [refreshFlag, setRefreshFlag] = useState<number>(0)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(()=>{
    if (!mounted) return
    setLoadingQs(true)
    setError(null)
    api.get('/quiz/start', { params: { track: track || undefined, size } })
      .then(r=>{
        setQuizId(r.data.quiz_id)
        setQs(r.data.questions || [])
        setSource(r.data.source || '')
      })
      .catch(async (e)=>{
        console.error('Failed to load quiz (auth route). Will try public route next:', e)
        try {
          const r = await api.get('/quiz/start-public', { params: { track: track || undefined, size } })
          setQuizId(r.data.quiz_id)
          setQs(r.data.questions || [])
          setSource(r.data.source || '')
        } catch (e2) {
          console.error('Failed to load quiz (public route):', e2)
          setError('Failed to load quiz. Please try again.')
        }
      })
      .finally(()=> setLoadingQs(false))
  }, [mounted, userId, track, size, refreshFlag])

  const submit = async () => {
    if (!mounted) return null
    const r = await api.post('/quiz/submit', { quiz_id: quizId, answers })
    setResult(r.data)
  }

  if (!mounted) return null

  return (
    <main className="space-y-4">
      <RequireAuth />
      <h2 className="text-xl font-semibold">Mini Quiz</h2>
      <div className="flex flex-wrap items-end gap-3">
        <div>
          <label className="text-xs text-gray-500">Track</label>
          <select className="input ml-2" value={track} onChange={(e)=>setTrack(e.target.value)}>
            <option value="">Any</option>
            <option value="articles">Articles</option>
            <option value="pluralization">Pluralization</option>
            <option value="cases">Cases</option>
            <option value="nouns">Nouns</option>
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-500">Size</label>
          <input
            type="number"
            min={1}
            max={10}
            className="input ml-2 w-24"
            value={size}
            onChange={(e)=> setSize(Math.max(1, Math.min(10, Number(e.target.value) || 1)))}
          />
        </div>
        <button className="btn" onClick={()=> setRefreshFlag(f=>f+1)}>Reload</button>
      </div>
      {/* Source hidden from end users */}
      {loadingQs ? (
        <div className="space-y-4 animate-pulse">
          <div className="rounded-md border p-3">
            <div className="h-4 w-1/2 rounded bg-gray-200 dark:bg-zinc-800" />
            <div className="mt-2 flex gap-2">
              <div className="h-8 w-20 rounded-md bg-gray-200 dark:bg-zinc-800" />
              <div className="h-8 w-20 rounded-md bg-gray-200 dark:bg-zinc-800" />
              <div className="h-8 w-20 rounded-md bg-gray-200 dark:bg-zinc-800" />
            </div>
          </div>
          <div className="rounded-md border p-3">
            <div className="h-4 w-2/3 rounded bg-gray-200 dark:bg-zinc-800" />
            <div className="mt-2 h-10 rounded bg-gray-200 dark:bg-zinc-800" />
          </div>
        </div>
      ) : (
        <>
          <div className="space-y-4">
            {qs.map(q=> (
              <div key={q.id} className="rounded-md border p-3">
                {q.type === 'mcq' ? (
                  <>
                    <div className="font-medium">{q.question}</div>
                    <div className="mt-2 flex gap-2 flex-wrap">
                      {q.options?.map(opt => (
                        <button key={opt} className={`px-3 py-1 rounded-md border ${answers[q.id]===opt ? 'bg-brand-600 text-white' : ''}`} onClick={()=>setAnswers(prev=>({...prev, [q.id]: opt}))}>{opt}</button>
                      ))}
                    </div>
                  </>
                ) : (
                  <>
                    <div className="font-medium">{q.sentence}</div>
                    <input className="input mt-2" placeholder="Your answer" value={answers[q.id] || ''} onChange={(e)=>setAnswers(prev=>({...prev, [q.id]: e.target.value}))} />
                  </>
                )}
              </div>
            ))}
          </div>
          {error && <div className="text-sm text-red-600">{error}</div>}
          {qs.length > 0 && <button className="btn" onClick={submit}>Submit</button>}
        </>
      )}
      {result && (
        <div className="rounded-md border p-3">
          <div className="font-semibold">Score: {result.score}/{result.total}</div>
          <div className="text-sm">{result.feedback}</div>
          <div className="text-xs text-gray-600">Weaknesses: {result.weaknesses?.join(', ')}</div>
        </div>
      )}
    </main>
  )
}
