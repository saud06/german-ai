"use client"
import React, { useState } from 'react'
import api from '@/lib/api'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function RegisterPage() {
  const router = useRouter()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [ok, setOk] = useState<string | null>(null)

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setOk(null)
    try {
      await api.post('/auth/register', { name, email, password })
      setOk('Registration successful. Please login.')
      setTimeout(()=>{ router.replace('/login', { scroll: false }) }, 500)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-[70vh] flex items-center justify-center">
      <div className="w-full max-w-md rounded-xl border bg-white/80 p-6 shadow-sm backdrop-blur dark:bg-zinc-900/70">
        <div className="mb-4 flex items-center gap-2">
          <img src="/logo.svg" alt="Logo" className="h-8 w-8" />
          <h2 className="text-xl font-semibold">Create account</h2>
        </div>
        <form className="space-y-3" onSubmit={onSubmit}>
          <input className="input" placeholder="Name" value={name} onChange={(e)=>setName(e.target.value)} required />
          <input className="input" placeholder="Email" type="email" value={email} onChange={(e)=>setEmail(e.target.value)} required />
          <input className="input" placeholder="Password" type="password" value={password} onChange={(e)=>setPassword(e.target.value)} required />
          {error && <p className="text-red-600 text-sm">{error}</p>}
          {ok && <p className="text-green-600 text-sm">{ok}</p>}
          <button className="btn w-full" disabled={loading}>{loading ? 'Creating…' : 'Register'}</button>
        </form>
        <p className="mt-4 text-sm text-gray-600 dark:text-zinc-400">Have an account? <Link className="underline" href="/login" scroll={false}>Login</Link></p>
      </div>
    </main>
  )
}
