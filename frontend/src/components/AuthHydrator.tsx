"use client"
import { useEffect } from 'react'
import { useAuth } from '@/store/auth'
import { getMe } from '@/lib/users'

export default function AuthHydrator() {
  const { setAuth, setProfile, logout } = useAuth()

  useEffect(() => {
    try {
      const t = localStorage.getItem('token')
      const u = localStorage.getItem('user_id')
      const n = localStorage.getItem('user_name')
      const e = localStorage.getItem('user_email')
      if (t && u) {
        setAuth(t, u)
        if (n && e) {
          // Optimistically set cached profile for immediate UI
          setProfile(n, e)
        }
        // Fetch profile details
        getMe().then((me) => {
          setProfile(me.name, me.email)
        }).catch(() => {/* handled by interceptor */})
      } else {
        // Ensure store reflects logged-out state if nothing is persisted
        logout()
      }
    } catch {
      // ignore
    }
  }, [setAuth, setProfile, logout])

  return null
}
