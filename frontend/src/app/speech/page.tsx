"use client"
import React, { useCallback, useEffect, useRef, useState } from 'react'
import RequireAuth from '@/components/RequireAuth'
import LiveTranscriptionCard from '@/components/LiveTranscriptionCard'
import api from '@/lib/api'
import { useAuth } from '@/store/auth'
import Link from 'next/link'

type SpeechResult = {
  expected: string
  transcribed: string
  score: number
  feedback: string
  aligned?: { expected?: string | null; heard?: string | null; op: 'ok'|'sub'|'del'|'ins' }[]
}

// Simple Levenshtein similarity [0..100]
function similarity(a: string, b: string): number {
  const s1 = (a || '').toLowerCase().trim()
  const s2 = (b || '').toLowerCase().trim()
  const m = s1.length, n = s2.length
  if (m === 0 && n === 0) return 100
  const dp = Array.from({ length: m + 1 }, () => new Array<number>(n + 1).fill(0))
  for (let i = 0; i <= m; i++) dp[i][0] = i
  for (let j = 0; j <= n; j++) dp[0][j] = j
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      const cost = s1[i - 1] === s2[j - 1] ? 0 : 1
      dp[i][j] = Math.min(
        dp[i - 1][j] + 1,
        dp[i][j - 1] + 1,
        dp[i - 1][j - 1] + cost
      )
    }
  }
  const dist = dp[m][n]
  const maxLen = Math.max(m, n) || 1
  return Math.round((1 - dist / maxLen) * 100)
}

