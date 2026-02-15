import Link from "next/link";

export const metadata = {
  title: "Privacy Policy | dopamine.watch",
  description: "Privacy Policy for dopamine.watch",
};

export default function PrivacyPolicy() {
  return (
    <main className="min-h-screen bg-background py-16 px-4">
      <div className="max-w-3xl mx-auto">
        <Link
          href="/"
          className="text-sm text-muted hover:text-foreground transition-colors mb-8 inline-block"
        >
          &larr; Back to home
        </Link>

        <h1 className="text-4xl font-bold mb-2">Privacy Policy</h1>
        <p className="text-muted mb-8">Last updated: February 14, 2026</p>

        <div className="prose prose-invert max-w-none space-y-8">
          <section>
            <h2 className="text-2xl font-semibold mb-3">
              1. Our Commitment to Privacy
            </h2>
            <p className="text-foreground/80 leading-relaxed">
              dopamine.watch is built for neurodivergent minds. We understand
              that emotional and health-related data is deeply personal. We
              collect only what is necessary to provide the Service and will
              never sell your data to third parties.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">
              2. Information We Collect
            </h2>
            <p className="text-foreground/80 leading-relaxed mb-3">
              We collect the following categories of information:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-foreground/80">
              <li>
                <strong>Account Information:</strong> Email address, display
                name, and authentication data (via Supabase Auth or Google
                OAuth)
              </li>
              <li>
                <strong>Mood and Preference Data:</strong> Mood selections,
                content preferences, and emotional state transitions you
                voluntarily provide
              </li>
              <li>
                <strong>Chat Messages:</strong> Messages sent in community chat
                channels (stored in Supabase)
              </li>
              <li>
                <strong>Usage Data:</strong> Pages visited, features used, and
                session duration for improving the Service
              </li>
              <li>
                <strong>Health Reminders:</strong> Meal and break timing data
                stored locally on your device
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">
              3. How We Use Your Information
            </h2>
            <ul className="list-disc pl-6 space-y-2 text-foreground/80">
              <li>
                Provide personalized content recommendations based on emotional
                state
              </li>
              <li>
                Power AI features (Mr.DP chatbot, meal planning) using
                anonymized context
              </li>
              <li>
                Send health and wellness reminders (opt-in, user-controlled)
              </li>
              <li>Improve the Service through aggregated, anonymized analytics</li>
              <li>
                Communicate important updates about the Service
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">
              4. Third-Party Services
            </h2>
            <p className="text-foreground/80 leading-relaxed mb-3">
              We use the following third-party services:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-foreground/80">
              <li>
                <strong>Supabase:</strong> Authentication, database, real-time
                messaging (hosted in US)
              </li>
              <li>
                <strong>OpenAI:</strong> AI-powered recommendations and meal
                planning (data not used for training)
              </li>
              <li>
                <strong>Anthropic:</strong> Mr.DP chatbot and admin
                orchestration (data not used for training)
              </li>
              <li>
                <strong>TMDB:</strong> Movie and TV show metadata (no user data
                shared)
              </li>
              <li>
                <strong>Google OAuth:</strong> Optional sign-in method (only
                email and name shared)
              </li>
              <li>
                <strong>Vercel:</strong> Hosting and deployment
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">
              5. Data Storage and Security
            </h2>
            <p className="text-foreground/80 leading-relaxed">
              Data is stored in Supabase (PostgreSQL) with row-level security
              policies. All connections use TLS encryption. Health reminder data
              (meal times, break reminders) is stored locally in your browser
              using localStorage and is never sent to our servers. We implement
              rate limiting, input validation, and security headers to protect
              the Service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">
              6. Your Rights
            </h2>
            <p className="text-foreground/80 leading-relaxed mb-3">
              You have the right to:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-foreground/80">
              <li>Access your personal data</li>
              <li>Request correction of inaccurate data</li>
              <li>Request deletion of your account and associated data</li>
              <li>Export your data in a portable format</li>
              <li>Opt out of non-essential data collection</li>
              <li>Withdraw consent at any time</li>
            </ul>
            <p className="text-foreground/80 leading-relaxed mt-3">
              To exercise these rights, contact{" "}
              <a
                href="mailto:privacy@dopamine.watch"
                className="text-primary hover:text-primary-hover"
              >
                privacy@dopamine.watch
              </a>
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">
              7. Sensitive Data Handling
            </h2>
            <p className="text-foreground/80 leading-relaxed">
              We recognize that mood data, ADHD-related preferences, and
              wellness information are sensitive. This data is never shared with
              advertisers, never used for targeted advertising, and never sold
              to data brokers. AI interactions are processed in real-time and
              not stored beyond your active session unless explicitly saved by
              you.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">
              8. Children&apos;s Privacy
            </h2>
            <p className="text-foreground/80 leading-relaxed">
              The Service is not intended for children under 13. We do not
              knowingly collect personal information from children under 13. If
              you believe a child under 13 has provided us with personal
              information, please contact us and we will delete it promptly.
              Users aged 13-17 must have parental consent.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">
              9. Cookies and Local Storage
            </h2>
            <p className="text-foreground/80 leading-relaxed">
              We use essential cookies for authentication (Supabase session
              tokens). We use localStorage for user preferences (presence
              state, health reminder timings, theme settings). We do not use
              tracking cookies or third-party advertising cookies.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">
              10. Changes to This Policy
            </h2>
            <p className="text-foreground/80 leading-relaxed">
              We may update this Privacy Policy from time to time. We will
              notify users of significant changes via email or in-app
              notification. Your continued use of the Service constitutes
              acceptance of the updated policy.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">11. Contact</h2>
            <p className="text-foreground/80 leading-relaxed">
              For privacy concerns or data requests, contact{" "}
              <a
                href="mailto:privacy@dopamine.watch"
                className="text-primary hover:text-primary-hover"
              >
                privacy@dopamine.watch
              </a>
            </p>
          </section>
        </div>
      </div>
    </main>
  );
}
