"use client"
import React, { useEffect, useState } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import dynamic from 'next/dynamic'
import PageTransition from '@/components/PageTransition'
import AuthHydrator from '@/components/AuthHydrator'
import Footer from '@/components/Footer'
import { onError } from '@/store/errors'
import { JourneyProvider, useJourney } from '@/contexts/JourneyContext'

// Render Navbar only on the client to avoid SSR/client markup mismatch
// because it depends on localStorage-based auth/theme state.
const Navbar = dynamic(() => import('@/components/Navbar'), { ssr: false })

function LayoutContent({ children }: { children: React.ReactNode }) {
  const [err, setErr] = useState<string | null>(null)
  const pathname = usePathname()
  const router = useRouter()
  const { activeJourney, loading } = useJourney()
  
  // Check if we're in onboarding flow or settings
  const isOnboarding = pathname?.startsWith('/onboarding')
  const isSettings = pathname?.startsWith('/settings')
  const isAuth = pathname?.startsWith('/login') || pathname?.startsWith('/register') || pathname === '/'
  
  useEffect(() => {
    return onError((m) => { setErr(m); setTimeout(() => setErr(null), 4000) })
  }, [])

  // Persist lastPath for Resume button on the dashboard
  useEffect(() => {
    if (typeof window === 'undefined') return
    try {
      if (pathname && pathname.startsWith('/')) {
        localStorage.setItem('lastPath', pathname)
      }
    } catch {}
  }, [pathname])

  // Route protection: Block access to all routes except onboarding, settings, and auth if no active journey
  useEffect(() => {
    if (loading) return
    
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
    if (!token) return // Not logged in, let auth routes handle it
    
    if (!activeJourney && !isOnboarding && !isSettings && !isAuth) {
      window.location.href = '/onboarding/welcome'
    }
  }, [activeJourney, loading, isOnboarding, isSettings, isAuth, pathname])

  return (
    <div className="container py-6">
      <AuthHydrator />
      {!isOnboarding && <Navbar />}
      {err && (
        <div className="mb-3 rounded-md border border-red-300 bg-red-50 p-2 text-sm text-red-700">{err}</div>
      )}
      <PageTransition>
        {children}
      </PageTransition>
      {!isOnboarding && <Footer />}
    </div>
  )
}

export default function ClientLayoutShell({ children }: { children: React.ReactNode }) {
  return (
    <JourneyProvider>
      <LayoutContent>{children}</LayoutContent>
    </JourneyProvider>
  )
}
