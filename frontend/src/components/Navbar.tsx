"use client"
import React, { useEffect, useRef, useState } from 'react'
import { useAuth } from '@/store/auth'
import clsx from 'clsx'
import Link from 'next/link'
import { useRouter, usePathname } from 'next/navigation'
import { APP_VERSION } from '@/lib/appInfo'

// Simple inline SVG icons (no extra deps)
const MoonIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" {...props}><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20.354 15.354A9 9 0 118.646 3.646 7 7 0 0020.354 15.354z"/></svg>
)
const SunIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" {...props}><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 3v2m0 14v2m9-9h-2M5 12H3m15.364 6.364l-1.414-1.414M7.05 7.05L5.636 5.636m12.728 0l-1.414 1.414M7.05 16.95l-1.414 1.414M12 8a4 4 0 100 8 4 4 0 000-8z"/></svg>
)
const LogoutIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" {...props}><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 01-2 2H7a2 2 0 01-2-2V7a2 2 0 012-2h4a2 2 0 012 2v1"/></svg>
)
const LoginIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" {...props}><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16l-4-4m0 0l4-4m-4 4h10m0 4v1a2 2 0 002 2h4a2 2 0 002-2V7a2 2 0 00-2-2h-4a2 2 0 00-2 2v1"/></svg>
)
const MenuIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" {...props}><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
)
const CloseIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" {...props}><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"/></svg>
)

// Extra small colorful icons for menu items
const SettingsIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11.983 6.5a1 1 0 01.934.65l.33.9a1 1 0 00.707.63l.94.24a1 1 0 01.66.56l.02.05a1 1 0 01-.15 1.04l-.62.77a1 1 0 000 1.26l.62.77a1 1 0 01.15 1.04l-.02.05a1 1 0 01-.66.56l-.94.24a1 1 0 00-.707.63l-.33.9a1 1 0 01-.934.65h-.046a1 1 0 01-.934-.65l-.33-.9a1 1 0 00-.707-.63l-.94-.24a1 1 0 01-.66-.56l-.02-.05a1 1 0 01.15-1.04l.62-.77a1 1 0 000-1.26l-.62-.77a1 1 0 01-.15-1.04l.02-.05a1 1 0 01.66-.56l.94-.24a1 1 0 00.707-.63l.33-.9a1 1 0 01.934-.65h.046z"/>
    <circle cx="12" cy="12" r="2.5" strokeWidth="2"/>
  </svg>
)
const InfoIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M12 3a9 9 0 100 18 9 9 0 000-18z"/>
  </svg>
)
const UserPlusIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 7a4 4 0 11-8 0 4 4 0 018 0z"/>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 21v-2a4 4 0 014-4h0m8-7v6m3-3h-6"/>
  </svg>
)

// Nav item icons
const HomeIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l9-7 9 7M5 10v10a1 1 0 001 1h4a1 1 0 001-1v-4h2v4a1 1 0 001 1h4a1 1 0 001-1V10"/>
  </svg>
)
const BookIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 5a2 2 0 012-2h10a2 2 0 012 2v14a1 1 0 01-1.447.894L12 17l-6.553 2.894A1 1 0 014 19V5z"/>
  </svg>
)
const CapIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 14l9-5-9-5-9 5 9 5z"/>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 14l6.16-3.422A12.083 12.083 0 0112 21a12.083 12.083 0 01-6.16-10.422L12 14z"/>
  </svg>
)
const PuzzleIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 14h2a2 2 0 114 0h2a2 2 0 012 2v2a2 2 0 01-2 2h-2v-2a2 2 0 10-4 0v2H8a2 2 0 01-2-2v-2a2 2 0 012-2zM8 10V8a2 2 0 012-2h2V4a2 2 0 112 0v2h2a2 2 0 012 2v2"/>
  </svg>
)
const MicIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 14a3 3 0 003-3V7a3 3 0 10-6 0v4a3 3 0 003 3zm0 0v4m0 0H9m3 0h3M5 11a7 7 0 0014 0"/>
  </svg>
)

