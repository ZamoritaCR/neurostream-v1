"use client";

import { useAuth } from "@/components/shared/AuthProvider";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { MoodSelector } from "@/components/app/MoodSelector";
import { tmdb, type Movie, type TVShow } from "@/lib/tmdb/client";
import { MrDPChat } from "@/components/app/MrDPChat";
import { HealthMonitor } from "@/components/app/HealthMonitor";

export default function WatchPage() {
  const { user, loading: authLoading, signOut } = useAuth();
  const router = useRouter();

  const [currentMood, setCurrentMood] = useState("");
  const [targetMood, setTargetMood] = useState("");
  const [recommendations, setRecommendations] = useState<(Movie | TVShow)[]>(
    []
  );
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<"current" | "target" | "results">(
    "current"
  );

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/auth");
    }
  }, [user, authLoading, router]);

  const handleGetRecommendations = async () => {
    if (!currentMood || !targetMood) return;

    setLoading(true);
    setStep("results");

    try {
      // Call our API route (keeps OpenAI key server-side)
      const res = await fetch("/api/recommendations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ currentMood, targetMood }),
      });
      const { recommendations: aiRecs } = await res.json();
      const aiTitles: string[] = aiRecs.map(
        (r: { title: string }) => r.title
      );

      // Search TMDB for the AI-recommended titles
      const searchPromises = aiTitles.map(async (title) => {
        const [movies, tv] = await Promise.all([
          tmdb.searchMovies(title),
          tmdb.searchTV(title),
        ]);
        return [...movies, ...tv][0];
      });

      const results = await Promise.all(searchPromises);
      const validResults = results.filter(Boolean);

      // If AI results are sparse, add mood-based discovery
      if (validResults.length < 3) {
        const moodResults = await tmdb.discoverByMood(targetMood);
        validResults.push(
          ...moodResults.slice(0, 5 - validResults.length)
        );
      }

      setRecommendations(validResults);
    } catch (error) {
      console.error("Error getting recommendations:", error);
      // Fallback to mood-based discovery
      const fallback = await tmdb.discoverByMood(targetMood);
      setRecommendations(fallback.slice(0, 5));
    } finally {
      setLoading(false);
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted">Loading...</p>
      </div>
    );
  }

  if (!user) return null;

  const isMovie = (item: Movie | TVShow): item is Movie => "title" in item;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border p-6">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">
              <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                dopamine.watch
              </span>
            </h1>
            <p className="text-muted mt-1">
              Find content based on how you feel
            </p>
          </div>
          <button
            onClick={() => signOut()}
            className="px-4 py-2 bg-surface hover:bg-surface-hover border border-border rounded-lg"
          >
            Sign Out
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-6">
        {/* Step 1: Current Mood */}
        {step === "current" && (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold mb-2">
                How are you feeling right now?
              </h2>
              <p className="text-muted">Select your current emotional state</p>
            </div>

            <MoodSelector
              selectedMood={currentMood}
              onMoodChange={setCurrentMood}
              label="Current Mood"
            />

            {currentMood && (
              <div className="flex justify-center">
                <button
                  onClick={() => setStep("target")}
                  className="px-8 py-3 bg-primary hover:bg-primary-hover text-white rounded-lg font-semibold"
                >
                  Next
                </button>
              </div>
            )}
          </div>
        )}

        {/* Step 2: Target Mood */}
        {step === "target" && (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold mb-2">
                How do you want to feel?
              </h2>
              <p className="text-muted">
                Currently:{" "}
                <span className="text-primary font-semibold">
                  {currentMood}
                </span>
              </p>
            </div>

            <MoodSelector
              selectedMood={targetMood}
              onMoodChange={setTargetMood}
              label="Target Mood"
            />

            {targetMood && (
              <div className="flex justify-center gap-4">
                <button
                  onClick={() => setStep("current")}
                  className="px-8 py-3 bg-surface hover:bg-surface-hover border border-border rounded-lg font-semibold"
                >
                  Back
                </button>
                <button
                  onClick={handleGetRecommendations}
                  disabled={loading}
                  className="px-8 py-3 bg-primary hover:bg-primary-hover text-white rounded-lg font-semibold disabled:opacity-50"
                >
                  {loading ? "Finding content..." : "Get Recommendations"}
                </button>
              </div>
            )}
          </div>
        )}

        {/* Step 3: Results */}
        {step === "results" && (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold mb-2">
                Your Personalized Recommendations
              </h2>
              <p className="text-muted">
                {currentMood} → {targetMood}
              </p>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <p className="text-muted">
                  Finding the perfect content for you...
                </p>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
                  {recommendations.map((item) => (
                    <div
                      key={item.id}
                      className="group cursor-pointer transition-transform hover:scale-105"
                    >
                      <div className="relative aspect-[2/3] rounded-lg overflow-hidden bg-surface mb-2">
                        {item.poster_path ? (
                          <img
                            src={tmdb.getPosterUrl(item.poster_path)}
                            alt={isMovie(item) ? item.title : item.name}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-muted text-sm">
                            No poster
                          </div>
                        )}
                      </div>
                      <h3 className="font-semibold text-sm line-clamp-2">
                        {isMovie(item) ? item.title : item.name}
                      </h3>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-muted">
                          {item.vote_average.toFixed(1)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="flex justify-center mt-8">
                  <button
                    onClick={() => {
                      setStep("current");
                      setCurrentMood("");
                      setTargetMood("");
                      setRecommendations([]);
                    }}
                    className="px-8 py-3 bg-surface hover:bg-surface-hover border border-border rounded-lg font-semibold"
                  >
                    Start Over
                  </button>
                </div>
              </>
            )}
          </div>
        )}
      </main>

      {/* Health Monitor - Research: Brain 1, Section 3 (hyperfocus protection) */}
      <HealthMonitor />

      {/* Mr.DP Floating Chat - Research: Brain 1 (ADHD emotional dysregulation), Brain 6 (DBT/CBT) */}
      <MrDPChat
        context={{
          currentMood: currentMood || undefined,
          targetMood: targetMood || undefined,
          recentActivity: step === "results" ? "viewing recommendations" : "selecting mood",
        }}
      />
    </div>
  );
}
