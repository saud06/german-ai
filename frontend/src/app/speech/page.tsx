"use client"
import React, { useCallback, useEffect, useRef, useState } from 'react'
import RequireAuth from '@/components/RequireAuth'
import MiniTranscriptionCard from '@/components/MiniTranscriptionCard'
import api from '@/lib/api'
import { useAuth } from '@/store/auth'
import { useRouter } from 'next/navigation'
import { useJourney } from '@/contexts/JourneyContext'
import { getJourneyLevels } from '@/lib/levelUtils'

type SpeechResult = {
  expected: string
  transcribed: string
  score: number
  feedback: string
  aligned?: { expected?: string | null; heard?: string | null; op: 'ok'|'sub'|'del'|'ins' }[]
}

// Fallback minimal BlobEvent type for browsers where TypeScript lib lacks it
type BlobEvent = { data: Blob }

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

function calculateWordScore(expectedWord: string, spokenWord: string): number {
  const exp = expectedWord.toLowerCase().trim()
  const spoken = spokenWord.toLowerCase().trim()
  
  if (exp === spoken) return 100
  if (exp.includes(spoken) || spoken.includes(exp)) return 75
  
  const maxLen = Math.max(exp.length, spoken.length)
  if (maxLen === 0) return 100
  
  let matches = 0
  const minLen = Math.min(exp.length, spoken.length)
  for (let i = 0; i < minLen; i++) {
    if (exp[i] === spoken[i]) matches++
  }
  
  return Math.round((matches / maxLen) * 100)
}

