"use client";

import { useAuth } from "@/components/shared/AuthProvider";
import { usePresenceStore } from "@/stores/presence-store";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { MrDPChat } from "@/components/app/MrDPChat";
import { HealthMonitor } from "@/components/app/HealthMonitor";

// Research: Brain 1, Section 3 — ADHD hyperfocus causes skipped meals
// Research: Brain 5, Section 4 — Celebrate attempts, never shame breaks

interface MealSuggestion {
  name: string;
  timeMinutes: number;
  ingredients: string[];
  steps: string[];
  reason: string;
  nutritionNote: string;
}

export default function FoodPage() {
  const { user, loading: authLoading, signOut } = useAuth();
  const router = useRouter();
  const { currentState, getTimeSinceLastMeal, recordMeal } =
    usePresenceStore();

  const [mealSuggestion, setMealSuggestion] = useState<MealSuggestion | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [selectedMood, setSelectedMood] = useState("");
  const [mealRecorded, setMealRecorded] = useState(false);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/auth");
    }
  }, [user, authLoading, router]);

  const generateMeal = async () => {
    setLoading(true);
    setMealRecorded(false);
    try {
      const timeSinceMeal = getTimeSinceLastMeal() || 0;

      const response = await fetch("/api/food", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          presenceState: currentState,
          timeSinceMeal,
          mood: selectedMood || undefined,
        }),
      });

      const data = await response.json();
      setMealSuggestion(data.meal);
    } catch (error) {
      console.error("Error generating meal:", error);
    } finally {
      setLoading(false);
    }
  };

  const markAsEaten = () => {
    recordMeal();
    setMealRecorded(true);
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted">Loading...</p>
      </div>
    );
  }

  if (!user) return null;

  const timeSinceMeal = getTimeSinceLastMeal();
  const hoursWithoutFood = timeSinceMeal
    ? Math.floor(timeSinceMeal / (1000 * 60 * 60))
    : null;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border p-6">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">
              <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Food Planner
              </span>
            </h1>
            <p className="text-muted mt-1">
              ADHD-friendly meals based on your state
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => router.push("/watch")}
              className="px-4 py-2 text-sm text-primary hover:text-primary-hover"
            >
              Watch
            </button>
            <button
              onClick={() => signOut()}
              className="px-4 py-2 bg-surface hover:bg-surface-hover border border-border rounded-lg text-sm"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto p-6">
        {/* Health Status Alert */}
        {hoursWithoutFood !== null && hoursWithoutFood >= 3 && (
          <div className="mb-6 p-4 bg-accent/10 border border-accent/30 rounded-lg">
            <p className="text-accent font-semibold">
              It&apos;s been {hoursWithoutFood} hours since your last meal
            </p>
            <p className="text-sm text-muted mt-1">
              Let&apos;s get you some fuel. No pressure — even a small snack
              counts.
            </p>
          </div>
        )}

        {/* Current State Display */}
        <div className="mb-6 p-4 bg-surface border border-border rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted">Current State</p>
              <p className="text-lg font-semibold capitalize">
                {currentState.replace("_", " ")}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted">Last Meal</p>
              <p className="text-lg font-semibold">
                {hoursWithoutFood !== null
                  ? `${hoursWithoutFood}h ago`
                  : "Not tracked"}
              </p>
            </div>
          </div>
        </div>

        {/* Mood Selection (Optional) */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-3">
            How are you feeling? (optional)
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {["hungry", "stressed", "tired", "energized"].map((mood) => (
              <button
                key={mood}
                onClick={() =>
                  setSelectedMood(mood === selectedMood ? "" : mood)
                }
                className={`p-3 rounded-lg border-2 transition-all text-sm ${
                  selectedMood === mood
                    ? "border-primary bg-primary/10"
                    : "border-border hover:border-muted"
                }`}
              >
                <span className="capitalize">{mood}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Generate Button */}
        <button
          onClick={generateMeal}
          disabled={loading}
          className="w-full py-4 bg-primary hover:bg-primary-hover text-white font-semibold rounded-lg transition-colors disabled:opacity-50 mb-6"
        >
          {loading ? "Generating meal plan..." : "Get Meal Suggestion"}
        </button>

        {/* Meal Suggestion */}
        {mealSuggestion && (
          <div className="bg-surface border border-border rounded-lg p-6 mb-8">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-2xl font-bold">{mealSuggestion.name}</h2>
                <p className="text-muted mt-1">{mealSuggestion.reason}</p>
              </div>
              <div className="text-right">
                <p className="text-primary font-semibold">
                  {mealSuggestion.timeMinutes} min
                </p>
                <p className="text-xs text-muted">
                  {mealSuggestion.nutritionNote}
                </p>
              </div>
            </div>

            {/* Ingredients */}
            <div className="mb-6">
              <h3 className="font-semibold mb-2">Ingredients</h3>
              <ul className="space-y-1">
                {mealSuggestion.ingredients.map((ingredient, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm">
                    <span className="w-2 h-2 bg-primary rounded-full flex-shrink-0" />
                    <span>{ingredient}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Steps */}
            <div className="mb-6">
              <h3 className="font-semibold mb-2">Steps</h3>
              <ol className="space-y-2">
                {mealSuggestion.steps.map((step, i) => (
                  <li key={i} className="flex gap-3 text-sm">
                    <span className="flex-shrink-0 w-6 h-6 bg-primary rounded-full flex items-center justify-center text-xs font-semibold text-white">
                      {i + 1}
                    </span>
                    <span className="pt-0.5">{step}</span>
                  </li>
                ))}
              </ol>
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              {mealRecorded ? (
                <div className="flex-1 py-3 bg-secondary/20 text-secondary text-center rounded-lg font-semibold">
                  Meal recorded!
                </div>
              ) : (
                <button
                  onClick={markAsEaten}
                  className="flex-1 py-3 bg-primary hover:bg-primary-hover text-white font-semibold rounded-lg transition-colors"
                >
                  I ate this
                </button>
              )}
              <button
                onClick={generateMeal}
                disabled={loading}
                className="flex-1 py-3 bg-surface hover:bg-surface-hover border border-border rounded-lg text-sm transition-colors"
              >
                Different suggestion
              </button>
            </div>
          </div>
        )}

        {/* Quick Snacks */}
        <div className="p-4 bg-surface/50 border border-border rounded-lg">
          <h3 className="font-semibold mb-3">
            Can&apos;t cook? Zero-prep snacks:
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {[
              "Apple",
              "Handful of nuts",
              "String cheese",
              "Protein bar",
              "Banana",
              "Crackers + hummus",
            ].map((snack) => (
              <button
                key={snack}
                onClick={() => {
                  recordMeal();
                  setMealRecorded(true);
                }}
                className="p-2 bg-surface border border-border rounded text-center text-sm hover:border-primary transition-colors"
              >
                {snack}
              </button>
            ))}
          </div>
          <p className="text-xs text-muted mt-2">
            Tap any snack to record it as eaten
          </p>
        </div>
      </main>

      {/* Health Monitor */}
      <HealthMonitor />

      {/* Mr.DP */}
      <MrDPChat
        context={{
          currentMood: selectedMood || undefined,
          recentActivity: "planning food",
        }}
      />
    </div>
  );
}
