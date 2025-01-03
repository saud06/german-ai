export default function Loading() {
  return (
    <>
      {/* Top progress bar */}
      <div className="fixed left-0 top-0 z-50 h-1 w-full bg-gradient-to-r from-indigo-500 via-pink-500 to-indigo-500">
        <div className="h-full w-1/3 bg-white/70 progress-anim" />
      </div>
      <main className="space-y-6 animate-pulse">
      <div className="h-10 w-2/3 rounded-md bg-gray-200 dark:bg-zinc-800" />
      <div className="h-5 w-full rounded-md bg-gray-200 dark:bg-zinc-800" />
      <div className="h-5 w-5/6 rounded-md bg-gray-200 dark:bg-zinc-800" />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mt-6">
        <div className="h-32 rounded-lg border bg-gray-100 dark:bg-zinc-900" />
        <div className="h-32 rounded-lg border bg-gray-100 dark:bg-zinc-900" />
        <div className="h-32 rounded-lg border bg-gray-100 dark:bg-zinc-900" />
        <div className="h-32 rounded-lg border bg-gray-100 dark:bg-zinc-900" />
      </div>
      </main>
    </>
  )
}