export default function SpeechPage() {
  const { userId } = useAuth()
  const { activeJourney } = useJourney()
  const journeyLevels = getJourneyLevels(activeJourney)
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
  const [isParagraphMode, setIsParagraphMode] = useState(false)
  const [paragraph, setParagraph] = useState<{title: string; sentences: string[]} | null>(null)
  const [currentSentenceIndex, setCurrentSentenceIndex] = useState(0)
  const [isGeneratingParagraph, setIsGeneratingParagraph] = useState(false)
  // TTS paragraph progress
  const [ttsSpeaking, setTtsSpeaking] = useState(false)
  const [ttsWordIndex, setTtsWordIndex] = useState<number>(-1)
  const ttsTokensRef = useRef<{text:string; start:number; end:number; isWord:boolean}[]>([])
  const ttsUttRef = useRef<SpeechSynthesisUtterance | null>(null)

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

  // Paragraph mode helpers
  const generateNewParagraph = async () => {
    if (isGeneratingParagraph) return
    setIsGeneratingParagraph(true)
    try {
      const r = await api.get('/paragraph/generate')
      const data = r.data as { title: string; sentences: string[] }
      setParagraph(data)
      setCurrentSentenceIndex(0)
      // In paragraph mode, expected should be the entire paragraph
      setExpected((data.sentences || []).join(' '))
      // reset feedback state when switching content
      setServerResult(null)
      setLocalTranscript('')
      setLocalScore(null)
    } catch (e) {
      setError('Failed to generate paragraph. Please try again.')
    } finally {
      setIsGeneratingParagraph(false)
    }
  }

  const handleNextSentence = () => {
    if (!paragraph) return
    const next = currentSentenceIndex + 1
    if (next < paragraph.sentences.length) {
      setCurrentSentenceIndex(next)
      setExpected(paragraph.sentences[next] || '')
      setServerResult(null)
      setLocalTranscript('')
      setLocalScore(null)
    }
  }

  const handlePrevSentence = () => {
    if (!paragraph) return
    const prev = currentSentenceIndex - 1
    if (prev >= 0) {
      setCurrentSentenceIndex(prev)
      setExpected(paragraph.sentences[prev] || '')
      setServerResult(null)
      setLocalTranscript('')
      setLocalScore(null)
    }
  }

  const toggleParagraphMode = async () => {
    const newMode = !isParagraphMode
    setIsParagraphMode(newMode)
    if (newMode) {
      await generateNewParagraph()
    } else {
      setParagraph(null)
      setCurrentSentenceIndex(0)
      // keep current expected or reset to a simple default
      if (!expected) setExpected('Ich gehe zur Schule.')
      // stop paragraph TTS if any
      try { window.speechSynthesis?.cancel(); } catch {}
      setTtsSpeaking(false)
      setTtsWordIndex(-1)
      setServerResult(null)
      setLocalTranscript('')
      setLocalScore(null)
    }
  }

  // If user toggles into paragraph mode with no data yet, fetch one
  useEffect(() => {
    if (isParagraphMode && !paragraph && !isGeneratingParagraph) {
      generateNewParagraph()
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isParagraphMode])

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

  // Build token map for paragraph TTS highlighting
  const buildParagraphTokens = useCallback((text: string) => {
    const tokens: {text:string; start:number; end:number; isWord:boolean}[] = []
    let idx = 0
    const re = /[\wÄÖÜäöüß]+|[^\w\s]+|\s+/g
    let m: RegExpExecArray | null
    while ((m = re.exec(text)) !== null) {
      const t = m[0]
      const start = idx
      const end = idx + t.length
      const isWord = /[\wÄÖÜäöüß]/.test(t[0] || '')
      tokens.push({ text: t, start, end, isWord })
      idx = end
    }
    return tokens
  }, [])

  const speakParagraph = () => {
    if (!paragraph) return
    try {
      const synth: SpeechSynthesis | undefined = window.speechSynthesis
      if (!synth) return
      // Cancel any ongoing
      try { synth.cancel() } catch {}
      setTtsWordIndex(-1)

      const fullText = (paragraph.sentences || []).join(' ')
      const tokens = buildParagraphTokens(fullText)
      ttsTokensRef.current = tokens

      const utter = new SpeechSynthesisUtterance(fullText)
      // Set German
      const voices = synth.getVoices()
      const de = voices.find(v => /de(-|_)?DE/i.test(v.lang))
      if (de) utter.voice = de
      utter.lang = de?.lang || 'de-DE'

      utter.onstart = () => {
        setTtsSpeaking(true)
      }
      utter.onend = () => {
        setTtsSpeaking(false)
        setTtsWordIndex(-1)
        ttsUttRef.current = null
      }
      utter.onerror = () => {
        setTtsSpeaking(false)
        setTtsWordIndex(-1)
        ttsUttRef.current = null
      }
      utter.onboundary = (ev: any) => {
        // ev.charIndex is where current spoken fragment starts
        const ci = ev.charIndex as number
        const toks = ttsTokensRef.current
        // find the first word token with start <= ci < end
        let idx = -1
        for (let i = 0; i < toks.length; i++) {
          const tk = toks[i]
          if (!tk.isWord) continue
          if (ci >= tk.start && ci < tk.end) { idx = i; break }
        }
        if (idx !== -1) setTtsWordIndex(idx)
      }
      ttsUttRef.current = utter
      synth.speak(utter)
    } catch {}
  }

  const stopParagraphTTS = () => {
    try { window.speechSynthesis?.cancel() } catch {}
    setTtsSpeaking(false)
    setTtsWordIndex(-1)
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
    timerRef.current = window.setInterval(() => setElapsed((e: number) => e + 1), 1000) as unknown as number
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
      rec.ondataavailable = (e: BlobEvent) => { if ((e as BlobEvent).data?.size) chunksRef.current.push((e as BlobEvent).data) }
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
    mediaStreamRef.current?.getTracks().forEach((t: MediaStreamTrack) => t.stop())
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
      const expectedForCheck = isParagraphMode && paragraph ? (paragraph.sentences || []).join(' ') : expected
      fd.append('expected', expectedForCheck)
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
    mediaStreamRef.current?.getTracks().forEach((t: MediaStreamTrack) => t.stop())
  }, [])

  // Redirect unauthenticated users immediately
  // (RequireAuth performs the redirect on mount)
  
  const router = useRouter()

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900">
      <RequireAuth />
      
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/dashboard')}
            className="mb-4 text-purple-600 dark:text-purple-400 hover:text-purple-800 dark:hover:text-purple-300 flex items-center font-medium transition-colors"
          >
            ← Back to Dashboard
          </button>
          <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4 flex items-center justify-center gap-3">
            🎙️ Speech Practice
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Practice your German pronunciation with AI-powered feedback
          </p>
          
          {/* Paragraph Mode Toggle */}
          <div className="mt-6 flex justify-center">
            <button
              onClick={toggleParagraphMode}
              disabled={isGeneratingParagraph}
              className={`px-6 py-3 rounded-xl font-bold transition-all shadow-lg hover:shadow-xl flex items-center gap-2 ${
                isParagraphMode
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              📖 {isParagraphMode ? 'Exit Paragraph Mode' : 'Paragraph Mode'}
              {isGeneratingParagraph && <span className="animate-spin">⏳</span>}
            </button>
          </div>
        </div>
        </div>

        {/* Main Practice Card */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-6">
          <div className="space-y-6">
            {/* Paragraph Mode Info */}
            {isParagraphMode && paragraph && (
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-6 border-2 border-blue-200 dark:border-blue-800">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-blue-900 dark:text-blue-100">
                    📖 {paragraph.title}
                  </h3>
                  <button
                    onClick={generateNewParagraph}
                    disabled={isGeneratingParagraph}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    🔄 New Paragraph
                  </button>
                </div>
                <div className="flex items-center gap-3 mb-4">
                  <button
                    onClick={handlePrevSentence}
                    disabled={currentSentenceIndex === 0}
                    className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-semibold hover:bg-gray-300 dark:hover:bg-gray-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    ← Previous
                  </button>
                  <span className="text-sm font-semibold text-blue-900 dark:text-blue-100">
                    Sentence {currentSentenceIndex + 1} of {paragraph.sentences.length}
                  </span>
                  <button
                    onClick={handleNextSentence}
                    disabled={currentSentenceIndex === paragraph.sentences.length - 1}
                    className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-semibold hover:bg-gray-300 dark:hover:bg-gray-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next →
                  </button>
                  <button
                    onClick={speakParagraph}
                    className="ml-auto px-4 py-2 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition-all"
                  >
                    🔊 Read Full Paragraph
                  </button>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
                  <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                    {paragraph.sentences.map((sentence, idx) => (
                      <span
                        key={idx}
                        className={`${
                          idx === currentSentenceIndex
                            ? 'bg-yellow-200 dark:bg-yellow-700 font-bold'
                            : ''
                        }`}
                      >
                        {sentence}{' '}
                      </span>
                    ))}
                  </p>
                </div>
              </div>
            )}

            {/* Target Sentence Input - Only show in single sentence mode */}
            {!isParagraphMode && (
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  🎯 Target Sentence (German)
                </label>
                <div className="flex gap-3">
                  <input 
                    className="flex-1 px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:border-purple-600 focus:ring-2 focus:ring-purple-200 dark:bg-gray-700 dark:text-white text-lg transition-all" 
                    value={expected} 
                    onChange={(e)=>setExpected(e.target.value)}
                    placeholder="Enter a German sentence..."
                  />
                  <button 
                    type="button" 
                    className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-bold hover:from-purple-700 hover:to-pink-700 transition-all shadow-lg hover:shadow-xl flex items-center gap-2"
                    onClick={speakExpected}
                  >
                    🔊 Listen
                  </button>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 italic">
                  💡 Tip: Keep it short (3–8 words) for best recognition
                </p>
              </div>
            )}

            {/* Recording Controls */}
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-gray-700 dark:to-gray-600 rounded-xl p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  {!isRecording ? (
                    <button 
                      className="px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-bold hover:from-green-600 hover:to-emerald-700 transition-all shadow-lg hover:shadow-xl flex items-center gap-2 text-lg"
                      onClick={startRecording}
                    >
                      🎤 Start Recording
                    </button>
                  ) : (
                    <button 
                      className="px-8 py-4 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl font-bold hover:from-red-600 hover:to-red-700 transition-all shadow-lg hover:shadow-xl flex items-center gap-2 text-lg animate-pulse"
                      onClick={stopRecording}
                    >
                      ⏹️ Stop Recording
                    </button>
                  )}
                  <div className="flex flex-col">
                    <span className={`text-sm font-semibold ${isRecording ? 'text-red-600 dark:text-red-400' : 'text-gray-600 dark:text-gray-400'}`}>
                      {isRecording ? '🔴 Recording...' : '⚪ Ready'}
                    </span>
                    <span className="text-2xl font-mono font-bold text-gray-700 dark:text-gray-300 tabular-nums">
                      {Math.floor(elapsed/60)}:{String(elapsed%60).padStart(2,'0')}
                    </span>
                  </div>
                </div>
              </div>
              
              {/* Volume Meter */}
              <div className="space-y-2">
                <p className="text-xs font-medium text-gray-600 dark:text-gray-400">Volume Level</p>
                <canvas ref={canvasRef} width={360} height={16} className="w-full rounded-lg shadow-inner" />
              </div>
              
              {/* Action Buttons */}
              <div className="flex items-center gap-3 pt-2">
                <button 
                  className="px-6 py-3 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-xl font-bold hover:bg-gray-300 dark:hover:bg-gray-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  onClick={resetAll} 
                  disabled={isRecording}
                >
                  🔄 Reset
                </button>
                <button 
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-bold hover:from-indigo-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  onClick={uploadForCheck} 
                  disabled={!audioUrl || isRecording}
                >
                  🎓 Send to AI Coach
                </button>
              </div>
              
              {/* Audio Playback */}
              {audioUrl && (
                <div className="pt-2">
                  <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">Your Recording:</p>
                  <audio className="w-full" controls src={audioUrl} />
                </div>
              )}
              
              {error && (
                <div className="bg-red-100 dark:bg-red-900 border-2 border-red-300 dark:border-red-700 text-red-700 dark:text-red-200 px-4 py-3 rounded-xl text-sm font-medium">
                  ⚠️ {error}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Live Feedback Card with Word-by-Word Analysis */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">📊 Live Feedback</h3>
            <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full text-xs font-medium">Real-time</span>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Real-time transcription and word-by-word analysis as you speak
          </p>
          
          <div className="space-y-4">
            {/* Expected vs Spoken Comparison */}
            <div className="grid md:grid-cols-2 gap-4">
              <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-gray-700 dark:to-gray-600 rounded-xl p-4">
                <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Expected:</p>
                <p className="text-base font-medium text-gray-900 dark:text-white">{expected}</p>
              </div>
              
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-700 dark:to-gray-600 rounded-xl p-4">
                <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">You're Saying:</p>
                {localTranscript ? (
                  <div className="flex flex-wrap gap-2">
                    {localTranscript.split(/\s+/).filter(w => w.length > 0).map((word, index) => {
                      const expectedWords = expected.toLowerCase().split(/\s+/).filter(w => w.length > 0)
                      const expectedWord = expectedWords[index]
                      const cleanWord = word.toLowerCase().replace(/[.,!?]/g, '')
                      
                      let colorClass = 'bg-gray-100 text-gray-700 border-gray-300'
                      if (expectedWord) {
                        const score = calculateWordScore(expectedWord, cleanWord)
                        if (score >= 90) {
                          colorClass = 'bg-green-100 text-green-800 border-green-300 dark:bg-green-900 dark:text-green-200 dark:border-green-700'
                        } else if (score >= 70) {
                          colorClass = 'bg-yellow-100 text-yellow-800 border-yellow-300 dark:bg-yellow-900 dark:text-yellow-200 dark:border-yellow-700'
                        } else {
                          colorClass = 'bg-red-100 text-red-800 border-red-300 dark:bg-red-900 dark:text-red-200 dark:border-red-700'
                        }
                      } else {
                        colorClass = 'bg-blue-100 text-blue-800 border-blue-300 dark:bg-blue-900 dark:text-blue-200 dark:border-blue-700'
                      }
                      
                      return (
                        <span
                          key={index}
                          className={`px-3 py-1.5 text-sm font-medium border-2 rounded-lg ${colorClass} transition-all duration-300`}
                        >
                          {word}
                        </span>
                      )
                    })}
                  </div>
                ) : (
                  <p className="text-base font-medium text-gray-400 italic">Listening...</p>
                )}
              </div>
            </div>
            
            {/* Score Display */}
            {localScore !== null && (
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-gray-700 dark:to-gray-600 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs font-semibold text-gray-600 dark:text-gray-400">Accuracy Score:</p>
                  <span className={`text-2xl font-bold ${
                    localScore >= 80 ? 'text-green-600' : 
                    localScore >= 60 ? 'text-yellow-600' : 
                    'text-red-600'
                  }`}>
                    {localScore}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-3 overflow-hidden">
                  <div 
                    className={`h-3 rounded-full transition-all duration-500 ${
                      localScore >= 80 ? 'bg-green-500' : 
                      localScore >= 60 ? 'bg-yellow-500' : 
                      'bg-red-500'
                    }`}
                    style={{ width: `${localScore}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Mini Transcription Card */}
        <MiniTranscriptionCard 
          expected={expected}
          isRecording={isRecording}
          onTranscriptUpdate={(transcript, score) => {
            setLocalTranscript(transcript)
            setLocalScore(score)
          }}
        />

        {/* AI Coach Feedback */}
        {loading && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-6 animate-pulse">
            <div className="h-6 w-1/3 rounded-lg bg-gray-200 dark:bg-gray-700 mb-4" />
            <div className="h-4 w-2/3 rounded bg-gray-200 dark:bg-gray-700 mb-2" />
            <div className="h-24 rounded-lg bg-gray-200 dark:bg-gray-700" />
          </div>
        )}
        
        {serverResult && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 mb-6">
            <div className="flex items-center gap-2 mb-4">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">🎓 AI Coach Feedback</h3>
              <span className="px-3 py-1 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded-full text-xs font-medium">AI-Powered</span>
            </div>
            
            <div className="space-y-4">
              {/* Score Display */}
              <div className="bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-gray-700 dark:to-gray-600 rounded-xl p-6 text-center">
                <p className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">Your Score</p>
                <div className={`text-6xl font-bold mb-2 ${
                  serverResult.score >= 80 ? 'text-green-600' : 
                  serverResult.score >= 60 ? 'text-yellow-600' : 
                  'text-red-600'
                }`}>
                  {serverResult.score}%
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-4 overflow-hidden max-w-md mx-auto">
                  <div 
                    className={`h-4 rounded-full transition-all duration-500 ${
                      serverResult.score >= 80 ? 'bg-green-500' : 
                      serverResult.score >= 60 ? 'bg-yellow-500' : 
                      'bg-red-500'
                    }`}
                    style={{ width: `${serverResult.score}%` }}
                  />
                </div>
              </div>
              
              {/* Comparison */}
              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-purple-50 dark:bg-gray-700 rounded-xl p-4">
                  <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">Expected:</p>
                  <p className="text-base font-medium text-gray-900 dark:text-white">{serverResult.expected}</p>
                </div>
                <div className="bg-blue-50 dark:bg-gray-700 rounded-xl p-4">
                  <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">What AI Heard:</p>
                  <p className="text-base font-medium text-gray-900 dark:text-white">{serverResult.transcribed}</p>
                </div>
              </div>
              
              {/* Feedback */}
              <div className="bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-gray-700 dark:to-gray-600 rounded-xl p-4">
                <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">💬 Coach's Feedback:</p>
                <p className="text-sm text-gray-700 dark:text-gray-300">{serverResult.feedback}</p>
              </div>
              
              {/* Word Alignment */}
              {serverResult.aligned && serverResult.aligned.length > 0 && (
                <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-4">
                  <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-3">🔍 Word-by-Word Analysis</p>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {serverResult.aligned.map((t, i) => {
                      let bg = 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                      if (t.op === 'sub') bg = 'bg-amber-100 dark:bg-amber-900 text-amber-800 dark:text-amber-200'
                      if (t.op === 'del') bg = 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                      if (t.op === 'ins') bg = 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200'
                      const label = t.op === 'ins' ? (t.heard || '') : (t.expected || '')
                      return <span key={i} className={`px-3 py-1.5 rounded-lg text-sm font-medium ${bg}`}>{label}</span>
                    })}
                  </div>
                  <div className="flex flex-wrap gap-3 text-xs">
                    <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-green-500"></span> Match</span>
                    <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-amber-500"></span> Substitution</span>
                    <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-red-500"></span> Missed</span>
                    <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-blue-500"></span> Extra</span>
                  </div>
                </div>
              )}
              
              {/* Save Button */}
              <button 
                className="w-full px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl font-bold hover:from-green-700 hover:to-emerald-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                onClick={saveAttempt} 
                disabled={saving}
              >
                {saving ? '💾 Saving...' : '💾 Save to History'}
              </button>
            </div>
          </div>
        )}

        {/* Practice Deck */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">📚 Practice Deck</h3>
              <span className="px-3 py-1 bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 rounded-full text-xs font-medium">Suggestions</span>
            </div>
            <button
              className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-bold hover:from-indigo-700 hover:to-purple-700 transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              onClick={loadSuggestions}
              disabled={loadingSugg}
            >
              {loadingSugg && (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className="animate-spin">
                  <path d="M12 2a10 10 0 100 20 10 10 0 100-20Zm0 3a7 7 0 110 14 7 7 0 010-14Z" fill="#e5e7eb"/>
                  <path d="M12 2a10 10 0 00-7.07 2.93l2.12 2.12A7 7 0 0119 12h3A10 10 0 0012 2Z" fill="currentColor"/>
                </svg>
              )}
              <span>{loadingSugg ? 'Loading...' : '🔄 Refresh'}</span>
            </button>
          </div>
          
          {/* Filters */}
          <div className="flex flex-wrap items-center gap-3 mb-4">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Level:</span>
              <select
                className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
                value={levelFilter}
                onChange={(e)=>setLevelFilter(e.target.value)}
              >
                <option value="">All Levels</option>
                {journeyLevels.map((level) => (
                  <option key={level} value={level}>{level}</option>
                ))}
              </select>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Topic:</span>
              <select 
                className="px-3 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg focus:border-purple-600 focus:ring-2 focus:ring-purple-200 dark:bg-gray-700 dark:text-white text-sm font-medium" 
                value={trackFilter} 
                onChange={(e)=>setTrackFilter(e.target.value)}
              >
                <option value="">All Topics</option>
                <option value="articles">Articles</option>
                <option value="verbs">Verbs</option>
                <option value="nouns">Nouns</option>
                <option value="cases">Cases</option>
                <option value="pluralization">Pluralization</option>
              </select>
            </div>
          </div>
          
          {/* Suggestions Grid */}
          <div className="flex flex-wrap gap-2">
            {suggestions.map((s, idx) => (
              <button 
                key={idx} 
                className="px-4 py-2 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-gray-700 dark:to-gray-600 border-2 border-purple-200 dark:border-purple-700 rounded-lg hover:from-purple-100 hover:to-pink-100 dark:hover:from-gray-600 dark:hover:to-gray-500 transition-all font-medium text-gray-900 dark:text-white text-sm" 
                onClick={()=>setExpected(s.text)} 
                title={s.source}
              >
                {s.text}
              </button>
            ))}
            {suggestions.length === 0 && (
              <div className="w-full text-center py-8 text-gray-500 dark:text-gray-400">
                <p className="text-lg">📭 No suggestions available</p>
                <p className="text-sm mt-1">Try adjusting the filters or click Refresh</p>
              </div>
            )}
          </div>
        </div>

        {/* History */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">📜 Practice History</h3>
              <span className="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-full text-xs font-medium">{history.length} attempts</span>
            </div>
            <button
              className="px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg font-bold hover:from-green-700 hover:to-emerald-700 transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              onClick={loadHistory}
              disabled={loadingHistory}
            >
              {loadingHistory && (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className="animate-spin">
                  <path d="M12 2a10 10 0 100 20 10 10 0 100-20Zm0 3a7 7 0 110 14 7 7 0 010-14Z" fill="#e5e7eb"/>
                  <path d="M12 2a10 10 0 00-7.07 2.93l2.12 2.12A7 7 0 0119 12h3A10 10 0 0012 2Z" fill="currentColor"/>
                </svg>
              )}
              <span>{loadingHistory ? 'Loading...' : '🔄 Refresh'}</span>
            </button>
          </div>
          
          <div className="space-y-3">
            {history.length === 0 && (
              <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                <p className="text-lg">📭 No practice history yet</p>
                <p className="text-sm mt-1">Your saved attempts will appear here</p>
              </div>
            )}
            {history.map((h, i) => (
              <div key={i} className="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-600 rounded-xl p-4 border-2 border-gray-200 dark:border-gray-600">
                <div className="flex items-center justify-between mb-2">
                  <div className={`text-2xl font-bold ${
                    h.score >= 80 ? 'text-green-600' : 
                    h.score >= 60 ? 'text-yellow-600' : 
                    'text-red-600'
                  }`}>
                    {h.score}%
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 font-medium">
                    🕐 {new Date(h.ts).toLocaleString()}
                  </div>
                </div>
                <div className="space-y-1 text-sm">
                  <div className="flex items-start gap-2">
                    <span className="font-semibold text-gray-600 dark:text-gray-400 min-w-[60px]">Expected:</span>
                    <span className="text-gray-900 dark:text-white font-medium">{h.expected}</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="font-semibold text-gray-600 dark:text-gray-400 min-w-[60px]">You said:</span>
                    <span className="text-gray-900 dark:text-white">{h.transcribed}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
