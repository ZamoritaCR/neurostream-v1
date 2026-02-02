import { redirect } from 'next/navigation'

// Force dynamic rendering to ensure redirect runs
export const dynamic = 'force-dynamic'

// Redirect root to home - landing page is at www.dopamine.watch
export default function RootPage() {
  redirect('/home')
}
