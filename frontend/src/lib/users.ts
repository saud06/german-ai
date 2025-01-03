import api from '@/lib/api'

export type Me = { _id: string; name: string; email: string }

export async function getMe() {
  const res = await api.get<Me>('/users/me')
  return res.data
}

export async function updateMe(input: { name: string; email: string }) {
  const res = await api.put<Me>('/users/me', input)
  return res.data
}

export async function changePassword(input: { current_password: string; new_password: string }) {
  const res = await api.put<{ message: string }>('/users/me/password', input)
  return res.data
}
