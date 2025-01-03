import type { NextRequest } from 'next/server'
import { NextResponse } from 'next/server'

// No-op middleware; disabled per request to keep only Navbar client-side guards
export function middleware(_req: NextRequest) {
  return NextResponse.next()
}

// Disable matching so middleware does not run
export const config = {
  matcher: [],
}
