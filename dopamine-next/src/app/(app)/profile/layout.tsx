import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Profile | dopamine.watch',
  description: 'Manage your dopamine.watch profile, view achievements, track your streak, and customize your experience.',
  openGraph: {
    title: 'Profile | dopamine.watch',
    description: 'Your dopamine.watch profile and achievements.',
  },
}

export default function ProfileLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}
