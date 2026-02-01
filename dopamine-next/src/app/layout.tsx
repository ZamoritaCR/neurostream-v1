import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

export const metadata: Metadata = {
  title: 'dopamine.watch | Stop Scrolling. Start Watching.',
  description: 'AI-powered streaming recommendations for ADHD brains. Find the perfect movie, show, or music based on your mood in seconds.',
  keywords: ['ADHD', 'streaming', 'movie recommendations', 'neurodivergent', 'mood-based', 'Netflix', 'entertainment'],
  authors: [{ name: 'dopamine.watch' }],
  creator: 'dopamine.watch',
  metadataBase: new URL('https://app.dopamine.watch'),
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://app.dopamine.watch',
    siteName: 'dopamine.watch',
    title: 'dopamine.watch | Stop Scrolling. Start Watching.',
    description: 'AI-powered streaming recommendations for ADHD brains.',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'dopamine.watch - AI-powered streaming for ADHD brains',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'dopamine.watch | Stop Scrolling. Start Watching.',
    description: 'AI-powered streaming recommendations for ADHD brains.',
    images: ['/og-image.png'],
  },
  manifest: '/manifest.json',
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
}

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#FFFFFF' },
    { media: '(prefers-color-scheme: dark)', color: '#0A0A0F' },
  ],
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  userScalable: true,
  viewportFit: 'cover',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <head>
        {/* Prevent iOS zoom on input focus */}
        <meta name="format-detection" content="telephone=no" />
        {/* PWA */}
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="apple-mobile-web-app-title" content="dopamine.watch" />
        {/* Google Analytics */}
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-34Q0KMXDQF"></script>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', 'G-34Q0KMXDQF');
            `,
          }}
        />
      </head>
      <body className="font-sans bg-white dark:bg-dark-bg text-surface-900 dark:text-white min-h-screen-safe">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
