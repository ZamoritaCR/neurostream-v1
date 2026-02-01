'use client'

import { Navigation, PageWrapper } from '@/components/layout/Navigation'
import { ToastProvider } from '@/components/ui'
import { MrDpFloating } from '@/components/features'

export default function AppLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ToastProvider>
      <div className="min-h-screen bg-white dark:bg-dark-bg">
        <Navigation />
        <PageWrapper>
          {children}
        </PageWrapper>
        {/* Omnipresent Mr.DP floating assistant */}
        <MrDpFloating />
      </div>
    </ToastProvider>
  )
}
