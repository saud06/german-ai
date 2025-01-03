"use client"
import { useEffect } from 'react'
import { useAuth } from '@/store/auth'
import { useRouter } from 'next/navigation'

export default function RequireAuth() {
  const { token } = useAuth()
  const router = useRouter()

  useEffect(() => {
    // Avoid redirect flash on initial page load before auth hydration.
    // If a token exists in localStorage or in the store, consider user authenticated.
    try {
      const persisted = typeof window !== 'undefined' ? localStorage.getItem('token') : null
      const hasAuth = !!token || !!persisted
      if (!hasAuth) router.replace('/login')
    } catch {
      if (!token) router.replace('/login')
    }
  }, [token, router])

  return null
}
