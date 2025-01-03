import dynamic from 'next/dynamic'
import RequireAuth from '@/components/RequireAuth'

const ClientDashboard = dynamic(() => import('./ClientDashboard'), {
  ssr: false,
  loading: () => (
    <div className="space-y-4 animate-pulse">
      <div className="h-8 w-1/2 rounded-md bg-gray-200 dark:bg-zinc-800" />
      <div className="h-32 rounded-md border bg-gray-100 dark:bg-zinc-900" />
      <div className="h-32 rounded-md border bg-gray-100 dark:bg-zinc-900" />
    </div>
  ),
})

export default function Page() {
  return (
    <>
      <RequireAuth />
      <ClientDashboard />
    </>
  )
}
