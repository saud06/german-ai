"use client"
import React, { useEffect, useState } from 'react'
import RequireAuth from '@/components/RequireAuth'
import api from '@/lib/api'
import { useAuth } from '@/store/auth'

// Character-level inline diff for compare view
const charDiff = (a: string, b: string) => {
  const s1 = a || ''
  const s2 = b || ''
  const m = s1.length, n = s2.length
  const dp: number[][] = Array.from({length:m+1},()=>Array(n+1).fill(0))
  for (let i=0;i<=m;i++) dp[i][0]=i
  for (let j=0;j<=n;j++) dp[0][j]=j
  for (let i=1;i<=m;i++) for (let j=1;j<=n;j++) {
    const cost = s1[i-1]===s2[j-1]?0:1
    dp[i][j] = Math.min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+cost)
  }
  const outA: {t:'eq'|'del'|'sub', ch:string}[] = []
  const outB: {t:'eq'|'ins'|'sub', ch:string}[] = []
  let i=m, j=n
  while (i>0 || j>0) {
    if (i>0 && j>0 && dp[i][j] === dp[i-1][j-1] + (s1[i-1]===s2[j-1]?0:1)) {
      const t = s1[i-1]===s2[j-1]? 'eq':'sub'
      outA.push({t: t==='sub'?'sub':'eq', ch: s1[i-1]})
      outB.push({t: t==='sub'?'sub':'eq', ch: s2[j-1]})
      i--; j--
    } else if (i>0 && dp[i][j] === dp[i-1][j] + 1) {
      outA.push({t:'del', ch:s1[i-1]}); i--
    } else {
      outB.push({t:'ins', ch:s2[j-1]}); j--
    }
  }
  return {a: outA.reverse(), b: outB.reverse()}
}

const renderCharRow = (row: {t:string,ch:string}[], map: Record<string,string>) => {
  return (
    <div className="flex flex-wrap text-xs font-mono">
      {row.map((x, idx) => {
        let cls = 'px-0.5 rounded'
        if (x.t==='eq') cls += ' bg-gray-100'
        if (x.t==='del') cls += ' bg-red-200 text-red-900'
        if (x.t==='ins') cls += ' bg-blue-200 text-blue-900'
        if (x.t==='sub') cls += ' bg-amber-200 text-amber-900'
        return <span key={idx} className={cls}>{map[x.ch] ?? x.ch}</span>
      })}
    </div>
  )
}

const charMap: Record<string,string> = {}

