"use client"
import React, { useEffect, useMemo, useRef, useState } from 'react'
import Link from 'next/link'
import api from '@/lib/api'
import { useAuth } from '@/store/auth'
import LiveTranscriptionCard from '@/components/LiveTranscriptionCard'

type ProgressDTO = {
  user_id: string
  streak: number
  words_learned: number
  quizzes_completed: number
  common_errors?: string[]
  badges?: string[]
}

export default function ClientDashboard() {
  const { userId } = useAuth()
  const [data, setData] = useState<ProgressDTO | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [mounted, setMounted] = useState(false)

  // Mini Pronunciation widget state
  const [recording, setRecording] = useState(false)
  const [score, setScore] = useState<number | null>(null)
  const [transcript, setTranscript] = useState('')
  const [confetti, setConfetti] = useState(false)
  const [currentSentence, setCurrentSentence] = useState('')

  // German sentences pool for mini pronunciation practice
  const sentencePool = [
    'Guten Morgen!',
    'Wie geht es dir?',
    'Ich bin müde.',
    'Das Wetter ist schön.',
    'Wo ist der Bahnhof?',
    'Ich hätte gern einen Kaffee.',
    'Entschuldigung, sprechen Sie Englisch?',
    'Vielen Dank für Ihre Hilfe.',
    'Ich verstehe nicht.',
    'Können Sie das wiederholen?'
  ]
  const [reduceMotion, setReduceMotion] = useState(false)
  const [lastPath, setLastPath] = useState<string | null>(null)
  const [weeklyData, setWeeklyData] = useState<number[] | null>(null)
  const [highStreak, setHighStreak] = useState<number>(0)
  const [showHighBadge, setShowHighBadge] = useState(false)

  // Mock weekly activity heatmap (7 days, simple counts)
  const weeklyActivity = useMemo(() => {
    // Generate a simple deterministic set based on words learned to make it feel data-driven
    const seed = (data?.words_learned ?? 7) % 7
    return new Array(7).fill(0).map((_, i) => ((i + seed) % 5))
  }, [data?.words_learned])

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!userId) return
    api
      .get(`/progress/${userId}`)
      .then((r) => setData(r.data))
      .catch(() => setError('Failed to load progress'))
    // Try to fetch weekly activity if backend supports it; ignore failures gracefully
    api
      .get(`/progress/${userId}/weekly`)
      .then((r) => {
        const arr = Array.isArray(r.data) ? r.data : r.data?.values
        if (Array.isArray(arr) && arr.length === 7) setWeeklyData(arr.map((n: any) => Number(n) || 0))
      })
      .catch(() => {})
  }, [userId])

  // Celebrate good pronunciation
  useEffect(() => {
    if (score !== null && score >= 85 && !reduceMotion) {
      setConfetti(true)
    }
  }, [score, reduceMotion])

  // Respect reduced motion preference
  useEffect(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    const update = () => setReduceMotion(!!mq.matches)
    update()
    mq.addEventListener?.('change', update)
    return () => mq.removeEventListener?.('change', update)
  }, [])

  // Load last session path from localStorage (set elsewhere in the app)
  useEffect(() => {
    if (typeof window === 'undefined') return
    try {
      const lp = localStorage.getItem('lastPath')
      if (lp && lp.startsWith('/')) setLastPath(lp)
      const hs = Number(localStorage.getItem('highStreak') || '0')
      if (!Number.isNaN(hs)) setHighStreak(hs)
    } catch {}
  }, [])

  // When data arrives, check for new high streak
  useEffect(() => {
    if (typeof window === 'undefined') return
    const current = data?.streak ?? 0
    if (current > highStreak) {
      try { localStorage.setItem('highStreak', String(current)) } catch {}
      setHighStreak(current)
      setShowHighBadge(true)
      const t = setTimeout(() => setShowHighBadge(false), 2500)
      return () => clearTimeout(t)
    }
  }, [data?.streak])

  const handleTranscriptUpdate = (newTranscript: string, newScore: number) => {
    setTranscript(newTranscript)
    setScore(newScore)
  }

  const getRandomSentence = () => {
    const randomIndex = Math.floor(Math.random() * sentencePool.length)
    return sentencePool[randomIndex]
  }

  const handleNewSentence = () => {
    setCurrentSentence(getRandomSentence())
    setScore(null)
    setTranscript('')
  }

  // Initialize with a random sentence on mount
  useEffect(() => {
    if (mounted && !currentSentence) {
      setCurrentSentence(getRandomSentence())
    }
  }, [mounted, currentSentence])

  if (!mounted) return null

  if (!userId)
    return (
      <p>
        Please <a className="underline" href="/login">login</a> to view your dashboard.
      </p>
    )

  return (
    <main className="space-y-6">
      {confetti && <ConfettiOverlay onDone={() => setConfetti(false)} />}
      {/* Hero */}
      <section className="rounded-xl border bg-gradient-to-br from-white/70 to-white/40 p-5 backdrop-blur dark:from-zinc-900/60 dark:to-zinc-900/40">
        <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <h2 className="text-2xl font-semibold">Welcome back{data ? ',' : ''} <span className="text-primary">Learner</span>!</h2>
            <p className="mt-1 text-sm text-gray-600 dark:text-zinc-400">
              Keep your streak alive and focus on one small win today.
            </p>
          </div>
          <Link href="/quiz" className="btn inline-flex items-center gap-2 hover:scale-[1.02] transition" aria-label="Start a quick quiz">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="opacity-90" aria-hidden="true"><path d="M12 3l2.09 4.24L18.82 8l-3.36 3.27.79 4.73L12 14.77 7.75 16l.79-4.73L5.18 8l4.73-.76L12 3z" fill="currentColor"/></svg>
            <span className="font-medium leading-none">Start a quick quiz</span>
          </Link>
          {lastPath && lastPath !== '/quiz' && (
            <Link href={lastPath} className="btn-outline inline-flex items-center gap-2" aria-label="Resume last session">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="opacity-90" aria-hidden="true"><path d="M12 5v4l4-2-4-2zm-6 7a6 6 0 1112 0 6 6 0 01-12 0zm-2 0a8 8 0 1016 0 8 8 0 00-16 0z" fill="currentColor"/></svg>
              <span className="font-medium leading-none">Resume last session</span>
            </Link>
          )}
        </div>
      </section>

      {error && <p className="text-red-600">{error}</p>}

      {/* KPI Cards */}
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard title="Streak" hint="days in a row">
          <div className="flex items-center gap-3">
            <div className="flex flex-col items-center">
              <ProgressRing value={data?.streak ?? 0} goal={30} size={56} animate={!reduceMotion} />
              <span className="mt-1 text-[10px] text-gray-500">Goal: 30d</span>
            </div>
            <div className="text-3xl font-bold">
              <AnimatedNumber value={data?.streak ?? 0} reduceMotion={reduceMotion} /> 🔥
            </div>
            {showHighBadge && (
              <span className="ml-1 inline-flex items-center rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800 dark:bg-amber-900/30 dark:text-amber-200">
                New high!
              </span>
            )}
          </div>
        </KpiCard>
        <KpiCard title="Words Learned" hint="total">
          <div className="text-3xl font-bold"><AnimatedNumber value={data?.words_learned ?? 0} reduceMotion={reduceMotion} /></div>
        </KpiCard>
        <KpiCard title="Quizzes" hint="completed">
          <div className="text-3xl font-bold"><AnimatedNumber value={data?.quizzes_completed ?? 0} reduceMotion={reduceMotion} /></div>
        </KpiCard>
        <KpiCard title="Focus" hint="common errors">
          <div className="flex items-start justify-between gap-2">
            <div className="truncate text-sm text-gray-700 dark:text-zinc-300">
              {data?.common_errors?.join(', ') || '—'}
            </div>
            <div className="relative ml-1 inline-block group" title="We surface common error themes from recent practice to guide a short focused review.">
              <span className="inline-flex h-5 w-5 items-center justify-center rounded-full border text-xs text-gray-500 group-hover:bg-gray-50 dark:group-hover:bg-zinc-900">i</span>
              <div className="pointer-events-none absolute right-0 z-10 hidden w-56 rounded-md border bg-white p-2 text-xs text-gray-700 shadow-md group-hover:block dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-200">
                We surface common error themes (e.g., articles, verb conjugation) so you can run a 2-minute mini-drill and improve faster.
              </div>
            </div>
          </div>
        </KpiCard>
      </section>

      {/* Interactive Row: Mini Pronunciation + Weekly Activity + Insights */}
      <section className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Mini Pronunciation */}
        <div className="rounded-xl border p-4">
          <div className="mb-2 flex items-center justify-between">
            <h3 className="font-medium">Mini Pronunciation</h3>
            <span className="text-xs text-green-600 font-medium">live</span>
          </div>
          <div className="mb-3 flex items-center justify-between">
            <p className="text-sm text-gray-600 dark:text-zinc-400">
              Say: <span className="font-medium">{currentSentence}</span>
            </p>
            <button 
              onClick={handleNewSentence}
              className="text-xs text-blue-600 hover:text-blue-800 underline"
              disabled={recording}
            >
              New
            </button>
          </div>
          
          {/* Recording Controls */}
          <div className="flex items-center gap-2 mb-3">
            {!recording ? (
              <button 
                onClick={() => setRecording(true)} 
                className="btn-outline inline-flex items-center gap-2 btn-sm"
              >
                <span className="inline-block h-2 w-2 rounded-full bg-red-500"></span>
                Record
              </button>
            ) : (
              <button 
                onClick={() => setRecording(false)} 
                className="inline-flex items-center gap-2 rounded-md bg-red-500 px-3 py-1.5 text-white shadow hover:brightness-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-400/50"
              >
                Stop
              </button>
            )}
          </div>

          {/* Live Transcription - Mini Version */}
          {currentSentence && (
            <div className="mb-3">
              <LiveTranscriptionCard 
                expected={currentSentence}
                isRecording={recording}
                onTranscriptUpdate={handleTranscriptUpdate}
              />
            </div>
          )}
          
          {/* Score Display */}
          <div className="text-sm text-gray-700 dark:text-zinc-300" aria-live="polite" aria-atomic="true">
            {score !== null ? (
              <span>Your score: <span className="font-semibold">{Math.round(score)}%</span>{score >= 90 ? ' 🎉' : score >= 70 ? ' 👍' : ' 💪'}</span>
            ) : (
              <span className="text-gray-500">Record to get live pronunciation feedback</span>
            )}
          </div>
        </div>

        {/* Weekly Activity Heatmap */}
        <div className="rounded-xl border p-4">
          <div className="mb-2 flex items-center justify-between">
            <h3 className="font-medium">This Week</h3>
            <span className="text-xs text-gray-500">activity</span>
          </div>
          <div className="grid grid-cols-7 gap-2">
            {(weeklyData ?? weeklyActivity).map((v, i) => (
              <div key={i} className="aspect-square w-full rounded-md border bg-gradient-to-br from-gray-50 to-white dark:from-zinc-950 dark:to-zinc-900">
                <div
                  className="h-full w-full rounded-md"
                  style={{
                    backgroundColor: levelToColor(v),
                  }}
                  title={`Day ${i + 1}: ${v} sessions`}
                />
              </div>
            ))}
          </div>
          <div className="mt-2 flex justify-between text-xs text-gray-500">
            <span>Mon</span>
            <span>Sun</span>
          </div>
        </div>

        {/* Insights */}
        <div className="rounded-xl border p-4">
          <div className="mb-2 flex items-center justify-between">
            <h3 className="font-medium">Smart Insight</h3>
            {data?.badges?.[0] && (
              <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300">
                {data.badges[0]}
              </span>
            )}
          </div>
          <p className="text-sm text-gray-700 dark:text-zinc-300">
            {buildInsight(data)}
          </p>
          <Link href="/vocab" className="mt-3 btn-outline inline-flex items-center gap-2 text-sm" aria-label="Review words">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className="opacity-90" aria-hidden="true"><path d="M4 6h16v2H4V6zm0 4h10v2H4v-2zm0 4h16v2H4v-2z" fill="currentColor"/></svg>
            <span className="leading-none">Review words</span>
          </Link>
        </div>
      </section>

      {/* Recent Activity (synthesized) */}
      <section className="rounded-xl border p-4">
        <div className="mb-2 flex items-center justify-between">
          <h3 className="font-medium">Recent Activity</h3>
          <span className="text-xs text-gray-500">last 3 highlights</span>
        </div>
        <ul className="divide-y divide-gray-200 dark:divide-zinc-800">
          {buildRecentActivity(data).map((item, idx) => (
            <li key={idx} className="flex items-center justify-between py-3">
              <div>
                <div className="font-medium">{item.title}</div>
                <div className="text-xs text-gray-500">{item.subtitle}</div>
              </div>
              <span className="text-xs text-gray-400">{item.when}</span>
            </li>
          ))}
        </ul>
      </section>
    </main>
  )
}

