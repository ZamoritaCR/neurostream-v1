import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Home | dopamine.watch',
  description: 'Your personalized streaming dashboard. Get mood-based recommendations, quick picks, and AI-powered suggestions for ADHD-friendly entertainment.',
  openGraph: {
    title: 'Home | dopamine.watch',
    description: 'Your personalized streaming dashboard. Get mood-based recommendations and AI-powered suggestions.',
  },
}

export default function HomeLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}
