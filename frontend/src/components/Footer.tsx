"use client"
import Link from 'next/link'
import { APP_VERSION } from '@/lib/appInfo'
import { useAuth } from '@/store/auth'
import { usePathname } from 'next/navigation'
import { useEffect, useState } from 'react'

export default function Footer() {
  const year = new Date().getFullYear()
  const { token } = useAuth()
  const pathname = usePathname()
  const [mounted, setMounted] = useState(false)
  
  // Prevent hydration mismatch by only checking auth after mount
  useEffect(() => {
    setMounted(true)
  }, [])
  
  const hasAuth = mounted && !!token
  const gate = (href: string) => (hasAuth ? href : '/login')

  // Decide layout: full only on home
  const isHome = pathname === '/'

  return (
    <footer className="mt-12 select-none">
      {isHome ? (
        <div className="rounded-xl border bg-white/70 p-4 sm:p-5 dark:bg-zinc-900/60 backdrop-blur supports-[backdrop-filter]:bg-white/60">
          <div className="grid gap-5 sm:gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <div className="text-lg font-semibold">German AI Learner</div>
            <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
              Learn smarter with focused practice across vocab, grammar, pronunciation, and quizzes.
            </p>
            <div className="mt-3 text-xs text-zinc-500">v{APP_VERSION}</div>
          </div>
          <div className="text-sm">
            <div className="font-medium mb-1">Explore</div>
            <div className="flex flex-col gap-1">
              <Link href={gate('/vocab')} className="hover:underline">Vocab</Link>
              <Link href={gate('/grammar')} className="hover:underline">Grammar</Link>
              <Link href={gate('/speech')} className="hover:underline">Pronunciation</Link>
              <Link href={gate('/quiz')} className="hover:underline">Quiz</Link>
            </div>
          </div>
          <div className="text-sm">
            <div className="font-medium mb-1">Account</div>
            <div className="flex flex-col gap-1">
              <Link href="/login" className="hover:underline">Login</Link>
              <Link href="/register" className="hover:underline">Register</Link>
              <Link href={gate('/settings')} className="hover:underline">Settings</Link>
            </div>
          </div>
          <div className="text-sm">
            <div className="font-medium mb-1">Resources</div>
            <div className="flex flex-col gap-1">
              <a href="#features" className="hover:underline">Features</a>
              <a href="https://github.com/saud06/german-ai" target="_blank" rel="noreferrer" className="hover:underline">GitHub</a>
              <a href="mailto:saud.mn6@gmail.com" className="hover:underline">Contact</a>
            </div>
          </div>
          </div>
          <div className="mt-5 sm:mt-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-zinc-500">
            <div>© {year} German AI Learner</div>
            <div className="flex items-center gap-3">
              <a className="hover:underline" href="#">Privacy</a>
              <a className="hover:underline" href="#">Terms</a>
            </div>
          </div>
        </div>
      ) : (
        <div className="border-t pt-4 text-xs text-zinc-500 flex items-center justify-between">
          <div>© {year} German AI Learner</div>
          <div className="font-mono">v{APP_VERSION}</div>
        </div>
      )}
    </footer>
  )
}
