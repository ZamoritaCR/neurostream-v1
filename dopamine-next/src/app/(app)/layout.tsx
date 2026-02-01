'use client'

import { Navigation, PageWrapper } from '@/components/layout/Navigation'
import { ToastProvider } from '@/components/ui'
import { MrDpFloating, MovieDetailsModal } from '@/components/features'
import { RecommendationsProvider, useRecommendations } from '@/lib/recommendations-context'

function AppContent({ children }: { children: React.ReactNode }) {
  const { selectedMovie, showMovieModal, setShowMovieModal } = useRecommendations()

  return (
    <div className="min-h-screen bg-white dark:bg-dark-bg">
      <Navigation />
      <PageWrapper>
        {children}
      </PageWrapper>
      {/* Omnipresent Mr.DP floating assistant */}
      <MrDpFloating />
      {/* Movie details modal */}
      <MovieDetailsModal
        movie={selectedMovie}
        isOpen={showMovieModal}
        onClose={() => setShowMovieModal(false)}
      />
    </div>
  )
}

export default function AppLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <RecommendationsProvider>
      <ToastProvider>
        <AppContent>{children}</AppContent>
      </ToastProvider>
    </RecommendationsProvider>
  )
}
