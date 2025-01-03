export default function LoadingQuiz() {
  return (
    <main className="space-y-4 animate-pulse">
      <div className="h-8 w-1/3 rounded-md bg-gray-200 dark:bg-zinc-800" />
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="h-24 rounded-md border bg-gray-100 dark:bg-zinc-900" />
        <div className="h-24 rounded-md border bg-gray-100 dark:bg-zinc-900" />
      </div>
    </main>
  )
}
