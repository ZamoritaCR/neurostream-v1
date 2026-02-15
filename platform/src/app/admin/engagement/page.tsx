"use client";

import { useState } from "react";

export default function EngagementAgentPage() {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"email" | "streak">("email");

  // Email state
  const [emailUserName, setEmailUserName] = useState("");
  const [emailLastActive, setEmailLastActive] = useState("7 days ago");
  const [emailPrefs, setEmailPrefs] = useState("comedy, documentaries, calm content");
  const [generatedEmail, setGeneratedEmail] = useState<{
    subject?: string;
    body?: string;
  } | null>(null);

  // Streak state
  const [streakUserName, setStreakUserName] = useState("");
  const [streakDays, setStreakDays] = useState(7);
  const [celebration, setCelebration] = useState("");

  const handleGenerateEmail = async () => {
    if (!emailUserName.trim()) return;
    setLoading(true);

    try {
      const res = await fetch("/api/admin/agents/engagement", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "generateEmail",
          params: {
            userName: emailUserName,
            lastActive: emailLastActive,
            userPreferences: { interests: emailPrefs },
          },
        }),
      });
      const data = await res.json();
      setGeneratedEmail(data.email);
    } catch (error) {
      console.error("Email generation error:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCelebrateStreak = async () => {
    if (!streakUserName.trim()) return;
    setLoading(true);

    try {
      const res = await fetch("/api/admin/agents/engagement", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "celebrateStreak",
          params: {
            userName: streakUserName,
            streakDays,
          },
        }),
      });
      const data = await res.json();
      setCelebration(data.celebration);
    } catch (error) {
      console.error("Streak error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Engagement Engine</h1>
        <p className="text-muted">
          Create re-engagement emails and celebrate streaks (never guilt)
        </p>
        <p className="text-xs text-accent mt-1">
          Research: Brain 5, Section 4 &mdash; Celebrate attempts, never shame
          breaks
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {(["email", "streak"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === tab
                ? "bg-primary text-white"
                : "bg-surface-hover text-muted hover:text-foreground"
            }`}
          >
            {tab === "email" ? "Re-engagement Email" : "Streak Celebration"}
          </button>
        ))}
      </div>

      {activeTab === "email" && (
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Input */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                User Name
              </label>
              <input
                type="text"
                value={emailUserName}
                onChange={(e) => setEmailUserName(e.target.value)}
                placeholder="e.g., Sarah"
                className="w-full px-4 py-3 bg-surface border border-border rounded-lg text-sm focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Last Active
              </label>
              <select
                value={emailLastActive}
                onChange={(e) => setEmailLastActive(e.target.value)}
                className="w-full px-4 py-3 bg-surface border border-border rounded-lg text-sm focus:outline-none focus:border-primary"
              >
                <option value="3 days ago">3 days ago</option>
                <option value="7 days ago">7 days ago</option>
                <option value="14 days ago">14 days ago</option>
                <option value="30 days ago">30 days ago</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                User Interests
              </label>
              <input
                type="text"
                value={emailPrefs}
                onChange={(e) => setEmailPrefs(e.target.value)}
                placeholder="e.g., comedy, nature docs, calm content"
                className="w-full px-4 py-3 bg-surface border border-border rounded-lg text-sm focus:outline-none focus:border-primary"
              />
            </div>

            <div className="p-3 bg-accent/10 border border-accent/30 rounded-lg">
              <p className="text-xs text-accent">
                Harm Prevention: All emails avoid guilt language. No
                &quot;We miss you&quot; or &quot;You&apos;ve been away.&quot;
                Instead: &quot;Whenever you&apos;re ready&quot; and
                &quot;Something new you might enjoy.&quot;
              </p>
            </div>

            <button
              onClick={handleGenerateEmail}
              disabled={loading || !emailUserName.trim()}
              className="w-full py-3 bg-primary hover:bg-primary-hover text-white rounded-lg font-semibold disabled:opacity-50 transition-colors"
            >
              {loading ? "Generating..." : "Generate Email"}
            </button>
          </div>

          {/* Output */}
          <div>
            {generatedEmail ? (
              <div className="p-6 bg-surface border border-border rounded-lg space-y-4">
                <div>
                  <p className="text-xs text-muted mb-1">Subject Line</p>
                  <p className="font-semibold text-lg">
                    {generatedEmail.subject}
                  </p>
                </div>
                <hr className="border-border" />
                <div>
                  <p className="text-xs text-muted mb-2">Email Body</p>
                  <div className="whitespace-pre-wrap text-sm leading-relaxed text-foreground/90">
                    {generatedEmail.body}
                  </div>
                </div>
                <div className="flex gap-2 pt-2">
                  <button
                    onClick={() =>
                      navigator.clipboard.writeText(
                        `Subject: ${generatedEmail.subject}\n\n${generatedEmail.body}`
                      )
                    }
                    className="px-4 py-2 bg-surface-hover hover:bg-border rounded-lg text-xs transition-colors"
                  >
                    Copy Email
                  </button>
                  <button
                    onClick={handleGenerateEmail}
                    disabled={loading}
                    className="px-4 py-2 bg-surface-hover hover:bg-border rounded-lg text-xs transition-colors"
                  >
                    Regenerate
                  </button>
                </div>
              </div>
            ) : (
              <div className="p-8 bg-surface border border-border rounded-lg text-center">
                <p className="text-muted">
                  Generated email will appear here...
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === "streak" && (
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Input */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                User Name
              </label>
              <input
                type="text"
                value={streakUserName}
                onChange={(e) => setStreakUserName(e.target.value)}
                placeholder="e.g., Alex"
                className="w-full px-4 py-3 bg-surface border border-border rounded-lg text-sm focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Streak Days: {streakDays}
              </label>
              <input
                type="range"
                min={1}
                max={365}
                value={streakDays}
                onChange={(e) => setStreakDays(Number(e.target.value))}
                className="w-full accent-primary"
              />
              <div className="flex justify-between text-xs text-muted mt-1">
                <span>1 day</span>
                <span>365 days</span>
              </div>
            </div>

            {/* Milestone hints */}
            <div className="flex flex-wrap gap-2">
              {[3, 7, 14, 30, 50, 100, 365].map((d) => (
                <button
                  key={d}
                  onClick={() => setStreakDays(d)}
                  className={`px-3 py-1 rounded-full text-xs transition-colors ${
                    streakDays === d
                      ? "bg-primary text-white"
                      : "bg-surface-hover text-muted hover:text-foreground"
                  }`}
                >
                  {d} days
                </button>
              ))}
            </div>

            <button
              onClick={handleCelebrateStreak}
              disabled={loading || !streakUserName.trim()}
              className="w-full py-3 bg-accent hover:opacity-90 text-background rounded-lg font-semibold disabled:opacity-50 transition-colors"
            >
              {loading ? "Generating..." : "Generate Celebration"}
            </button>
          </div>

          {/* Output */}
          <div>
            {celebration ? (
              <div className="p-6 bg-gradient-to-br from-primary/10 to-accent/10 border border-primary/30 rounded-lg">
                <p className="text-xs text-muted mb-2">
                  Streak Celebration for {streakUserName} ({streakDays} days)
                </p>
                <p className="text-lg leading-relaxed">{celebration}</p>
                <button
                  onClick={handleCelebrateStreak}
                  disabled={loading}
                  className="mt-4 px-4 py-2 bg-surface-hover hover:bg-border rounded-lg text-xs transition-colors"
                >
                  Regenerate
                </button>
              </div>
            ) : (
              <div className="p-8 bg-surface border border-border rounded-lg text-center">
                <p className="text-muted">
                  Celebration message will appear here...
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
