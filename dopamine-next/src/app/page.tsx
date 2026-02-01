'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Sparkle,
  Lightning,
  Brain,
  ArrowRight,
  Play,
  Star,
  Users,
  Devices,
  CheckCircle,
} from '@phosphor-icons/react'
import Link from 'next/link'
import { Button } from '@/components/ui'
import { cn } from '@/lib/utils'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-dark-bg overflow-hidden">
      {/* Gradient mesh background */}
      <div className="fixed inset-0 bg-gradient-mesh opacity-50 pointer-events-none" />

      {/* Floating orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute w-96 h-96 rounded-full bg-primary-500/20 blur-3xl"
          animate={{
            x: [0, 50, 0],
            y: [0, 30, 0],
          }}
          transition={{ duration: 15, repeat: Infinity, ease: 'easeInOut' }}
          style={{ top: '10%', left: '10%' }}
        />
        <motion.div
          className="absolute w-80 h-80 rounded-full bg-secondary-400/20 blur-3xl"
          animate={{
            x: [0, -30, 0],
            y: [0, 50, 0],
          }}
          transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut' }}
          style={{ top: '50%', right: '10%' }}
        />
        <motion.div
          className="absolute w-64 h-64 rounded-full bg-accent-400/20 blur-3xl"
          animate={{
            x: [0, 40, 0],
            y: [0, -30, 0],
          }}
          transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
          style={{ bottom: '20%', left: '30%' }}
        />
      </div>

      {/* Header */}
      <header className="relative z-10">
        <div className="max-w-7xl mx-auto px-4 md:px-8 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-secondary-400 flex items-center justify-center shadow-glow-sm">
              <Sparkle size={24} weight="fill" className="text-white" />
            </div>
            <span className="text-xl font-bold text-surface-900 dark:text-white">
              dopamine<span className="gradient-text">.watch</span>
            </span>
          </Link>

          <div className="flex items-center gap-4">
            <Link
              href="/login"
              className="hidden md:block text-surface-600 dark:text-surface-300 font-medium hover:text-primary-500 transition-colors"
            >
              Log in
            </Link>
            <Link href="/app">
              <Button size="md">
                Get Started Free
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 pt-12 md:pt-20 pb-16 md:pb-24 px-4">
        <div className="max-w-4xl mx-auto text-center">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-50 dark:bg-primary-500/10 text-primary-600 dark:text-primary-400 text-sm font-medium mb-6"
          >
            <Brain size={16} weight="fill" />
            <span>Built for ADHD brains</span>
          </motion.div>

          {/* Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-4xl md:text-6xl lg:text-7xl font-bold text-surface-900 dark:text-white leading-tight mb-6"
          >
            Stop scrolling.
            <br />
            <span className="gradient-text">Start watching.</span>
          </motion.h1>

          {/* Subheadline */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-lg md:text-xl text-surface-600 dark:text-surface-300 max-w-2xl mx-auto mb-8 text-balance"
          >
            AI-powered streaming recommendations based on your mood.
            Find the perfect movie, show, or music in seconds — not hours.
          </motion.p>

          {/* CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12"
          >
            <Link href="/app">
              <Button
                size="lg"
                icon={<Lightning size={20} weight="fill" />}
                className="px-8"
              >
                Find My Show Now
              </Button>
            </Link>
            <Button
              size="lg"
              variant="secondary"
              icon={<Play size={20} weight="fill" />}
            >
              Watch Demo
            </Button>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="flex flex-wrap items-center justify-center gap-8 md:gap-12"
          >
            <Stat value="500+" label="Happy users" />
            <Stat value="< 30s" label="Average pick time" />
            <Stat value="4.9" label="User rating" icon={<Star size={16} weight="fill" className="text-amber-400" />} />
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 py-16 md:py-24 px-4">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-surface-900 dark:text-white mb-4">
              Why ADHD brains love us
            </h2>
            <p className="text-surface-600 dark:text-surface-400 max-w-xl mx-auto">
              We understand decision fatigue. That's why we built something different.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-6">
            <FeatureCard
              icon={<Sparkle size={28} weight="fill" />}
              title="Mood-Based Discovery"
              description="Tell us how you feel. We'll find content that matches your emotional state — or helps you change it."
              gradient="from-primary-500 to-primary-600"
              delay={0.1}
            />
            <FeatureCard
              icon={<Lightning size={28} weight="fill" />}
              title="Quick Dope Hit"
              description="Can't decide? One button gives you the perfect recommendation instantly. Zero scrolling required."
              gradient="from-secondary-400 to-secondary-500"
              delay={0.2}
            />
            <FeatureCard
              icon={<Brain size={28} weight="fill" />}
              title="AI That Gets It"
              description="Meet Mr.DP, your personal dopamine curator. Just tell him what's on your mind."
              gradient="from-accent-400 to-accent-500"
              delay={0.3}
            />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="relative z-10 py-16 md:py-24 px-4 bg-surface-50 dark:bg-dark-card/50">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-surface-900 dark:text-white mb-4">
              How it works
            </h2>
            <p className="text-surface-600 dark:text-surface-400">
              From overwhelmed to entertained in three simple steps
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            <Step
              number={1}
              title="Tell us how you feel"
              description="Select your current emotional state from our intuitive mood wheel."
              delay={0.1}
            />
            <Step
              number={2}
              title="Choose your destination"
              description="Where do you want to be? Relaxed? Energized? Focused? Pick your target mood."
              delay={0.2}
            />
            <Step
              number={3}
              title="Get perfect picks"
              description="Receive personalized recommendations across movies, TV, music, and more."
              delay={0.3}
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 py-16 md:py-24 px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-3xl mx-auto"
        >
          <div className="relative p-8 md:p-12 rounded-3xl bg-gradient-to-br from-primary-500 via-primary-600 to-secondary-500 shadow-glow overflow-hidden">
            {/* Background pattern */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute inset-0" style={{
                backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
                backgroundSize: '32px 32px',
              }} />
            </div>

            <div className="relative text-center">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                Ready to boss your dopamine?
              </h2>
              <p className="text-white/80 mb-8 max-w-lg mx-auto">
                Join thousands of neurodivergent minds who've stopped doom-scrolling
                and started actually watching.
              </p>
              <Link href="/app">
                <Button
                  size="lg"
                  variant="secondary"
                  className="bg-white text-primary-600 hover:bg-white/90 border-none"
                  icon={<ArrowRight size={20} weight="bold" />}
                  iconPosition="right"
                >
                  Get Started Free
                </Button>
              </Link>
              <p className="text-white/60 text-sm mt-4">
                No credit card required • Works on all devices
              </p>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 py-8 px-4 border-t border-surface-100 dark:border-dark-border">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-surface-500 dark:text-surface-400">
            <Sparkle size={20} weight="fill" className="text-primary-500" />
            <span>© 2026 dopamine.watch</span>
          </div>
          <div className="flex items-center gap-6 text-sm">
            <Link href="/privacy" className="text-surface-500 hover:text-surface-700 dark:hover:text-surface-300">
              Privacy
            </Link>
            <Link href="/terms" className="text-surface-500 hover:text-surface-700 dark:hover:text-surface-300">
              Terms
            </Link>
            <Link href="/blog" className="text-surface-500 hover:text-surface-700 dark:hover:text-surface-300">
              Blog
            </Link>
          </div>
        </div>
      </footer>
    </div>
  )
}

