import { create } from 'zustand'
import api from '@/lib/api'

interface AuthState {
  token: string | null
  userId: string | null
  name: string | null
  email: string | null
  setAuth: (t: string, u: string) => void
  setProfile: (name: string, email: string) => void
  logout: () => void
}

export const useAuth = create<AuthState>((set) => ({
  // Initialize with null on both server and first client render to avoid
  // SSR/CSR markup mismatches. We will hydrate from localStorage after mount
  // via a dedicated client component.
  token: null,
  userId: null,
  name: null,
  email: null,
  setAuth: (t, u) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', t)
      localStorage.setItem('user_id', u)
    }
    set({ token: t, userId: u })
  },
  setProfile: (name, email) => {
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem('user_name', name)
        localStorage.setItem('user_email', email)
      } catch {}
    }
    set({ name, email })
  },
  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token')
      localStorage.removeItem('user_id')
      localStorage.removeItem('user_name')
      localStorage.removeItem('user_email')
    }
    set({ token: null, userId: null, name: null, email: null })
  },
}))
