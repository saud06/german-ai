"use client"
import React, { useState } from 'react'
import api from '@/lib/api'
import { useAuth } from '@/store/auth'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getMe } from '@/lib/users'

export default function LoginPage() {
  const { setAuth, setProfile } = useAuth()
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await api.post('/auth/login', { email, password })
      setAuth(res.data.token, res.data.user_id)
      // Immediately fetch profile so navbar/settings have data without reload
      try {
        const me = await getMe()
        setProfile(me.name, me.email)
      } catch {}
      // Redirect to onboarding/welcome - it will handle routing to dashboard if journey exists
      window.location.href = '/onboarding/welcome'
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-[70vh] flex items-center justify-center">
      <div className="w-full max-w-md rounded-xl border bg-white/80 p-6 shadow-sm backdrop-blur dark:bg-zinc-900/70">
        <div className="mb-4 flex items-center gap-2">
          <img src="/logo.svg" alt="Logo" className="h-8 w-8" />
          <h2 className="text-xl font-semibold">Welcome back</h2>
        </div>
        <form className="space-y-3" onSubmit={onSubmit}>
          <input className="input" placeholder="Email" type="email" value={email} onChange={(e)=>setEmail(e.target.value)} required />
          <input className="input" placeholder="Password" type="password" value={password} onChange={(e)=>setPassword(e.target.value)} required />
          {error && <p className="text-red-600 text-sm">{error}</p>}
          <button className="btn w-full" disabled={loading}>{loading ? 'Signing in…' : 'Login'}</button>
        </form>
        <div className="mt-3 rounded-md border bg-amber-50 p-3 text-xs text-amber-800">
          <div className="font-medium">Demo account</div>
          <div>Email: <code>saud@gmail.com</code></div>
          <div>Password: <code>password</code></div>
        </div>
        <p className="mt-4 text-sm text-gray-600 dark:text-zinc-400">
          No account? <Link className="underline" href="/register" scroll={false}>Create one</Link>
        </p>
      </div>
    </main>
  )
}