function KpiCard({ title, hint, children }: { title: string; hint?: string; children: React.ReactNode }) {
  return (
    <div className="group rounded-xl border p-4 transition hover:shadow-sm">
      <div className="mb-1 flex items-baseline justify-between">
        <span className="text-sm text-gray-500">{title}</span>
        {hint && <span className="text-xs text-gray-400">{hint}</span>}
      </div>
      <div className="translate-y-0 transition group-hover:-translate-y-0.5">{children}</div>
    </div>
  )
}


function levelToColor(level: number) {
  // 0..4
  const map = ['#e5e7eb', '#c7d2fe', '#a5b4fc', '#818cf8', '#6366f1']
  return map[Math.max(0, Math.min(4, level))]
}


function buildInsight(data: ProgressDTO | null): string {
  if (!data) return 'Loading your stats...'
  if ((data.words_learned ?? 0) < 20)
    return 'Add 5 new words today to build momentum. Small steps compound quickly.'
  if ((data.streak ?? 0) === 0)
    return 'Kickstart your streak with a 3-minute review session right now.'
  if ((data.quizzes_completed ?? 0) < 5)
    return 'Take a quick quiz to reinforce what you learned this week.'
  if (data.common_errors && data.common_errors.length)
    return `Target your weak spot: ${data.common_errors[0]}. Do a 2-minute mini-drill.`
  return 'Great consistency. Keep it up with a short review to close the loop.'
}

