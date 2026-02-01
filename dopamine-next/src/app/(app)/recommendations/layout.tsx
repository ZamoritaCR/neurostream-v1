import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Recommendations | dopamine.watch',
  description: 'Personalized movie, TV, and music recommendations based on your emotional journey. From stressed to relaxed, anxious to calm.',
  openGraph: {
    title: 'Recommendations | dopamine.watch',
    description: 'AI-curated entertainment for your exact mood. Movies, shows, and music tailored to how you feel.',
  },
}

export default function RecommendationsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}