export default function Navbar() {
  const { token, userId, name, email, logout } = useAuth()
  const [dark, setDark] = useState(false)
  const [open, setOpen] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)
  const router = useRouter()
  const pathname = usePathname()
  const profileRef = useRef<HTMLDivElement | null>(null)

  useEffect(()=>{
    const saved = localStorage.getItem('theme')
    if (saved === 'dark') {
      setDark(true)
      document.documentElement.classList.add('dark')
    }
  }, [])

  const toggleTheme = () => {
    const next = !dark
    setDark(next)
    document.documentElement.classList.toggle('dark', next)
    localStorage.setItem('theme', next ? 'dark' : 'light')
  }

  const NavLink = ({ href, label, starts }: { href: string; label: React.ReactNode; starts: string }) => {
    let hasAuth = !!token
    try {
      if (!hasAuth && typeof window !== 'undefined') {
        hasAuth = !!localStorage.getItem('token')
      }
    } catch {}
    const dst = hasAuth ? href : '/login'
    return (
      <Link
        href={dst}
        scroll={false}
        onClick={() => setOpen(false)}
        className={clsx(
          'block px-3 py-2 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-800 md:hover:underline md:hover:bg-transparent',
          pathname?.startsWith(starts) && hasAuth && 'text-indigo-600 font-semibold md:underline'
        )}
        aria-current={pathname?.startsWith(starts) && hasAuth ? 'page' : undefined}
      >
        {label}
      </Link>
    )
  }

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setOpen(false)
      setProfileOpen(false)
    }
  }

  // Close profile menu on outside click
  useEffect(() => {
    const onDocClick = (e: MouseEvent) => {
      if (!profileRef.current) return
      if (!profileRef.current.contains(e.target as Node)) {
        setProfileOpen(false)
      }
    }
    document.addEventListener('mousedown', onDocClick)
    return () => document.removeEventListener('mousedown', onDocClick)
  }, [])

  return (
    <header className="sticky top-0 z-40 mb-6 border-b bg-white/70 dark:bg-zinc-900/70 backdrop-blur supports-[backdrop-filter]:bg-white/60 header-gradient">
      <div className="flex h-12 items-center justify-between" onKeyDown={onKeyDown}>
        <Link href="/" className="flex items-center gap-2">
          <img src="/logo.svg" alt="Logo" className="h-9 w-9 md:h-10 md:w-10" />
          <span className="hidden sm:inline text-lg md:text-2xl font-semibold leading-none">German AI Learner</span>
        </Link>
        {/* Right controls */}
        <div className="flex items-center gap-2 md:gap-3">
          {/* Theme toggle: icon-only on small screens, with text on md+ via tooltip/title */}
          <button
            aria-label="Toggle theme"
            title={dark ? 'Light mode' : 'Dark mode'}
            className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-indigo-300 hover:bg-indigo-50 dark:hover:bg-zinc-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
            onClick={toggleTheme}
          >
            {dark ? <SunIcon className="h-5 w-5"/> : <MoonIcon className="h-5 w-5"/>}
          </button>
          <div className="relative" ref={profileRef}>
            <button
              aria-haspopup="menu"
              aria-expanded={profileOpen}
              aria-label={token ? 'User menu' : 'Guest menu'}
              title={token ? 'Account' : 'Sign in'}
              className={clsx(
                'inline-flex h-10 w-10 items-center justify-center rounded-full border border-indigo-300 focus:outline-none focus-visible:ring-2',
                token ? 'bg-indigo-50 dark:bg-zinc-800 focus-visible:ring-indigo-500' : 'hover:bg-indigo-50 dark:hover:bg-zinc-800 focus-visible:ring-indigo-500'
              )}
              onClick={() => setProfileOpen(v => !v)}
            >
              {/* Simple avatar circle with initials or icon */}
              {token ? (
                <span className="select-none font-semibold text-indigo-700 dark:text-indigo-200">
                  {(name || email || userId || 'U').slice(0, 2).toUpperCase()}
                </span>
              ) : (
                <LoginIcon className="h-5 w-5" />
              )}
            </button>

            {/* Dropdown Menu */}
            {profileOpen && (
              <div
                role="menu"
                className="absolute right-0 mt-2 w-56 origin-top-right rounded-md border bg-white/95 dark:bg-zinc-900/95 shadow-lg backdrop-blur p-1 z-50"
              >
                {token ? (
                  <>
                    <div className="px-3 py-2 text-xs text-zinc-500">Signed in</div>
                    <div className="px-3 pb-2">
                      <div className="text-sm font-medium truncate" title={name || ''}>{name || 'User'}</div>
                      <div className="text-xs text-zinc-600 dark:text-zinc-400 truncate" title={email || ''}>{email || ''}</div>
                    </div>
                    <div className="my-1 h-px bg-zinc-200 dark:bg-zinc-800" />
                    <Link
                      href="/settings"
                      className="flex items-center gap-2 px-3 py-2 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-800 text-sm"
                      onClick={() => setProfileOpen(false)}
                    >
                      <span aria-hidden className="h-2.5 w-2.5 rounded-full bg-indigo-500"></span>
                      <span>Settings</span>
                    </Link>
                    <div className="flex items-center justify-between px-3 py-2 text-xs text-zinc-600 dark:text-zinc-400">
                      <span className="inline-flex items-center gap-2">
                        <span aria-hidden className="h-2.5 w-2.5 rounded-full bg-teal-500"></span>
                        Version
                      </span>
                      <span className="font-mono">{APP_VERSION}</span>
                    </div>
                    <button
                      className="mt-1 flex w-full items-center gap-2 px-3 py-2 rounded-md text-left text-red-600 hover:bg-red-50 dark:hover:bg-zinc-800 text-sm"
                      onClick={() => { setProfileOpen(false); logout(); router.push('/') }}
                    >
                      <LogoutIcon className="h-4 w-4" /> Logout
                    </button>
                  </>
                ) : (
                  <>
                    <div className="px-3 py-2 text-xs text-zinc-500">You are not signed in</div>
                    <Link
                      href="/login"
                      className="flex items-center gap-2 px-3 py-2 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-800 text-sm"
                      onClick={() => setProfileOpen(false)}
                    >
                      <span aria-hidden className="h-2.5 w-2.5 rounded-full bg-green-500"></span>
                      <span>Login</span>
                    </Link>
                    <Link
                      href="/register"
                      className="flex items-center gap-2 px-3 py-2 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-800 text-sm"
                      onClick={() => setProfileOpen(false)}
                    >
                      <span aria-hidden className="h-2.5 w-2.5 rounded-full bg-blue-500"></span>
                      <span>Register</span>
                    </Link>
                    <div className="my-1 h-px bg-zinc-200 dark:bg-zinc-800" />
                    <div className="flex items-center justify-between px-3 py-2 text-xs text-zinc-600 dark:text-zinc-400">
                      <span className="inline-flex items-center gap-2">
                        <InfoIcon className="h-3.5 w-3.5 text-teal-600" />
                        Version
                      </span>
                      <span className="font-mono">{APP_VERSION}</span>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
          {/* Hamburger for mobile */}
          <button
            aria-label={open ? 'Close menu' : 'Open menu'}
            className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-indigo-300 md:hidden hover:bg-indigo-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
            onClick={()=> setOpen(o=>!o)}
          >
            {open ? <CloseIcon className="h-5 w-5"/> : <MenuIcon className="h-5 w-5"/>}
          </button>
        </div>
      </div>

      {/* Desktop nav */}
      <nav className="mt-3 hidden md:flex items-center gap-2 text-sm">
        <NavLink
          href="/dashboard"
          starts="/dashboard"
          label={<span className="inline-flex items-center gap-1.5"><HomeIcon className="h-4 w-4 text-rose-500"/>Dashboard</span>}
        />
        <NavLink
          href="/vocab"
          starts="/vocab"
          label={<span className="inline-flex items-center gap-1.5"><BookIcon className="h-4 w-4 text-emerald-500"/>Vocab</span>}
        />
        <NavLink
          href="/grammar"
          starts="/grammar"
          label={<span className="inline-flex items-center gap-1.5"><CapIcon className="h-4 w-4 text-indigo-500"/>Grammar</span>}
        />
        <NavLink
          href="/quiz"
          starts="/quiz"
          label={<span className="inline-flex items-center gap-1.5"><PuzzleIcon className="h-4 w-4 text-amber-500"/>Quiz</span>}
        />
        <NavLink
          href="/speech"
          starts="/speech"
          label={<span className="inline-flex items-center gap-1.5"><MicIcon className="h-4 w-4 text-fuchsia-500"/>Pronunciation</span>}
        />
      </nav>

      {/* Mobile collapse */}
      <div className={clsx(
        'md:hidden transition-[max-height] duration-300 overflow-hidden',
        open ? 'max-h-96 mt-2' : 'max-h-0'
      )}>
        <nav className="flex flex-col rounded-md border p-2 text-sm bg-white/95 dark:bg-zinc-900/95 shadow-sm">
          <NavLink href="/dashboard" starts="/dashboard" label={<span className="inline-flex items-center gap-1.5"><HomeIcon className="h-4 w-4 text-rose-500"/>Dashboard</span>} />
          <NavLink href="/vocab" starts="/vocab" label={<span className="inline-flex items-center gap-1.5"><BookIcon className="h-4 w-4 text-emerald-500"/>Vocab</span>} />
          <NavLink href="/grammar" starts="/grammar" label={<span className="inline-flex items-center gap-1.5"><CapIcon className="h-4 w-4 text-indigo-500"/>Grammar</span>} />
          <NavLink href="/quiz" starts="/quiz" label={<span className="inline-flex items-center gap-1.5"><PuzzleIcon className="h-4 w-4 text-amber-500"/>Quiz</span>} />
          <NavLink href="/speech" starts="/speech" label={<span className="inline-flex items-center gap-1.5"><MicIcon className="h-4 w-4 text-fuchsia-500"/>Pronunciation</span>} />
        </nav>
      </div>
    </header>
  )
}