function buildRecentActivity(data: ProgressDTO | null): Array<{ title: string; subtitle: string; when: string }> {
  const now = new Date()
  const yesterday = new Date(now)
  yesterday.setDate(now.getDate() - 1)
  const twoDays = new Date(now)
  twoDays.setDate(now.getDate() - 2)

  const words = data?.words_learned ?? 0
  const quizzes = data?.quizzes_completed ?? 0
  const streak = data?.streak ?? 0
  const focus = data?.common_errors?.[0]

  const items: Array<{ title: string; subtitle: string; when: string }> = []
  items.push({
    title: `Learned ${Math.max(3, Math.min(12, (words % 15) + 3))} new words`,
    subtitle: 'Vocab builder session',
    when: formatDay(now),
  })
  items.push({
    title: `Completed ${Math.max(1, quizzes % 4)} quiz${(Math.max(1, quizzes % 4) > 1 ? 'zes' : '')}`,
    subtitle: 'Reinforced recent topics',
    when: formatDay(yesterday),
  })
  items.push({
    title: streak > 0 ? `Streak day ${streak}` : 'Started a new streak',
    subtitle: focus ? `Focus: ${focus}` : 'Daily practice',
    when: formatDay(twoDays),
  })
  return items
}

function formatDay(d: Date): string {
  const today = new Date()
  const diff = Math.floor((Date.UTC(today.getFullYear(), today.getMonth(), today.getDate()) - Date.UTC(d.getFullYear(), d.getMonth(), d.getDate())) / (1000 * 60 * 60 * 24))
  if (diff === 0) return 'Today'
  if (diff === 1) return 'Yesterday'
  return `${d.toLocaleDateString()}`
}

