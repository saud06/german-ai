export default function LoadingVocab() {
  return (
    <main className="space-y-4 animate-pulse">
      <div className="h-8 w-1/2 rounded-md bg-gray-200 dark:bg-zinc-800" />
      <div className="rounded-md border p-4 space-y-2 bg-white dark:bg-zinc-900">
        <div className="h-6 w-1/3 rounded bg-gray-200 dark:bg-zinc-800" />
        <div className="h-4 w-1/2 rounded bg-gray-200 dark:bg-zinc-800" />
        <div className="h-4 w-5/6 rounded bg-gray-200 dark:bg-zinc-800" />
      </div>
    </main>
  )
}
