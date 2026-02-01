import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Discover | dopamine.watch',
  description: 'Tell us how you feel and how you want to feel. Our AI finds the perfect movie, show, or music to bridge your emotional journey.',
  openGraph: {
    title: 'Discover | dopamine.watch',
    description: 'Mood-based content discovery for neurodivergent minds. Find entertainment that matches your emotional state.',
  },
}

export default function DiscoverLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}
