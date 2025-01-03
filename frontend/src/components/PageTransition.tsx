"use client"
import React, { useEffect, useState } from 'react'
import { usePathname } from 'next/navigation'

export default function PageTransition({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    // trigger fade-in on path change
    setVisible(false)
    const t = requestAnimationFrame(() => setVisible(true))
    return () => cancelAnimationFrame(t)
  }, [pathname])

  return (
    <div className={`transition-opacity duration-300 ease-out ${visible ? 'opacity-100' : 'opacity-0'}`}>
      {children}
    </div>
  )
}
