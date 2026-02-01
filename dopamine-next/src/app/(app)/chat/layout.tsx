import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Chat with Mr.DP | dopamine.watch',
  description: 'Talk to Mr.DP, your personal AI dopamine curator. Get personalized recommendations based on your mood and preferences.',
  openGraph: {
    title: 'Chat with Mr.DP | dopamine.watch',
    description: 'Your AI-powered entertainment companion for ADHD brains.',
  },
}

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}
