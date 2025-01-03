import axios from 'axios'
import { emitError } from '@/store/errors'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1',
})

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token')
    if (token) config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (error) => {
    try {
      const msg = error?.response?.data?.detail || error?.message || 'Something went wrong'
      emitError(String(msg))
    } catch {}
    return Promise.reject(error)
  }
)

export default api
