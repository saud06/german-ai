type Handler = (msg: string) => void

const listeners = new Set<Handler>()

export function emitError(msg: string) {
  if (!msg) return
  for (const fn of listeners) {
    try { fn(msg) } catch {}
  }
}

export function onError(handler: Handler) {
  listeners.add(handler)
  return () => { listeners.delete(handler) }
}
