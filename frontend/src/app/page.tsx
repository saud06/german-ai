"use client"
import Link from 'next/link'
import { useAuth } from '@/store/auth'
import { useRouter } from 'next/navigation'

export default function Home() {
  const { token } = useAuth()
  const router = useRouter()
  return (
    <main className="space-y-16">
      {/* Hero */}
      <section className="relative overflow-hidden rounded-2xl border bg-gradient-to-br from-indigo-50 via-white to-pink-50 p-10 dark:from-zinc-800 dark:via-zinc-900 dark:to-zinc-800">
        <div className="max-w-3xl">
          <h2 className="text-3xl md:text-5xl font-extrabold tracking-tight">
            Learn German smarter with AI guidance
          </h2>
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-300">
            Personalized practice across vocabulary, grammar, pronunciation, and quizzes. Progress at your pace—online or offline.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="#features" className="inline-flex items-center rounded-md bg-indigo-600 px-4 py-2 text-white shadow hover:bg-indigo-700 transition">
              Explore Features
            </Link>
            <Link href={token ? "/dashboard" : "/login"} className="inline-flex items-center rounded-md border px-4 py-2 hover:bg-gray-50 dark:hover:bg-zinc-800 transition">
              Go to Dashboard
            </Link>
          </div>
        </div>
        <div className="pointer-events-none absolute -right-10 -top-10 h-64 w-64 rounded-full bg-indigo-200/60 blur-3xl dark:bg-indigo-500/20" />
      </section>

      {/* Feature grid */}
      <section id="features" className="space-y-8">
        <h3 className="text-2xl font-semibold">Everything you need to master German</h3>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <Link href={token ? "/vocab" : "/login"} className="group rounded-xl border p-6 hover:shadow-md transition bg-white dark:bg-zinc-900">
            <div className="text-indigo-600 group-hover:scale-110 transition transform">🧠</div>
            <h4 className="mt-3 font-semibold">Smart Vocabulary</h4>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Adaptive spaced repetition and themed word sets.</p>
            <span className="mt-3 inline-block text-sm text-indigo-600">Practice Vocab →</span>
          </Link>
          <Link href={token ? "/grammar" : "/login"} className="group rounded-xl border p-6 hover:shadow-md transition bg-white dark:bg-zinc-900">
            <div className="text-indigo-600 group-hover:scale-110 transition transform">⚙️</div>
            <h4 className="mt-3 font-semibold">Grammar</h4>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Clear explanations with instant, contextual feedback.</p>
            <span className="mt-3 inline-block text-sm text-indigo-600">Open Grammar →</span>
          </Link>
          <Link href={token ? "/speech" : "/login"} className="group rounded-xl border p-6 hover:shadow-md transition bg-white dark:bg-zinc-900">
            <div className="text-indigo-600 group-hover:scale-110 transition transform">🗣️</div>
            <h4 className="mt-3 font-semibold">Pronunciation</h4>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Listen, repeat, and get feedback on your pronunciation.</p>
            <span className="mt-3 inline-block text-sm text-indigo-600">Try Speaking →</span>
          </Link>
          <Link href={token ? "/quiz" : "/login"} className="group rounded-xl border p-6 hover:shadow-md transition bg-white dark:bg-zinc-900">
            <div className="text-indigo-600 group-hover:scale-110 transition transform">📝</div>
            <h4 className="mt-3 font-semibold">Quizzes</h4>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Test your knowledge with dynamic, AI-assisted quizzes.</p>
            <span className="mt-3 inline-block text-sm text-indigo-600">Start a Quiz →</span>
          </Link>
        </div>
      </section>

      {/* Social proof */}
      <section className="rounded-xl border p-6 bg-white dark:bg-zinc-900">
        <div className="grid gap-6 md:grid-cols-3">
          <div>
            <div className="text-3xl font-bold">+1,000</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">practice prompts available</div>
          </div>
          <div>
            <div className="text-3xl font-bold">Adaptive</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">content tuned to your level</div>
          </div>
          <div>
            <div className="text-3xl font-bold">AI-first</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">authentic content powered by AI and curated data</div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="text-center">
        <p className="text-gray-600 dark:text-gray-400">Ready to learn? Jump into a section below.</p>
        <div className="mt-4 flex flex-wrap justify-center gap-3">
          <Link href={token ? "/vocab" : "/login"} className="rounded-md border px-4 py-2 hover:bg-gray-50 dark:hover:bg-zinc-800">Vocab</Link>
          <Link href={token ? "/grammar" : "/login"} className="rounded-md border px-4 py-2 hover:bg-gray-50 dark:hover:bg-zinc-800">Grammar</Link>
          <Link href={token ? "/quiz" : "/login"} className="rounded-md border px-4 py-2 hover:bg-gray-50 dark:hover:bg-zinc-800">Quiz</Link>
          <Link href={token ? "/speech" : "/login"} className="rounded-md border px-4 py-2 hover:bg-gray-50 dark:hover:bg-zinc-800">Pronunciation</Link>
        </div>
      </section>
    </main>
  )
}
