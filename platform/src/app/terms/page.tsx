import Link from "next/link";

export const metadata = {
  title: "Terms of Service | dopamine.watch",
  description: "Terms of Service for dopamine.watch",
};

export default function TermsOfService() {
  return (
    <main className="min-h-screen bg-background py-16 px-4">
      <div className="max-w-3xl mx-auto">
        <Link
          href="/"
          className="text-sm text-muted hover:text-foreground transition-colors mb-8 inline-block"
        >
          &larr; Back to home
        </Link>

        <h1 className="text-4xl font-bold mb-2">Terms of Service</h1>
        <p className="text-muted mb-8">Last updated: February 14, 2026</p>

        <div className="prose prose-invert max-w-none space-y-8">
          <section>
            <h2 className="text-2xl font-semibold mb-3">
              1. Acceptance of Terms
            </h2>
            <p className="text-foreground/80 leading-relaxed">
              By accessing or using dopamine.watch (&quot;the Service&quot;),
              you agree to be bound by these Terms of Service. If you do not
              agree, please do not use the Service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">
              2. Description of Service
            </h2>
            <p className="text-foreground/80 leading-relaxed">
              dopamine.watch is an ADHD-friendly content discovery platform that
              helps neurodivergent users find media based on emotional state
              transitions. The Service includes content recommendations, chat,
              meal planning, and AI-assisted features. The Service is NOT a
              medical device and does NOT provide medical advice, diagnosis, or
              treatment.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">3. Eligibility</h2>
            <p className="text-foreground/80 leading-relaxed">
              You must be at least 13 years old to use the Service. If you are
              under 18, you must have parental or guardian consent. By using the
              Service, you represent that you meet these requirements.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">4. User Accounts</h2>
            <p className="text-foreground/80 leading-relaxed">
              You are responsible for maintaining the confidentiality of your
              account credentials. You agree to notify us immediately of any
              unauthorized access to your account. We reserve the right to
              suspend or terminate accounts that violate these terms.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">
              5. Acceptable Use
            </h2>
            <p className="text-foreground/80 leading-relaxed mb-3">
              You agree not to:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-foreground/80">
              <li>Use the Service for any illegal purpose</li>
              <li>Harass, abuse, or harm other users</li>
              <li>
                Attempt to gain unauthorized access to any part of the Service
              </li>
              <li>
                Use automated systems to access the Service without permission
              </li>
              <li>Share harmful, abusive, or inappropriate content in chat</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">
              6. Health Disclaimer
            </h2>
            <p className="text-foreground/80 leading-relaxed">
              dopamine.watch is designed as a supportive tool, not a replacement
              for professional medical or mental health care. Features like mood
              tracking, wellness reminders, and coping techniques are
              informational only. Always consult a qualified healthcare
              professional for medical concerns. If you are in crisis, contact
              your local emergency services or the 988 Suicide &amp; Crisis
              Lifeline.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">
              7. Intellectual Property
            </h2>
            <p className="text-foreground/80 leading-relaxed">
              All content, branding, and technology of the Service are owned by
              dopamine.watch. Content recommendations are sourced from
              third-party APIs (TMDB, etc.) and remain the property of their
              respective owners.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">
              8. Limitation of Liability
            </h2>
            <p className="text-foreground/80 leading-relaxed">
              The Service is provided &quot;as is&quot; without warranties of
              any kind. We are not liable for any indirect, incidental, or
              consequential damages arising from your use of the Service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">
              9. Changes to Terms
            </h2>
            <p className="text-foreground/80 leading-relaxed">
              We may update these Terms at any time. Continued use of the
              Service after changes constitutes acceptance of the updated Terms.
              We will notify users of significant changes via email or
              in-app notification.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">10. Contact</h2>
            <p className="text-foreground/80 leading-relaxed">
              Questions about these Terms? Contact us at{" "}
              <a
                href="mailto:legal@dopamine.watch"
                className="text-primary hover:text-primary-hover"
              >
                legal@dopamine.watch
              </a>
            </p>
          </section>
        </div>
      </div>
    </main>
  );
}
