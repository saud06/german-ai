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

export const useAuth = create<AuthState>((set) => {
  // Hydrate from localStorage on initialization (client-side only)
  const initialState = typeof window !== 'undefined' ? {
    token: localStorage.getItem('token'),
    userId: localStorage.getItem('user_id'),
    name: localStorage.getItem('user_name'),
    email: localStorage.getItem('user_email'),
  } : {
    token: null,
    userId: null,
    name: null,
    email: null,
  }

  return {
    ...initialState,
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
  }
})
