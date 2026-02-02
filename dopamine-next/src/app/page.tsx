import { redirect } from 'next/navigation'

// Redirect root to home - landing page is at www.dopamine.watch
export default function RootPage() {
  redirect('/home')
}
