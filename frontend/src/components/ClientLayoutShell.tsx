"use client"
import React, { useEffect, useState } from 'react'
import { usePathname } from 'next/navigation'
import dynamic from 'next/dynamic'
import PageTransition from '@/components/PageTransition'
import AuthHydrator from '@/components/AuthHydrator'
import Footer from '@/components/Footer'
import { onError } from '@/store/errors'
import { JourneyProvider } from '@/contexts/JourneyContext'

// Render Navbar only on the client to avoid SSR/client markup mismatch
// because it depends on localStorage-based auth/theme state.
const Navbar = dynamic(() => import('@/components/Navbar'), { ssr: false })

export default function ClientLayoutShell({ children }: { children: React.ReactNode }) {
  const [err, setErr] = useState<string | null>(null)
  const pathname = usePathname()
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

  return (
    <JourneyProvider>
      <div className="container py-6">
        <AuthHydrator />
        <Navbar />
        {err && (
          <div className="mb-3 rounded-md border border-red-300 bg-red-50 p-2 text-sm text-red-700">{err}</div>
        )}
        <PageTransition>
          {children}
        </PageTransition>
        <Footer />
      </div>
    </JourneyProvider>
  )
}