export default function SpeechPage() {
  const { userId } = useAuth()
  const [expected, setExpected] = useState('Ich gehe zur Schule.')
  const [serverResult, setServerResult] = useState<SpeechResult | null>(null)
  const [localTranscript, setLocalTranscript] = useState<string>('')
  const [localScore, setLocalScore] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [suggestions, setSuggestions] = useState<{text: string, source: string}[]>([])
  const [loadingSugg, setLoadingSugg] = useState(false)
  const [levelFilter, setLevelFilter] = useState<string>('')
  const [trackFilter, setTrackFilter] = useState<string>('')
  const [saving, setSaving] = useState(false)
  const [history, setHistory] = useState<{expected:string,transcribed:string,score:number,feedback:string,ts:string}[]>([])
  const [loadingHistory, setLoadingHistory] = useState(false)

  // Recording state
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const recorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<BlobPart[]>([])
  const audioUrlRef = useRef<string | null>(null)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const timerRef = useRef<number | null>(null)

  // Volume meter
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const audioCtxRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const rafRef = useRef<number | null>(null)

  // Speech recognition is now handled by LiveTranscriptionCard

  const stopMeter = () => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current)
    rafRef.current = null
    analyserRef.current = null
    if (audioCtxRef.current) {
      try { audioCtxRef.current.close() } catch {}
      audioCtxRef.current = null
    }
  }

  const drawMeter = useCallback(() => {
    const canvas = canvasRef.current
    const analyser = analyserRef.current
    if (!canvas || !analyser) return
    const ctx = canvas.getContext('2d')!
    const data = new Uint8Array(analyser.fftSize)
    analyser.getByteTimeDomainData(data)
    let rms = 0
    for (let i = 0; i < data.length; i++) {
      const v = (data[i] - 128) / 128
      rms += v * v
    }
    rms = Math.sqrt(rms / data.length)
    const level = Math.min(1, rms * 5)
    // draw
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    const w = canvas.width, h = canvas.height
    ctx.fillStyle = '#e5e7eb'
    ctx.fillRect(0, 0, w, h)
    ctx.fillStyle = '#10b981'
    ctx.fillRect(0, 0, Math.max(4, level * w), h)
    rafRef.current = requestAnimationFrame(drawMeter)
  }, [])

  // load practice suggestions
  const loadSuggestions = async () => {
    try {
      setLoadingSugg(true)
      const params: any = { size: 12 }
      if (levelFilter) params.level = levelFilter
      if (trackFilter) params.track = trackFilter
      const r = await api.get('/speech/suggestions', { params })
      setSuggestions(r.data || [])
    } catch {}
    finally { setLoadingSugg(false) }
  }
  useEffect(() => { loadSuggestions() }, [levelFilter, trackFilter])

  const saveAttempt = async () => {
    if (!serverResult) return
    try {
      setSaving(true)
      await api.post('/speech/save', {
        expected: serverResult.expected,
        transcribed: serverResult.transcribed,
        score: serverResult.score,
        feedback: serverResult.feedback,
      })
      await loadHistory()
    } catch {}
    finally { setSaving(false) }
  }

  const loadHistory = async () => {
    try {
      setLoadingHistory(true)
      const r = await api.get('/speech/history', { params: { limit: 10 } })
      setHistory(r.data || [])
    } catch {}
    finally { setLoadingHistory(false) }
  }
  useEffect(() => { loadHistory() }, [])

  // TTS playback for expected sentence
  const speakExpected = () => {
    try {
      const synth: SpeechSynthesis | undefined = window.speechSynthesis
      if (!synth) return
      const utter = new SpeechSynthesisUtterance(expected)
      // Try to pick a German voice if available
      const voices = synth.getVoices()
      const de = voices.find(v => /de(-|_)?DE/i.test(v.lang))
      if (de) utter.voice = de
      utter.lang = de?.lang || 'de-DE'
      synth.cancel()
      synth.speak(utter)
    } catch {}
  }

  const setupMeter = async (stream: MediaStream) => {
    audioCtxRef.current = new (window.AudioContext || (window as any).webkitAudioContext)()
    const source = audioCtxRef.current.createMediaStreamSource(stream)
    analyserRef.current = audioCtxRef.current.createAnalyser()
    analyserRef.current.fftSize = 2048
    source.connect(analyserRef.current)
    drawMeter()
  }

  const startTimer = () => {
    setElapsed(0)
    timerRef.current = window.setInterval(() => setElapsed((e) => e + 1), 1000) as unknown as number
  }
  const stopTimer = () => {
    if (timerRef.current) window.clearInterval(timerRef.current)
    timerRef.current = null
  }

  // Speech recognition moved to LiveTranscriptionCard component

  const startRecording = async () => {
    setError(null)
    setServerResult(null)
    setLocalTranscript('')
    setLocalScore(null)
    chunksRef.current = []
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaStreamRef.current = stream
      const rec = new MediaRecorder(stream)
      recorderRef.current = rec
      rec.ondataavailable = (e) => { if (e.data?.size) chunksRef.current.push(e.data) }
      rec.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: rec.mimeType || 'audio/webm' })
        if (audioUrlRef.current) URL.revokeObjectURL(audioUrlRef.current)
        const url = URL.createObjectURL(blob)
        audioUrlRef.current = url
        setAudioUrl(url)
      }
      await setupMeter(stream)
      rec.start()
      startTimer()
      setIsRecording(true)
    } catch (e: any) {
      setError('Microphone permission denied or unsupported in this browser.')
    }
  }

  const stopRecording = () => {
    stopTimer()
    try { recorderRef.current?.stop() } catch {}
    recorderRef.current = null
    mediaStreamRef.current?.getTracks().forEach(t => t.stop())
    mediaStreamRef.current = null
    stopMeter()
    setIsRecording(false)
  }

  const resetAll = () => {
    setServerResult(null)
    setLocalTranscript('')
    setLocalScore(null)
    setAudioUrl(null)
    if (audioUrlRef.current) { URL.revokeObjectURL(audioUrlRef.current); audioUrlRef.current = null }
  }

  const uploadForCheck = async () => {
    if (!audioUrl) {
      setError('No recording available. Please record first.')
      return
    }
    setError(null)
    setLoading(true)
    try {
      const blob = await fetch(audioUrl).then(r => r.blob())
      const fd = new FormData()
      fd.append('expected', expected)
      fd.append('file', blob, 'recording.webm')
      const r = await api.post('/speech/check', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      setServerResult(r.data)
    } catch (e: any) {
      // Keep the page useful even if backend AI is off
      setError('Server speech check unavailable. You can still use local feedback below.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => () => {
    // cleanup on unmount
    stopMeter()
    stopTimer()
    if (audioUrlRef.current) URL.revokeObjectURL(audioUrlRef.current)
    mediaStreamRef.current?.getTracks().forEach(t => t.stop())
  }, [])

  // Redirect unauthenticated users immediately
  // (RequireAuth performs the redirect on mount)
  
  return (
    <main className="space-y-4">
      <RequireAuth />
      <h2 className="text-xl font-semibold">Pronunciation Coach</h2>

      <div className="space-y-2">
        <label className="text-sm font-medium">Target sentence (DE)</label>
        <input className="input w-full" value={expected} onChange={(e)=>setExpected(e.target.value)} />
        <div className="flex items-center gap-3">
          <p className="text-xs text-gray-500">Tip: Keep it short (3–8 words) for best recognition.</p>
          <button type="button" className="btn btn-sm" onClick={speakExpected}>Listen (TTS)</button>
        </div>
      </div>

      {/* Recorder controls */}
      <div className="rounded-md border p-3 space-y-3">
        <div className="flex items-center gap-3">
          {!isRecording ? (
            <button className="btn" onClick={startRecording}>Start Recording</button>
          ) : (
            <button className="btn bg-red-600 hover:bg-red-700" onClick={stopRecording}>Stop</button>
          )}
          <span className="text-sm text-gray-600">{isRecording ? 'Recording…' : 'Not recording'}</span>
          <span className="ml-auto text-sm tabular-nums">{Math.floor(elapsed/60)}:{String(elapsed%60).padStart(2,'0')}</span>
        </div>
        <canvas ref={canvasRef} width={360} height={10} className="w-full rounded bg-gray-100" />
        <div className="flex items-center gap-3">
          <button className="btn" onClick={resetAll} disabled={isRecording}>Reset</button>
          <button className="btn" onClick={uploadForCheck} disabled={!audioUrl || isRecording}>Send to Coach</button>
          {audioUrl && (
            <audio className="ml-auto" controls src={audioUrl} />
          )}
        </div>
        {error && <p className="text-red-600 text-sm">{error}</p>}
      </div>

      {/* Live Transcription Card */}
      <LiveTranscriptionCard 
        expected={expected}
        isRecording={isRecording}
        onTranscriptUpdate={(transcript, score) => {
          setLocalTranscript(transcript)
          setLocalScore(score)
        }}
      />

      {/* Local feedback - simplified */}
      <div className="rounded-md border p-3 text-sm space-y-2">
        <h3 className="font-medium">Browser Compatibility</h3>
        <p className="text-gray-600">
          Live transcription works best in Chrome/Edge. If you don't see real-time feedback above, 
          your browser may not support the Web Speech API.
        </p>
        {localScore !== null && (
          <p className="text-gray-600">
            <strong>Tip:</strong> Aim for similar word order and endings. Try slower, clearer vowels and final consonants.
          </p>
        )}
      </div>

      {/* Server feedback if available */}
      {loading && (
        <div className="rounded-md border p-3 animate-pulse">
          <div className="h-4 w-1/3 rounded bg-gray-200 dark:bg-zinc-800" />
          <div className="mt-2 h-4 w-2/3 rounded bg-gray-200 dark:bg-zinc-800" />
          <div className="mt-2 h-20 rounded bg-gray-200 dark:bg-zinc-800" />
        </div>
      )}
      {serverResult && (
        <div className="rounded-md border p-3 text-sm space-y-2">
          <div><span className="font-semibold">Coach expected:</span> {serverResult.expected}</div>
          <div><span className="font-semibold">Coach heard:</span> {serverResult.transcribed}</div>
          <div>Score: {serverResult.score}</div>
          <div className="text-gray-600">{serverResult.feedback}</div>
          <div className="flex items-center gap-2 pt-1">
            <button className="btn btn-sm" onClick={saveAttempt} disabled={saving}>{saving ? 'Saving…' : 'Save attempt'}</button>
          </div>
          {serverResult.aligned && serverResult.aligned.length > 0 && (
            <div className="mt-2">
              <div className="text-xs text-gray-500 mb-1">Alignment</div>
              <div className="flex flex-wrap gap-1">
                {serverResult.aligned.map((t, i) => {
                  let bg = 'bg-green-100 text-green-800'
                  if (t.op === 'sub') bg = 'bg-amber-100 text-amber-800'
                  if (t.op === 'del') bg = 'bg-red-100 text-red-800'
                  if (t.op === 'ins') bg = 'bg-blue-100 text-blue-800'
                  const label = t.op === 'ins' ? (t.heard || '') : (t.expected || '')
                  return <span key={i} className={`px-2 py-0.5 rounded text-xs ${bg}`}>{label}</span>
                })}
              </div>
              <div className="text-xs text-gray-500 mt-1">Legend: green=match, amber=substitution, red=missed, blue=extra.</div>
            </div>
          )}
        </div>
      )}

      {/* Practice deck */}
      <div className="rounded-md border p-3 text-sm space-y-2">
        <div className="flex items-center gap-2">
          <h3 className="font-medium">Practice deck</h3>
          <button
            className="btn btn-sm inline-flex items-center gap-1 disabled:opacity-60 disabled:cursor-not-allowed"
            onClick={loadSuggestions}
            disabled={loadingSugg}
            aria-busy={loadingSugg}
            aria-label="Refresh practice suggestions"
            title="Refresh practice suggestions"
          >
            {loadingSugg && (
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="opacity-90 animate-spin" aria-hidden="true" focusable="false"><path d="M12 2a10 10 0 100 20 10 10 0 100-20Zm0 3a7 7 0 110 14 7 7 0 010-14Z" fill="#e5e7eb"/><path d="M12 2a10 10 0 00-7.07 2.93l2.12 2.12A7 7 0 0119 12h3A10 10 0 0012 2Z" fill="currentColor"/></svg>
            )}
            <span>{loadingSugg ? 'Refreshing' : 'Refresh'}</span>
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
          {suggestions.map((s, idx) => (
            <button key={idx} className="px-2 py-1 rounded border hover:bg-gray-50" onClick={()=>setExpected(s.text)} title={s.source}>{s.text}</button>
          ))}
          {suggestions.length === 0 && <span className="text-gray-500">No suggestions yet.</span>}
        </div>
      </div>

      {/* History */}
      <div className="rounded-md border p-3 text-sm space-y-2">
        <div className="flex items-center gap-2">
          <h3 className="font-medium">History</h3>
          <button
            className="btn btn-sm inline-flex items-center gap-1 disabled:opacity-60 disabled:cursor-not-allowed"
            onClick={loadHistory}
            disabled={loadingHistory}
            aria-busy={loadingHistory}
            aria-label="Refresh history"
            title="Refresh history"
          >
            {loadingHistory && (
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="opacity-90 animate-spin" aria-hidden="true" focusable="false"><path d="M12 2a10 10 0 100 20 10 10 0 100-20Zm0 3a7 7 0 110 14 7 7 0 010-14Z" fill="#e5e7eb"/><path d="M12 2a10 10 0 00-7.07 2.93l2.12 2.12A7 7 0 0119 12h3A10 10 0 0012 2Z" fill="currentColor"/></svg>
            )}
            <span>{loadingHistory ? 'Refreshing' : 'Refresh'}</span>
          </button>
        </div>
        <div className="space-y-1">
          {history.length === 0 && <div className="text-gray-500">No attempts saved yet.</div>}
          {history.map((h, i) => (
            <div key={i} className="rounded border px-2 py-1">
              <div className="flex items-center justify-between">
                <div className="font-medium">{h.score}%</div>
                <div className="text-xs text-gray-500">{new Date(h.ts).toLocaleString()}</div>
              </div>
              <div><span className="font-semibold">Exp:</span> {h.expected}</div>
              <div><span className="font-semibold">Heard:</span> {h.transcribed}</div>
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}
