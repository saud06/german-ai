"use client"
import React, { useEffect, useMemo, useState } from 'react'
import RequireAuth from '@/components/RequireAuth'
import api from '@/lib/api'
import { useAuth } from '@/store/auth'

type SeedWord = { _id?: string, word: string, translation?: string, example?: string, level?: string }
type UserVocab = { _id: string, word: string, translation?: string, example?: string, level?: string, status?: string, srs?: any }

function SoundIcon() {
  // Speaker with sound waves
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      className="h-4 w-4 mr-1"
      aria-hidden="true"
    >
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M3 10v4a1 1 0 001 1h2l4 3V6L6 9H4a1 1 0 00-1 1z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M16 8a5 5 0 010 8M19 5a9 9 0 010 14" />
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
      // Cancel any ongoing speech so we don't queue
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
  const [tab, setTab] = useState<'today'|'browse'|'saved'|'review'>('today')
  const [msg, setMsg] = useState<string | null>(null)
  const flash = (m: string) => { setMsg(m); setTimeout(() => setMsg(null), 2500) }
  const { speaking, speak } = useSpeak()

  // Today
  const [today, setToday] = useState<SeedWord | null>(null)
  const [tLoading, setTLoading] = useState(false)
  const [tSaving, setTSaving] = useState(false)
  const loadToday = async () => {
    try {
      setTLoading(true)
      const r = await api.get('/vocab/today', { params: { user_id: userId || undefined } })
      setToday(r.data)
    } catch {}
    finally { setTLoading(false) }
  }
  useEffect(() => { if (tab==='today') loadToday() }, [tab, userId])
  const saveToday = async () => {
    if (!userId || !today) return
    try {
      setTSaving(true)
      await api.post('/vocab/save', { word: today.word, status: 'learning' })
      flash('Saved to your vocab')
      // If user is on Saved tab, auto-refresh the list
      if (tab === 'saved') {
        await loadSaved()
      }
    } catch {
      // Errors are emitted globally via interceptor; optional local hint
    } finally {
      setTSaving(false)
    }
  }

  // Browse
  const [q, setQ] = useState('')
  const [level, setLevel] = useState('')
  const [bLoading, setBLoading] = useState(false)
  const [results, setResults] = useState<SeedWord[]>([])
  const [bSavingId, setBSavingId] = useState<string | null>(null)
  const search = async () => {
    try {
      setBLoading(true)
      const r = await api.get('/vocab/search', { params: { q, level: level || undefined, limit: 30 } })
      setResults(r.data || [])
    } catch {}
    finally { setBLoading(false) }
  }
  useEffect(() => { if (tab==='browse') search() }, [tab])
  const saveSeed = async (w: SeedWord) => {
    if (!userId) return
    try {
      setBSavingId(w.word)
      await api.post('/vocab/save', { word: w.word, status: 'learning' })
      flash(`Added "${w.word}"`)
      if (tab === 'saved') {
        await loadSaved()
      }
    } catch {
      // handled globally
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
    } catch {}
    finally { setSLoading(false) }
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
      setSession(null)
      setGrades([])
      flash('Review submitted')
    } catch {
    } finally { setSubmitting(false) }
  }

  return (
    <main className="space-y-4">
      <RequireAuth />
      <h2 className="text-xl font-semibold">Vocab Coach</h2>

      {msg && (
        <div className="rounded-md border border-emerald-300 bg-emerald-50 p-2 text-sm text-emerald-700">{msg}</div>
      )}

      <div className="flex items-center gap-2">
        <button className={`btn btn-sm ${tab==='today' ? 'bg-indigo-600 text-white' : ''}`} onClick={()=>setTab('today')}>Today</button>
        <button className={`btn btn-sm ${tab==='browse' ? 'bg-indigo-600 text-white' : ''}`} onClick={()=>setTab('browse')}>Browse</button>
        <button className={`btn btn-sm ${tab==='saved' ? 'bg-indigo-600 text-white' : ''}`} onClick={()=>setTab('saved')}>Saved</button>
        <button className={`btn btn-sm ${tab==='review' ? 'bg-indigo-600 text-white' : ''}`} onClick={()=>setTab('review')}>Review</button>
      </div>

      {tab === 'today' && (
        <section className="space-y-3">
          {tLoading && (
            <div className="rounded-md border p-4 animate-pulse">
              <div className="h-6 w-40 rounded bg-gray-200 dark:bg-zinc-800" />
              <div className="mt-2 h-4 w-56 rounded bg-gray-200 dark:bg-zinc-800" />
              <div className="mt-4 h-4 w-5/6 rounded bg-gray-200 dark:bg-zinc-800" />
            </div>
          )}
          {today && (
            <div className="rounded-md border p-4">
              <div className="flex items-center gap-3">
                <div className="text-2xl font-bold">{today.word}</div>
                <button className="btn btn-sm" onClick={()=>speak(today.word)} disabled={speaking===today.word}>
                  {speaking===today.word ? (<><SoundIcon /> Playing…</>) : 'Listen'}
                </button>
                {today.level && <span className="text-xs rounded bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5">CEFR {today.level}</span>}
              </div>
              <div className="text-gray-600">{today.translation}</div>
              <div className="mt-2 italic">{today.example}</div>
              <div className="mt-3 flex items-center gap-2">
                <button className="btn" onClick={saveToday} disabled={!userId || tSaving}>{tSaving ? 'Saving…' : 'Save'}</button>
                <button className="btn" onClick={()=>startReview(10)} disabled={!userId}>Start review</button>
              </div>
              {!userId && <p className="mt-2 text-sm text-gray-600">Login to save & review.</p>}
            </div>
          )}
          {!tLoading && !today && (
            <div className="rounded-md border p-4 text-sm text-gray-600">
              No word is available right now. Please try again later.
            </div>
          )}
        </section>
      )}

      {tab === 'browse' && (
        <section className="space-y-3">
          <div className="flex items-center gap-2">
            <input className="input" placeholder="Search word or translation" value={q} onChange={(e)=>setQ(e.target.value)} />
            <select className="input" value={level} onChange={(e)=>setLevel(e.target.value)}>
              <option value="">All levels</option>
              <option value="A1">A1</option>
              <option value="A2">A2</option>
              <option value="B1">B1</option>
              <option value="B2">B2</option>
            </select>
            <button className="btn" onClick={search} disabled={bLoading}>{bLoading ? 'Searching…' : 'Search'}</button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {results.map((w, i) => (
              <div key={i} className="rounded-md border p-3">
                <div className="flex items-center gap-2">
                  <div className="font-semibold">{w.word}</div>
                  <button className="btn btn-sm" onClick={()=>speak(w.word)} disabled={speaking===w.word}>
                    {speaking===w.word ? (<><SoundIcon /> Playing…</>) : 'Listen'}
                  </button>
                  {w.level && <span className="text-xs rounded bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5">{w.level}</span>}
                </div>
                <div className="text-sm text-gray-700">{w.translation}</div>
                {w.example && <div className="text-xs italic mt-1">{w.example}</div>}
                <div className="mt-2">
                  <button className="btn btn-sm" disabled={!userId || bSavingId===w.word} onClick={()=>saveSeed(w)}>
                    {bSavingId===w.word ? 'Adding…' : 'Add'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {tab === 'saved' && (
        <section className="space-y-3">
          <div className="flex items-center gap-2">
            <select className="input" value={status} onChange={(e)=>setStatus(e.target.value)}>
              <option value="">All</option>
              <option value="learning">Learning</option>
              <option value="known">Known</option>
              <option value="due">Due</option>
            </select>
            <button className="btn" onClick={loadSaved} disabled={!userId || sLoading}>{sLoading ? 'Loading…' : 'Refresh'}</button>
          </div>
          {!userId && <p className="text-sm text-gray-600">Login to view saved words.</p>}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {saved.map((w) => (
              <div key={w._id} className="rounded-md border p-3">
                <div className="flex items-center gap-2">
                  <div className="font-semibold">{w.word}</div>
                  <button className="btn btn-sm" onClick={()=>speak(w.word)} disabled={speaking===w.word}>
                    {speaking===w.word ? (<><SoundIcon /> Playing…</>) : 'Listen'}
                  </button>
                  {w.level && <span className="text-xs rounded bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5">{w.level}</span>}
                  {w.srs?.due && <span className="ml-auto text-xs text-gray-500">Due: {new Date(w.srs.due).toLocaleDateString()}</span>}
                </div>
                <div className="text-sm text-gray-700">{w.translation}</div>
                {w.example && <div className="text-xs italic mt-1">{w.example}</div>}
              </div>
            ))}
          </div>
        </section>
      )}

      {tab === 'review' && (
        <section className="space-y-3">
          {!session && (
            <div className="flex items-center gap-2">
              <button className="btn" onClick={()=>startReview(10)} disabled={!userId || rLoading}>{rLoading ? 'Starting…' : 'Start 10'}</button>
              <button className="btn" onClick={()=>startReview(20)} disabled={!userId || rLoading}>Start 20</button>
              {!userId && <p className="text-sm text-gray-600">Login to review.</p>}
            </div>
          )}
          {session && current && (
            <div className="rounded-md border p-4 space-y-3">
              <div className="text-sm text-gray-500">{session.idx+1} / {session.items.length}</div>
              <div className="text-xl font-semibold">{current.word}</div>
              <button className="btn btn-sm" onClick={()=>speak(current.word)} disabled={speaking===current.word}>
                {speaking===current.word ? (<><SoundIcon /> Playing…</>) : 'Listen'}
              </button>
              <div className="rounded border p-3">
                {current.prompt.mode === 'fill_in' ? (
                  <div>
                    <div className="italic">{current.prompt.prompt}</div>
                    {showAns && <div className="mt-2">Answer: <span className="font-semibold">{current.prompt.answer}</span></div>}
                  </div>
                ) : (
                  <div>
                    <div className="mb-2">{current.prompt.prompt}</div>
                    <div className="flex flex-wrap gap-2">
                      {current.prompt.options?.map((o: string) => (
                        <button key={o} className="btn btn-sm" onClick={()=>setShowAns(true)}>{o}</button>
                      ))}
                    </div>
                    {showAns && <div className="mt-2">Answer: <span className="font-semibold">{current.prompt.answer}</span></div>}
                  </div>
                )}
              </div>
              <div className="flex flex-wrap gap-2">
                <button className="btn btn-sm" onClick={()=>setShowAns(true)}>Show answer</button>
                {/* SM-2 grades */}
                {[0,1,2,3,4,5].map(n => (
                  <button key={n} className="btn btn-sm" onClick={()=>grade(n)} disabled={submitting}>{n}</button>
                ))}
                {submitting && <span className="text-xs text-gray-500">Submitting…</span>}
              </div>
            </div>
          )}
        </section>
      )}
    </main>
  )
}
