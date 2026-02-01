import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Sign In | dopamine.watch',
  description: 'Sign in to dopamine.watch to save your preferences, track achievements, and get personalized recommendations.',
  openGraph: {
    title: 'Sign In | dopamine.watch',
    description: 'Join dopamine.watch for personalized ADHD-friendly entertainment.',
  },
}

export default function LoginLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}
