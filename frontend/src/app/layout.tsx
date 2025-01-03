import './globals.css'
import React from 'react'
import Script from 'next/script'
import ClientLayoutShell from '@/components/ClientLayoutShell'

export const metadata = {
  title: 'German AI Learner',
  description: 'Mini Duolingo-like German app with AI and smart UX',
  icons: [
    { rel: 'icon', url: '/logo.svg', type: 'image/svg+xml' },
    { rel: 'icon', url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
    { rel: 'icon', url: '/favicon.ico' },
    { rel: 'apple-touch-icon', url: '/apple-touch-icon.png', sizes: '180x180' },
  ],
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* Ensure theme class is set before hydration to avoid mismatches */}
        {/* Inline a tiny script to avoid any external loading/encoding hiccups */}
        <Script id="theme-init" strategy="beforeInteractive">
          {`try{var t=localStorage.getItem('theme');if(t==='dark'){document.documentElement.classList.add('dark')}}catch(e){}`}
        </Script>
        
      </head>
      <body suppressHydrationWarning>
        <ClientLayoutShell>
          {children}
        </ClientLayoutShell>
      </body>
    </html>
  )
}
