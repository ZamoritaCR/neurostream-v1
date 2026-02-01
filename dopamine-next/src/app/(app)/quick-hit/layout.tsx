import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Quick Hit | dopamine.watch',
  description: 'Decision fatigue? Let our AI pick something perfect for you in one tap. Zero scrolling, instant dopamine.',
  openGraph: {
    title: 'Quick Hit | dopamine.watch',
    description: 'One-tap entertainment recommendations. Perfect for ADHD decision fatigue.',
  },
}

export default function QuickHitLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}
