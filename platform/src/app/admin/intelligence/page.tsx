"use client";

import { useState } from "react";

export default function IntelligenceAgentPage() {
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<Record<string, unknown> | null>(
    null
  );
  const [insight, setInsight] = useState("");
  const [userName, setUserName] = useState("");

  // Sample data for demo — in production, this comes from Supabase
  const sampleUserData = {
    watchHistory: [
      { title: "The Office", mood: "stressed", date: "2026-02-10" },
      { title: "Planet Earth", mood: "anxious", date: "2026-02-11" },
      { title: "Brooklyn Nine-Nine", mood: "sad", date: "2026-02-12" },
      { title: "Chef's Table", mood: "bored", date: "2026-02-13" },
      { title: "Ted Lasso", mood: "tired", date: "2026-02-14" },
    ],
    moodSelections: [
      { current: "stressed", target: "calm", date: "2026-02-10" },
      { current: "anxious", target: "grounded", date: "2026-02-11" },
      { current: "sad", target: "happy", date: "2026-02-12" },
      { current: "bored", target: "energized", date: "2026-02-13" },
      { current: "tired", target: "relaxed", date: "2026-02-14" },
    ],
    timeOfDay: [
      "evening",
      "evening",
      "night",
      "afternoon",
      "evening",
    ],
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setInsight("");

    try {
      const res = await fetch("/api/admin/agents/intelligence", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "analyzePatterns",
          params: { userData: sampleUserData },
        }),
      });
      const data = await res.json();
      setAnalysis(data.analysis);
    } catch (error) {
      console.error("Analysis error:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleInsight = async () => {
    if (!analysis || !userName.trim()) return;
    setLoading(true);

    try {
      const res = await fetch("/api/admin/agents/intelligence", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "generateInsight",
          params: { userName, analysis },
        }),
      });
      const data = await res.json();
      setInsight(data.insight);
    } catch (error) {
      console.error("Insight error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">User Intelligence Agent</h1>
        <p className="text-muted">
          Analyze user patterns and generate personalized insights
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Input / Controls */}
        <div className="space-y-6">
          {/* Sample Data Preview */}
          <div className="p-4 bg-surface border border-border rounded-lg">
            <h3 className="text-sm font-medium mb-3">
              Sample User Data (Demo)
            </h3>
            <div className="space-y-2 text-xs text-muted">
              <p className="font-medium text-foreground">Watch History:</p>
              {sampleUserData.watchHistory.map((w, i) => (
                <p key={i}>
                  {w.date}: {w.title} (feeling {w.mood})
                </p>
              ))}
              <p className="font-medium text-foreground mt-3">
                Mood Transitions:
              </p>
              {sampleUserData.moodSelections.map((m, i) => (
                <p key={i}>
                  {m.date}: {m.current} &rarr; {m.target}
                </p>
              ))}
            </div>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="w-full py-3 bg-primary hover:bg-primary-hover text-white rounded-lg font-semibold disabled:opacity-50 transition-colors"
          >
            {loading && !analysis
              ? "Analyzing..."
              : "Analyze User Patterns"}
          </button>

          {analysis && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  User Name (for personalized insight)
                </label>
                <input
                  type="text"
                  value={userName}
                  onChange={(e) => setUserName(e.target.value)}
                  placeholder="e.g., Sarah"
                  className="w-full px-4 py-3 bg-surface border border-border rounded-lg text-sm focus:outline-none focus:border-primary"
                />
              </div>

              <button
                onClick={handleInsight}
                disabled={loading || !userName.trim()}
                className="w-full py-3 bg-accent hover:opacity-90 text-background rounded-lg font-semibold disabled:opacity-50 transition-colors"
              >
                {loading && !insight
                  ? "Generating..."
                  : "Generate Personalized Insight"}
              </button>
            </div>
          )}
        </div>

        {/* Results */}
        <div className="space-y-6">
          {analysis && (
            <div className="p-4 bg-surface border border-border rounded-lg">
              <h3 className="text-sm font-medium text-muted mb-3">
                Pattern Analysis
              </h3>
              <div className="space-y-4">
                {Object.entries(analysis).map(([key, value]) => (
                  <div key={key}>
                    <p className="text-xs text-muted uppercase tracking-wider mb-1">
                      {key.replace(/([A-Z])/g, " $1").trim()}
                    </p>
                    {Array.isArray(value) ? (
                      <div className="flex flex-wrap gap-2">
                        {value.map((v: string, i: number) => (
                          <span
                            key={i}
                            className="px-2 py-1 bg-surface-hover rounded text-xs"
                          >
                            {v}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm">{String(value)}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {insight && (
            <div className="p-4 bg-gradient-to-r from-primary/10 to-accent/10 border border-primary/30 rounded-lg">
              <h3 className="text-sm font-medium mb-2">
                Personalized Insight for {userName}
              </h3>
              <p className="text-sm leading-relaxed">{insight}</p>
            </div>
          )}

          {!analysis && !insight && (
            <div className="p-8 bg-surface border border-border rounded-lg text-center">
              <p className="text-muted">
                Click &quot;Analyze User Patterns&quot; to start
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
