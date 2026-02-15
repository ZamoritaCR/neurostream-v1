import Link from "next/link";
import { notFound } from "next/navigation";

interface BlogPostContent {
  title: string;
  date: string;
  author: string;
  tags: string[];
  content: string;
}

// Blog post content (in real app, this would come from markdown files or CMS)
const posts: Record<string, BlogPostContent> = {
  "introducing-dopamine-watch": {
    title:
      "Introducing dopamine.watch: The Operating System for Neurodivergent Minds",
    date: "2026-02-14",
    author: "Johan",
    tags: ["announcement", "product", "neurodiversity"],
    content: `
# Welcome to dopamine.watch

Today, we're launching **dopamine.watch** - a privacy-first digital toolkit designed specifically for ADHD and autistic minds.

## The Problem

Traditional apps treat everyone the same. They assume:
- You can handle infinite choices without decision fatigue
- Algorithmic recommendations based on watch history serve you well
- More features = better experience
- Privacy is a premium feature

For neurodivergent users, these assumptions break down.

## Our Solution

dopamine.watch is built on three core principles:

### 1. Feel-First, Not Algorithm-First

Instead of "because you watched Breaking Bad, here's Better Call Saul," we ask:
- How do you feel RIGHT NOW?
- How do you WANT to feel?
- What emotional journey do you need?

Content becomes medicine for emotional states.

### 2. Privacy is Fundamental

No face scans. No government IDs. No surveillance capitalism.

Your emotional state, viewing preferences, and conversations are YOURS.

### 3. ADHD-Optimized Design

- Lexend font for improved readability
- Reduced motion support
- Softened colors (no harsh reds)
- Clear visual hierarchy
- Keyboard shortcuts for power users
- No guilt mechanics or shame patterns

## What We're Building

**Already Available:**
- Content Discovery - Find what to watch based on emotional state
- Private Chat - Real-time messaging without surveillance
- Mr.DP - AI companion for emotional support

**Coming Soon:**
- Meal Planning - ADHD-friendly recipes
- Smart Home Control - Mood-based automation
- The Cockpit - Unified mobile control

## Research-Backed

Every design decision traces back to our knowledge base:
- 425+ peer-reviewed citations
- 8 research "brains" covering ADHD, psychology, UX, gamification
- DBT/CBT techniques integrated
- Harm prevention at the core

## Join Us

This is just the beginning. We're building the operating system for neurodivergent minds - one feature at a time.

Welcome to the dopamine.* ecosystem.

-- Johan & Mr.DP
    `,
  },
  "why-privacy-matters": {
    title: "Why Privacy Matters for Neurodivergent Users",
    date: "2026-02-14",
    author: "Johan",
    tags: ["privacy", "discord", "community"],
    content: `
# Why Privacy Matters for Neurodivergent Users

Discord recently announced mandatory face scans and government ID verification. For the neurodivergent community, this isn't just inconvenient - it's a fundamental violation of trust.

## The Discord Exodus

Within days of the announcement:
- 10,000% spike in searches for "Discord alternatives"
- Thousands of ADHD/autism communities seeking new homes
- Privacy-conscious users fleeing en masse

But this isn't just about Discord. It's about a pattern.

## Why Neurodivergent Users Need Privacy

### 1. Masking and Authentic Expression

Many neurodivergent people "mask" in public - hiding their true selves to fit neurotypical expectations. Online spaces have been safe havens for authentic expression.

Mandatory identity verification eliminates this safety.

### 2. Employment Discrimination

ADHD and autism are protected disabilities, but discrimination happens.

Real names + face scans = potential employment consequences for being openly neurodivergent.

### 3. Medical Privacy

Many users discuss medication, therapy, and diagnoses in private communities.

Identity verification creates a permanent link between these discussions and real identities.

### 4. Harassment Protection

Neurodivergent users face higher rates of online harassment.

Pseudonymity is a safety tool, not a luxury.

## Our Approach

dopamine/chat is built on these privacy principles:

**No Identity Verification:**
- Email + password only
- No phone numbers required
- No face scans, ever

**Data Minimization:**
- We collect what we need, nothing more
- No selling data to advertisers
- No surveillance capitalism

**User Control:**
- Delete your data anytime
- Export your conversations
- Choose your visibility

**End-to-End Encryption (Coming Soon):**
- Private conversations stay private
- Not even we can read them

## The Bigger Picture

Privacy isn't about having "something to hide."

It's about having something to protect: your authentic self.

For neurodivergent users, privacy enables:
- Safe experimentation with identity
- Honest discussion of struggles
- Community without consequence
- Freedom to be yourself

## Join the Movement

We're building alternatives. Privacy-first. Neurodivergent-optimized. Community-owned.

Discord's loss is our opportunity to build something better.

-- Johan
    `,
  },
};

// Generate static params for all known blog posts
export function generateStaticParams() {
  return Object.keys(posts).map((slug) => ({ slug }));
}

export default async function BlogPostPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const post = posts[slug];

  if (!post) {
    notFound();
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border py-8 px-4">
        <div className="max-w-3xl mx-auto">
          <Link
            href="/blog"
            className="text-primary hover:text-primary-hover text-sm mb-4 inline-block"
          >
            &larr; Back to Blog
          </Link>
        </div>
      </header>

      {/* Article */}
      <article className="max-w-3xl mx-auto px-4 py-12">
        {/* Meta */}
        <div className="flex items-center gap-3 text-sm text-muted mb-6">
          <time dateTime={post.date}>
            {new Date(post.date).toLocaleDateString("en-US", {
              month: "long",
              day: "numeric",
              year: "numeric",
            })}
          </time>
          <span>&bull;</span>
          <span>{post.author}</span>
        </div>

        {/* Title */}
        <h1 className="text-4xl md:text-5xl font-bold mb-6">
          <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            {post.title}
          </span>
        </h1>

        {/* Tags */}
        <div className="flex gap-2 mb-12">
          {post.tags.map((tag) => (
            <span
              key={tag}
              className="px-3 py-1 bg-surface border border-border rounded-full text-xs text-muted"
            >
              {tag}
            </span>
          ))}
        </div>

        {/* Content */}
        <div className="prose prose-invert prose-primary max-w-none">
          {post.content.split("\n").map((paragraph, i) => {
            if (paragraph.startsWith("# ")) {
              return (
                <h1 key={i} className="text-3xl font-bold mt-12 mb-6">
                  {paragraph.substring(2)}
                </h1>
              );
            }
            if (paragraph.startsWith("## ")) {
              return (
                <h2 key={i} className="text-2xl font-bold mt-8 mb-4">
                  {paragraph.substring(3)}
                </h2>
              );
            }
            if (paragraph.startsWith("### ")) {
              return (
                <h3 key={i} className="text-xl font-bold mt-6 mb-3">
                  {paragraph.substring(4)}
                </h3>
              );
            }
            if (paragraph.startsWith("**") && paragraph.endsWith("**")) {
              return (
                <p key={i} className="font-semibold mt-4">
                  {paragraph.slice(2, -2)}
                </p>
              );
            }
            if (paragraph.startsWith("- ")) {
              return (
                <li key={i} className="ml-6 my-2">
                  {paragraph.substring(2)}
                </li>
              );
            }
            if (paragraph.trim() === "") {
              return <div key={i} className="h-4" />;
            }
            return (
              <p key={i} className="my-4 text-foreground/90 leading-relaxed">
                {paragraph}
              </p>
            );
          })}
        </div>
      </article>
    </div>
  );
}