export default function GrammarCoach() {
  const { userId } = useAuth()
  const [sentence, setSentence] = useState('Ich gehen zur Schule.')
  const [res, setRes] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState<{original:string, corrected:string, explanation:string, ts:string}[]>([])
  const [saving, setSaving] = useState(false)
  const [examples, setExamples] = useState<{text:string, source:string}[]>([])
  const [loadingExamples, setLoadingExamples] = useState(false)
  const [levelFilter, setLevelFilter] = useState('')
  const [trackFilter, setTrackFilter] = useState('')
  const [loadingUnifiedHistory, setLoadingUnifiedHistory] = useState(false)
  const [showCompare, setShowCompare] = useState(false)
  const [patternExamples, setPatternExamples] = useState<{text:string, source:string}[]>([])
  const [loadingPatternExamples, setLoadingPatternExamples] = useState(false)

  const check = async () => {
    setLoading(true)
    try {
      const endpoint = userId ? '/grammar/check' : '/grammar/check-public'
      const r = await api.post(endpoint, { user_id: userId || undefined, sentence })
      setRes(r.data)
    } catch (e) {
      // Error banner is emitted globally via axios interceptor; clear any stale result
      setRes(null)
    } finally {
      setLoading(false)
    }
  }

  // Save grammar attempt locally in frontend (simple local history for now)
  const saveAttemptLocal = () => {
    if (!res) return
    try {
      setSaving(true)
      const item = { original: res.original, corrected: res.corrected, explanation: res.explanation, ts: new Date().toISOString() }
      const prev = JSON.parse(localStorage.getItem('grammar_history') || '[]')
      prev.unshift(item)
      localStorage.setItem('grammar_history', JSON.stringify(prev.slice(0, 20)))
      setHistory(prev.slice(0, 20))
    } finally { setSaving(false) }
  }

  const loadLocalHistory = () => {
    try {
      const prev = JSON.parse(localStorage.getItem('grammar_history') || '[]')
      setHistory(prev)
    } catch {}
  }
  useEffect(() => { if (!userId) loadLocalHistory(); }, [userId])

  // Load examples from backend
  const loadExamples = async () => {
    try {
      setLoadingExamples(true)
      const params: any = { size: 10 }
      if (levelFilter) params.level = levelFilter
      if (trackFilter) params.track = trackFilter
      const r = await api.get('/grammar/examples', { params })
      setExamples(r.data || [])
    } catch {
      // Avoid static fallbacks; show no examples when backend is unavailable
      setExamples([])
    } finally {
      setLoadingExamples(false)
    }
  }
  useEffect(() => { loadExamples() }, [levelFilter, trackFilter])

  // Save to server (if logged in)
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
    } else {
      loadLocalHistory()
    }
  }
  useEffect(() => { loadUnifiedHistory() }, [userId])

  // Guess a track (articles/verbs/cases/pluralization/nouns) from explanation text
  const guessTrack = (exp: string): string | '' => {
    const e = (exp || '').toLowerCase()
    if (/artikel|article/.test(e)) return 'articles'
    if (/konjugation|conjugation|verb/.test(e)) return 'verbs'
    if (/fall|case|akkusativ|dativ|genitiv|nominativ/.test(e)) return 'cases'
    if (/plural/.test(e)) return 'pluralization'
    if (/nomen|noun/.test(e)) return 'nouns'
    return ''
  }

  // Load practice items for detected pattern
  const loadPatternExamples = async (track: string) => {
    if (!track) { setPatternExamples([]); return }
    try {
      setLoadingPatternExamples(true)
      const r = await api.get('/grammar/examples', { params: { size: 6, track } })
      setPatternExamples(r.data || [])
    } catch {
      setPatternExamples([])
    } finally { setLoadingPatternExamples(false) }
  }

  return (
    <main className="space-y-4">
      <RequireAuth />
      <h2 className="text-xl font-semibold">AI Grammar Coach</h2>
      <textarea className="input h-28" value={sentence} onChange={(e)=>setSentence(e.target.value)} />
      <div className="flex items-center gap-3">
        <button className="btn" onClick={check} disabled={loading}>{loading ? 'Checking...' : 'Check grammar'}</button>
        {!userId && <p className="text-sm text-gray-600">Using public check (login for personalized features).</p>}
      </div>
      {loading && (
        <div className="rounded-md border p-4 animate-pulse">
          <div className="h-5 w-1/2 rounded bg-gray-200 dark:bg-zinc-800" />
          <div className="mt-2 h-4 w-5/6 rounded bg-gray-200 dark:bg-zinc-800" />
          <div className="mt-2 h-4 w-2/3 rounded bg-gray-200 dark:bg-zinc-800" />
        </div>
      )}
      {res && (
        res.source === 'ok' ? (
          <div className="rounded-md border border-green-300 bg-green-50 p-3 text-green-800">
            Looks correct! {res.explanation || 'No issues detected.'}
          </div>
        ) : (
          <div className="rounded-md border p-4 space-y-3">
            <div><span className="font-semibold">Corrected:</span> {res.corrected}</div>
            <div className="text-sm text-gray-700">{res.explanation}</div>
            <div className="flex items-center gap-2 text-xs">
              <label className="flex items-center gap-1"><input type="checkbox" checked={showCompare} onChange={(e)=>setShowCompare(e.target.checked)} /> Compare view</label>
            </div>
            {showCompare && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                <div className="rounded border p-2">
                  <div className="text-xs text-gray-500 mb-1">Original</div>
                  <div className="flex flex-wrap gap-1">
                    {(res.highlights||[]).map((h:any,i:number)=>{
                      let bg = 'bg-red-100 text-red-800'
                      if (h.op==='ok') bg='bg-gray-100'
                      if (h.op==='sub') bg='bg-amber-100 text-amber-800'
                      if (h.op==='del') bg='bg-red-200 text-red-900'
                      const label = h.before || ''
                      return <span key={i} className={`px-1.5 py-0.5 rounded ${bg}`}>{label}</span>
                    })}
                  </div>
                </div>
                <div className="rounded border p-2">
                  <div className="text-xs text-gray-500 mb-1">Corrected</div>
                  <div className="flex flex-wrap gap-1">
                    {(res.highlights||[]).map((h:any,i:number)=>{
                      let bg = 'bg-green-100 text-green-800'
                      if (h.op==='ok') bg='bg-gray-100'
                      if (h.op==='sub') bg='bg-green-200 text-green-900'
                      if (h.op==='ins') bg='bg-blue-100 text-blue-800'
                      const label = h.after || ''
                      return <span key={i} className={`px-1.5 py-0.5 rounded ${bg}`}>{label}</span>
                    })}
                  </div>
                </div>
                {/* Char-level inline diff */}
                <div className="md:col-span-2 rounded border p-2">
                  <div className="text-xs text-gray-500 mb-1">Character-level diff</div>
                  {(() => { const d = charDiff(res.original, res.corrected); return (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      <div>
                        <div className="text-xs text-gray-500">Original</div>
                        {renderCharRow(d.a as any, charMap)}
                      </div>
                      <div>
                        <div className="text-xs text-gray-500">Corrected</div>
                        {renderCharRow(d.b as any, charMap)}
                      </div>
                    </div>
                  )})()}
                </div>
              </div>
            )}
            {res.highlights?.length ? (
              <div>
                <div className="text-xs text-gray-500 mb-1">Changes</div>
                <div className="flex flex-wrap gap-1">
                  {res.highlights.map((h: any, i: number) => {
                    let bg = 'bg-green-100 text-green-800'
                    if (h.op === 'sub') bg = 'bg-amber-100 text-amber-800'
                    if (h.op === 'del') bg = 'bg-red-100 text-red-800'
                    if (h.op === 'ins') bg = 'bg-blue-100 text-blue-800'
                    const label = h.op === 'ins' ? (h.after || '') : (h.before || '')
                    return <span key={i} className={`px-2 py-0.5 rounded text-xs ${bg}`}>{label}</span>
                  })}
                </div>
              </div>
            ) : null}
            {res.tips?.length ? (
              <ul className="list-disc pl-6 text-sm text-gray-700">
                {res.tips.map((t: string, i: number) => <li key={i}>{t}</li>)}
              </ul>
            ) : null}
            <div className="text-sm italic">Try this: {res.suggested_variation}</div>
            <div className="flex items-center gap-2">
              <button className="btn btn-sm" onClick={saveAttemptLocal} disabled={saving}>{saving ? 'Saving…' : 'Save locally'}</button>
              {userId && (
                <button className="btn btn-sm" onClick={saveAttemptServer} disabled={saving}>{saving ? 'Saving…' : 'Save to account'}</button>
              )}
            </div>
            {/* Pattern-targeted practice */}
            {(() => {
              const t = guessTrack(res?.explanation || '')
              if (t && patternExamples.length === 0 && !loadingPatternExamples) {
                // lazy load once per result
                loadPatternExamples(t)
              }
              return t ? (
                <div className="rounded-md border p-3 text-sm space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="font-medium">Practice this pattern</div>
                    <span className="text-xs text-gray-500">track: {t}</span>
                    <button
                      className="btn btn-sm inline-flex items-center gap-1 disabled:opacity-60 disabled:cursor-not-allowed"
                      onClick={()=>loadPatternExamples(t)}
                      disabled={loadingPatternExamples}
                      aria-busy={loadingPatternExamples}
                      aria-label="Refresh pattern examples"
                      title="Refresh pattern examples"
                    >
                      {loadingPatternExamples && (
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="opacity-90 animate-spin" aria-hidden="true" focusable="false"><path d="M12 2a10 10 0 100 20 10 10 0 100-20Zm0 3a7 7 0 110 14 7 7 0 010-14Z" fill="#e5e7eb"/><path d="M12 2a10 10 0 00-7.07 2.93l2.12 2.12A7 7 0 0119 12h3A10 10 0 0012 2Z" fill="currentColor"/></svg>
                      )}
                      <span>{loadingPatternExamples ? 'Refreshing' : 'Refresh'}</span>
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {patternExamples.map((s, i) => (
                      <button key={i} className="px-2 py-1 rounded border hover:bg-gray-50" onClick={()=>setSentence(s.text)} title={s.source}>{s.text}</button>
                    ))}
                    {patternExamples.length === 0 && <span className="text-gray-500 text-xs">No suggestions yet.</span>}
                  </div>
                </div>
              ) : null
            })()}
          </div>
        )
      )}

      {/* Quick examples */}
      <div className="rounded-md border p-3 text-sm space-y-2">
        <div className="flex items-center gap-2">
          <h3 className="font-medium">Try one of these</h3>
          <button
            className="btn btn-sm inline-flex items-center gap-1 disabled:opacity-60 disabled:cursor-not-allowed"
            onClick={loadExamples}
            disabled={loadingExamples}
            aria-busy={loadingExamples}
            aria-label="Refresh examples"
            title="Refresh examples"
          >
            {loadingExamples && (
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="opacity-90 animate-spin" aria-hidden="true" focusable="false"><path d="M12 2a10 10 0 100 20 10 10 0 100-20Zm0 3a7 7 0 110 14 7 7 0 010-14Z" fill="#e5e7eb"/><path d="M12 2a10 10 0 00-7.07 2.93l2.12 2.12A7 7 0 0119 12h3A10 10 0 0012 2Z" fill="currentColor"/></svg>
            )}
            <span>{loadingExamples ? 'Refreshing' : 'Refresh'}</span>
          </button>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1">
            <span className="text-gray-500">Level</span>
            <select className="input py-1" value={levelFilter} onChange={(e)=>setLevelFilter(e.target.value)}>
              <option value="">Any</option>
              <option value="A1">A1</option>
              <option value="A2">A2</option>
              <option value="B1">B1</option>
              <option value="B2">B2</option>
            </select>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-gray-500">Track</span>
            <select className="input py-1" value={trackFilter} onChange={(e)=>setTrackFilter(e.target.value)}>
              <option value="">Any</option>
              <option value="articles">articles</option>
              <option value="verbs">verbs</option>
              <option value="nouns">nouns</option>
              <option value="cases">cases</option>
              <option value="pluralization">pluralization</option>
            </select>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {examples.map((s, i) => (
            <button key={i} className="px-2 py-1 rounded border hover:bg-gray-50" onClick={()=>setSentence(s.text)} title={s.source}>{s.text}</button>
          ))}
          {examples.length === 0 && !loadingExamples && (
            <span className="text-gray-500 text-xs">No examples available.</span>
          )}
        </div>
      </div>

      {/* Unified History (server if logged in; otherwise local) */}
      <div className="rounded-md border p-3 text-sm space-y-2">
        <div className="flex items-center gap-2">
          <h3 className="font-medium">History</h3>
          <button
            className="btn btn-sm inline-flex items-center gap-1 disabled:opacity-60 disabled:cursor-not-allowed"
            onClick={loadUnifiedHistory}
            disabled={loadingUnifiedHistory}
            aria-busy={loadingUnifiedHistory}
            aria-label="Refresh history"
            title="Refresh history"
          >
            {loadingUnifiedHistory && (
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="opacity-90 animate-spin" aria-hidden="true" focusable="false"><path d="M12 2a10 10 0 100 20 10 10 0 100-20Zm0 3a7 7 0 110 14 7 7 0 010-14Z" fill="#e5e7eb"/><path d="M12 2a10 10 0 00-7.07 2.93l2.12 2.12A7 7 0 0119 12h3A10 10 0 0012 2Z" fill="currentColor"/></svg>
            )}
            <span>{loadingUnifiedHistory ? 'Refreshing' : 'Refresh'}</span>
          </button>
        </div>
        <div className="space-y-1">
          {history.length === 0 && <div className="text-gray-500">No checks saved yet.</div>}
          {history.map((h, i) => (
            <div key={i} className="rounded border px-2 py-1">
              <div className="flex items-center justify-between">
                <div className="font-medium">{new Date(h.ts).toLocaleString()}</div>
              </div>
              <div><span className="font-semibold">Original:</span> {h.original}</div>
              <div><span className="font-semibold">Corrected:</span> {h.corrected}</div>
              <div className="text-xs text-gray-500">{h.explanation}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Micro-exercises (rule-specific) */}
      {res && res.corrected && (
        <MicroExercises original={res.original} corrected={res.corrected} explanation={res.explanation} />
      )}
    </main>
  )
}