function AnimatedNumber({ value, duration = 600, reduceMotion = false }: { value: number; duration?: number; reduceMotion?: boolean }) {
  const [display, setDisplay] = useState(0)
  const startRef = useRef<number | null>(null)
  const fromRef = useRef(0)

  useEffect(() => {
    if (reduceMotion) {
      setDisplay(value)
      return
    }
    fromRef.current = display
    startRef.current = null
    let raf = 0
    const step = (ts: number) => {
      if (startRef.current == null) startRef.current = ts
      const progress = Math.min(1, (ts - startRef.current) / duration)
      const eased = 1 - Math.pow(1 - progress, 3)
      const next = Math.round(fromRef.current + (value - fromRef.current) * eased)
      setDisplay(next)
      if (progress < 1) raf = requestAnimationFrame(step)
    }
    raf = requestAnimationFrame(step)
    return () => cancelAnimationFrame(raf)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value, reduceMotion])

  return <span>{display.toLocaleString()}</span>
}

function ProgressRing({ value, goal = 30, size = 56, animate = false }: { value: number; goal?: number; size?: number; animate?: boolean }) {
  const pctTarget = Math.max(0, Math.min(1, value / goal))
  const [pct, setPct] = useState(pctTarget)
  useEffect(() => {
    if (!animate) {
      setPct(pctTarget)
      return
    }
    let raf = 0
    const startPct = pct
    const start = performance.now()
    const dur = 600
    const tick = (t: number) => {
      const prog = Math.min(1, (t - start) / dur)
      const eased = 1 - Math.pow(1 - prog, 3)
      setPct(startPct + (pctTarget - startPct) * eased)
      if (prog < 1) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pctTarget, animate])

  const stroke = 6
  const r = (size - stroke) / 2
  const c = 2 * Math.PI * r
  const dash = c * pct
  const colorClass = value > 20 ? 'text-emerald-500' : value >= 10 ? 'text-indigo-500' : 'text-zinc-400'
  return (
    <svg width={size} height={size} role="img" aria-label={`Streak ${value} of ${goal} days`} className={colorClass}>
      <circle cx={size / 2} cy={size / 2} r={r} stroke="#e5e7eb" strokeWidth={stroke} fill="none" />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        stroke="currentColor"
        strokeWidth={stroke}
        fill="none"
        strokeLinecap="round"
        strokeDasharray={`${dash} ${c - dash}`}
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
      />
    </svg>
  )
}

function ConfettiOverlay({ onDone }: { onDone?: () => void }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const timeoutRef = useRef<any>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')!
    let w = (canvas.width = window.innerWidth)
    let h = (canvas.height = window.innerHeight)
    const resize = () => {
      w = canvas.width = window.innerWidth
      h = canvas.height = window.innerHeight
    }
    window.addEventListener('resize', resize)

    type P = { x: number; y: number; vx: number; vy: number; c: string; s: number; a: number; r: number }
    const colors = ['#f59e0b', '#10b981', '#3b82f6', '#ef4444', '#a855f7']
    const parts: P[] = new Array(120).fill(0).map(() => ({
      x: Math.random() * w,
      y: -20 - Math.random() * 80,
      vx: (Math.random() - 0.5) * 2,
      vy: 2 + Math.random() * 3,
      c: colors[Math.floor(Math.random() * colors.length)],
      s: 4 + Math.random() * 4,
      a: Math.random() * Math.PI,
      r: Math.random() * Math.PI * 2,
    }))

    let raf = 0
    const tick = () => {
      if (!ctx) return
      ctx.clearRect(0, 0, w, h)
      parts.forEach((p) => {
        p.x += p.vx
        p.y += p.vy
        p.r += 0.1
        if (p.y > h + 20) {
          p.y = -20
          p.x = Math.random() * w
        }
        ctx.save()
        ctx.translate(p.x, p.y)
        ctx.rotate(p.r)
        ctx.fillStyle = p.c
        ctx.globalAlpha = 0.9
        ctx.fillRect(-p.s / 2, -p.s / 2, p.s, p.s * 0.6)
        ctx.restore()
      })
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)

    timeoutRef.current = setTimeout(() => {
      cancelAnimationFrame(raf)
      window.removeEventListener('resize', resize)
      onDone?.()
    }, 1500)

    return () => {
      cancelAnimationFrame(raf)
      clearTimeout(timeoutRef.current)
      window.removeEventListener('resize', resize)
    }
  }, [onDone])

  return (
    <div className="pointer-events-none fixed inset-0 z-50">
      <canvas ref={canvasRef} className="h-full w-full" />
    </div>
  )
}
