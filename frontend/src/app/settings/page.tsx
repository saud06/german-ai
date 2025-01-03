"use client"
import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import RequireAuth from '@/components/RequireAuth'
import { useAuth } from '@/store/auth'
import { APP_VERSION } from '@/lib/appInfo'
import { getMe, updateMe, changePassword } from '@/lib/users'

export default function SettingsPage() {
  const { userId, token, name, email, setProfile } = useAuth()
  const [pName, setPName] = useState(name || '')
  const [pEmail, setPEmail] = useState(email || '')
  const [saving, setSaving] = useState(false)
  const [saveMsg, setSaveMsg] = useState<string | null>(null)

  const [curPwd, setCurPwd] = useState('')
  const [newPwd, setNewPwd] = useState('')
  const [confirmPwd, setConfirmPwd] = useState('')
  const [pwdSaving, setPwdSaving] = useState(false)
  const [pwdMsg, setPwdMsg] = useState<string | null>(null)

  useEffect(() => {
    setPName(name || '')
    setPEmail(email || '')
  }, [name, email])

  // If profile is not yet in store, fetch it so fields populate without a full reload
  useEffect(() => {
    if (!token) return
    if (!name || !email) {
      getMe().then((me) => setProfile(me.name, me.email)).catch(() => {})
    }
  }, [token, name, email, setProfile])

  // Inline validation helpers
  const nameError = pName.trim().length < 2 ? 'Name must be at least 2 characters' : null
  const emailError = (() => {
    if (!pEmail.trim()) return 'Email is required'
    const re = /[^@\s]+@[^@\s]+\.[^@\s]+/
    return re.test(pEmail.trim()) ? null : 'Enter a valid email address'
  })()

  function pwdStrength(p: string) {
    let score = 0
    if (p.length >= 6) score++
    if (p.length >= 10) score++
    if (/[A-Z]/.test(p)) score++
    if (/[0-9]/.test(p)) score++
    if (/[^A-Za-z0-9]/.test(p)) score++
    const clamp = Math.min(score, 4)
    const labels = ['Very weak', 'Weak', 'Okay', 'Good', 'Strong']
    const colors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-lime-600', 'bg-green-600']
    return { score: clamp, label: labels[clamp], color: colors[clamp] }
  }
  const strength = pwdStrength(newPwd)
  const pwdMatchError = newPwd && confirmPwd && newPwd !== confirmPwd ? 'Passwords do not match' : null

  // Redirect unauthenticated users quickly
  if (!token) return (<><RequireAuth /></>)

  async function onSaveProfile(e: React.FormEvent) {
    e.preventDefault()
    if (nameError || emailError) return
    try {
      setSaving(true)
      const res = await updateMe({ name: pName.trim(), email: pEmail.trim() })
      setProfile(res.name, res.email)
      setSaveMsg('Profile updated successfully')
      setTimeout(() => setSaveMsg(null), 3000)
    } catch (e: any) {
      setSaveMsg(e?.response?.data?.detail || 'Failed to update profile')
      setTimeout(() => setSaveMsg(null), 4000)
    } finally {
      setSaving(false)
    }
  }

  async function onChangePassword(e: React.FormEvent) {
    e.preventDefault()
    if (newPwd !== confirmPwd) {
      setPwdMsg('New password and confirmation do not match')
      setTimeout(() => setPwdMsg(null), 3000)
      return
    }
    try {
      setPwdSaving(true)
      await changePassword({ current_password: curPwd, new_password: newPwd })
      setPwdMsg('Password updated successfully')
      setCurPwd('')
      setNewPwd('')
      setConfirmPwd('')
      setTimeout(() => setPwdMsg(null), 3000)
    } catch (e: any) {
      setPwdMsg(e?.response?.data?.detail || 'Failed to update password')
      setTimeout(() => setPwdMsg(null), 4000)
    } finally {
      setPwdSaving(false)
    }
  }

  return (
    <div className="max-w-2xl space-y-6">
      <RequireAuth />
      <div>
        <h1 className="text-2xl font-semibold mb-1">Settings</h1>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">Manage your account and app preferences.</p>
      </div>

      <section className="rounded-md border p-4">
        <h2 className="font-medium mb-3">Account</h2>
        <form onSubmit={onSaveProfile} className="space-y-3">
          <div>
            <label className="block text-sm text-zinc-600 dark:text-zinc-400 mb-1">Name</label>
            <input
              type="text"
              value={pName}
              onChange={(e) => setPName(e.target.value)}
              className={
                `w-full rounded-md border px-3 py-2 bg-white dark:bg-zinc-900 ` +
                (nameError ? 'border-red-400 focus-visible:ring-red-500' : '')
              }
              required
            />
            {nameError && <div className="mt-1 text-xs text-red-600">{nameError}</div>}
          </div>
          <div>
            <label className="block text-sm text-zinc-600 dark:text-zinc-400 mb-1">Email</label>
            <input
              type="email"
              value={pEmail}
              onChange={(e) => setPEmail(e.target.value)}
              className={
                `w-full rounded-md border px-3 py-2 bg-white dark:bg-zinc-900 ` +
                (emailError ? 'border-red-400 focus-visible:ring-red-500' : '')
              }
              required
            />
            {emailError && <div className="mt-1 text-xs text-red-600">{emailError}</div>}
          </div>
          <div className="flex items-center gap-2">
            <button
              type="submit"
              disabled={!!nameError || !!emailError || saving}
              className="inline-flex items-center justify-center rounded-md border px-3 py-2 text-sm font-medium hover:bg-zinc-100 dark:hover:bg-zinc-800 disabled:opacity-60"
            >
              {saving ? 'Saving…' : 'Save changes'}
            </button>
            {saveMsg && <div className="text-sm text-zinc-600 dark:text-zinc-400">{saveMsg}</div>}
          </div>
          <div className="text-xs text-zinc-500">User ID: <span className="font-mono">{userId}</span></div>
        </form>
      </section>

      <section className="rounded-md border p-4">
        <h2 className="font-medium mb-2">Appearance</h2>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">Use the theme toggle in the top navigation to switch between light and dark mode.</p>
      </section>

      <section className="rounded-md border p-4">
        <h2 className="font-medium mb-3">Change password</h2>
        <form onSubmit={onChangePassword} className="space-y-3 max-w-md">
          <div>
            <label className="block text-sm text-zinc-600 dark:text-zinc-400 mb-1">Current password</label>
            <input
              type="password"
              value={curPwd}
              onChange={(e) => setCurPwd(e.target.value)}
              className="w-full rounded-md border px-3 py-2 bg-white dark:bg-zinc-900"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-zinc-600 dark:text-zinc-400 mb-1">New password</label>
            <input
              type="password"
              value={newPwd}
              onChange={(e) => setNewPwd(e.target.value)}
              className={
                `w-full rounded-md border px-3 py-2 bg-white dark:bg-zinc-900 ` +
                (newPwd && newPwd.length < 6 ? 'border-red-400 focus-visible:ring-red-500' : '')
              }
              required
              minLength={6}
            />
            {newPwd && (
              <div className="mt-1 flex items-center gap-2">
                <div className="h-1.5 w-24 rounded bg-zinc-200 overflow-hidden">
                  <div className={`h-full ${strength.color}`} style={{ width: `${(strength.score + 1) * 20}%` }} />
                </div>
                <div className="text-xs text-zinc-600 dark:text-zinc-400">{strength.label}</div>
              </div>
            )}
          </div>
          <div>
            <label className="block text-sm text-zinc-600 dark:text-zinc-400 mb-1">Confirm new password</label>
            <input
              type="password"
              value={confirmPwd}
              onChange={(e) => setConfirmPwd(e.target.value)}
              className={
                `w-full rounded-md border px-3 py-2 bg-white dark:bg-zinc-900 ` +
                (pwdMatchError ? 'border-red-400 focus-visible:ring-red-500' : '')
              }
              required
              minLength={6}
            />
            {pwdMatchError && <div className="mt-1 text-xs text-red-600">{pwdMatchError}</div>}
          </div>
          <div className="flex items-center gap-2">
            <button
              type="submit"
              disabled={
                pwdSaving || !curPwd || !newPwd || newPwd.length < 6 || !!pwdMatchError
              }
              className="inline-flex items-center justify-center rounded-md border px-3 py-2 text-sm font-medium hover:bg-zinc-100 dark:hover:bg-zinc-800 disabled:opacity-60"
            >
              {pwdSaving ? 'Updating…' : 'Update password'}
            </button>
            {pwdMsg && <div className="text-sm text-zinc-600 dark:text-zinc-400">{pwdMsg}</div>}
          </div>
        </form>
      </section>

      <section className="rounded-md border p-4">
        <h2 className="font-medium mb-2">About this app</h2>
        <div className="text-sm text-zinc-700 dark:text-zinc-300">
          <div><span className="text-zinc-500">App:</span> German AI Learner</div>
          <div><span className="text-zinc-500">Version:</span> {APP_VERSION}</div>
        </div>
      </section>
    </div>
  )
}