// Stat component
function Stat({
  value,
  label,
  icon,
}: {
  value: string
  label: string
  icon?: React.ReactNode
}) {
  return (
    <div className="text-center">
      <div className="flex items-center justify-center gap-1">
        <span className="text-2xl md:text-3xl font-bold text-surface-900 dark:text-white">
          {value}
        </span>
        {icon}
      </div>
      <span className="text-sm text-surface-500 dark:text-surface-400">{label}</span>
    </div>
  )
}

// Feature Card component
function FeatureCard({
  icon,
  title,
  description,
  gradient,
  delay,
}: {
  icon: React.ReactNode
  title: string
  description: string
  gradient: string
  delay: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay }}
      className="group p-6 rounded-2xl bg-white dark:bg-dark-card border border-surface-100 dark:border-dark-border shadow-card hover:shadow-card-hover transition-all duration-300 hover:-translate-y-1"
    >
      <div
        className={cn(
          'w-14 h-14 rounded-xl flex items-center justify-center mb-4',
          'bg-gradient-to-br',
          gradient,
          'text-white shadow-lg'
        )}
      >
        {icon}
      </div>
      <h3 className="text-xl font-semibold text-surface-900 dark:text-white mb-2">
        {title}
      </h3>
      <p className="text-surface-600 dark:text-surface-400">
        {description}
      </p>
    </motion.div>
  )
}

// Step component
function Step({
  number,
  title,
  description,
  delay,
}: {
  number: number
  title: string
  description: string
  delay: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay }}
      className="text-center"
    >
      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-500 to-secondary-400 text-white text-xl font-bold flex items-center justify-center mx-auto mb-4 shadow-glow-sm">
        {number}
      </div>
      <h3 className="text-xl font-semibold text-surface-900 dark:text-white mb-2">
        {title}
      </h3>
      <p className="text-surface-600 dark:text-surface-400">
        {description}
      </p>
    </motion.div>
  )
}