// --- Micro Exercises Component ---
function MicroExercises({ original, corrected, explanation }: { original: string, corrected: string, explanation?: string }) {
  const [items, setItems] = useState<any[]>([])
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [checked, setChecked] = useState(false)

  const load = async () => {
    try {
      const r = await api.post('/grammar/micro', { original, corrected, explanation })
      setItems(r.data || [])
      setAnswers({})
      setChecked(false)
    } catch {}
  }
  useEffect(() => { load() }, [original, corrected])

  const onAnswer = (id: string, val: string) => setAnswers(prev => ({ ...prev, [id]: val }))
  const isCorrect = (it: any) => (answers[it.id] || '').trim() === (it.answer || '').trim()

  if (!items.length) return null
  return (
    <div className="rounded-md border p-3 text-sm space-y-2">
      <div className="flex items-center gap-2">
        <h3 className="font-medium">Practice the fix</h3>
        <button className="btn btn-sm" onClick={load}>New set</button>
        <button className="btn btn-sm" onClick={()=>setChecked(true)}>Check</button>
      </div>
      <div className="space-y-2">
        {items.map((it) => (
          <div key={it.id} className="rounded border p-2">
            <div className="mb-1">{it.prompt}</div>
            {it.type === 'fill_in' ? (
              <input className="input py-1 text-sm" value={answers[it.id] || ''} onChange={(e)=>onAnswer(it.id, e.target.value)} placeholder="Your answer" />
            ) : (
              <div className="flex flex-wrap gap-2">
                {it.options?.map((o: string) => (
                  <button key={o} className={`px-2 py-1 rounded border ${checked ? (o===it.answer ? 'bg-green-100 border-green-300' : (answers[it.id]===o ? 'bg-red-100 border-red-300' : '')) : ''}`} onClick={()=>onAnswer(it.id, o)}>{o}</button>
                ))}
              </div>
            )}
            {checked && (
              <div className={`text-xs mt-1 ${isCorrect(it)?'text-green-700':'text-red-700'}`}>{isCorrect(it)?'Correct':'Answer: '+it.answer}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
