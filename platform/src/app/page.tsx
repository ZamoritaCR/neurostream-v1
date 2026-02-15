export default function Home() {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-surface to-background py-20 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              dopamine.watch
            </span>
          </h1>
          <p className="text-2xl md:text-3xl text-foreground/90 mb-4">
            The Operating System for Neurodivergent Minds
          </p>
          <p className="text-lg md:text-xl text-muted max-w-2xl mx-auto mb-8">
            Your digital toolkit for ADHD and autistic brains. Privacy-first.
            Research-backed. Built for how you actually think.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/watch"
              className="px-8 py-4 bg-primary hover:bg-primary-hover text-white rounded-lg font-semibold transition-colors"
            >
              Start Watching
            </a>
            <a
              href="/chat"
              className="px-8 py-4 bg-surface hover:bg-surface-hover border border-border text-foreground rounded-lg font-semibold transition-colors"
            >
              Join Chat
            </a>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">
            Your Digital Toolkit
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Content Discovery */}
            <div className="p-6 bg-surface rounded-lg border border-border hover:border-primary transition-colors">
              <div className="w-12 h-12 bg-gradient-to-br from-primary to-accent rounded-lg mb-4 flex items-center justify-center">
                <div className="w-6 h-6 bg-white/20 rounded" />
              </div>
              <h3 className="text-xl font-bold mb-2">Content Discovery</h3>
              <p className="text-muted mb-4 text-sm">
                Find what to watch based on emotional state transitions, not
                algorithms.
              </p>
              <a
                href="/watch"
                className="text-primary hover:text-primary-hover text-sm font-medium"
              >
                Start watching &rarr;
              </a>
            </div>

            {/* Private Chat */}
            <div className="p-6 bg-surface rounded-lg border border-border hover:border-primary transition-colors">
              <div className="w-12 h-12 bg-gradient-to-br from-primary to-accent rounded-lg mb-4 flex items-center justify-center">
                <div className="w-6 h-6 bg-white/20 rounded-full" />
              </div>
              <h3 className="text-xl font-bold mb-2">Private Chat</h3>
              <p className="text-muted mb-4 text-sm">
                Real-time messaging without surveillance. Your conversations,
                your data.
              </p>
              <a
                href="/chat"
                className="text-primary hover:text-primary-hover text-sm font-medium"
              >
                Join chat &rarr;
              </a>
            </div>

            {/* Meal Planning */}
            <div className="p-6 bg-surface rounded-lg border border-border hover:border-primary transition-colors">
              <div className="w-12 h-12 bg-gradient-to-br from-primary to-accent rounded-lg mb-4 flex items-center justify-center">
                <div className="w-6 h-6 bg-white/20 rounded-sm" />
              </div>
              <h3 className="text-xl font-bold mb-2">Meal Planning</h3>
              <p className="text-muted mb-4 text-sm">
                ADHD-optimized nutrition. Never forget to eat during hyperfocus
                again.
              </p>
              <a
                href="/food"
                className="text-primary hover:text-primary-hover text-sm font-medium"
              >
                Plan meals &rarr;
              </a>
            </div>

            {/* Smart Home (Coming Soon) */}
            <div className="p-6 bg-surface/50 rounded-lg border border-border opacity-60">
              <div className="w-12 h-12 bg-muted/30 rounded-lg mb-4 flex items-center justify-center">
                <div className="w-6 h-6 bg-white/10 rounded-lg" />
              </div>
              <h3 className="text-xl font-bold mb-2">Smart Home</h3>
              <p className="text-muted mb-4 text-sm">
                Mood-based automation for lighting, climate, and ambiance.
              </p>
              <span className="text-muted text-sm">Coming soon</span>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <div className="flex justify-center gap-6 mb-4">
            <a
              href="/blog"
              className="text-primary hover:text-primary-hover"
            >
              Blog
            </a>
            <a
              href="/about"
              className="text-muted hover:text-foreground"
            >
              About
            </a>
            <a
              href="https://github.com/ZamoritaCR"
              className="text-muted hover:text-foreground"
            >
              GitHub
            </a>
          </div>
          <div className="flex justify-center gap-6 mb-4">
            <a
              href="/terms"
              className="text-muted hover:text-foreground text-sm"
            >
              Terms of Service
            </a>
            <a
              href="/privacy"
              className="text-muted hover:text-foreground text-sm"
            >
              Privacy Policy
            </a>
          </div>
          <p className="text-muted">
            &copy; 2026 dopamine.watch - Built for neurodivergent minds
          </p>
          <div className="mt-4 pt-4 border-t border-border">
            <p className="text-xs text-muted">
              <strong>Not medical advice.</strong> For crisis support: 988 (US
              Suicide &amp; Crisis Lifeline) | Always consult healthcare
              providers for medical decisions.
            </p>
          </div>
        </div>
      </footer>
    </main>
  );
}
