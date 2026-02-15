"use client";

import { useEffect, useState } from "react";
import { usePresenceStore } from "@/stores/presence-store";
import Link from "next/link";

// Research: Brain 1, Section 3 — ADHD hyperfocus causes skipped meals/water
// Research: Brain 5, Section 4 — Celebrate attempts, never shame breaks
// Research: Brain 4, Section 10 — Non-guilt notifications, user-controlled

export function HealthMonitor() {
  const {
    currentState,
    shouldShowFoodReminder,
    shouldShowWaterReminder,
    shouldShowBreakReminder,
    recordWater,
    recordBreak,
  } = usePresenceStore();

  const [showWaterReminder, setShowWaterReminder] = useState(false);
  const [showFoodReminder, setShowFoodReminder] = useState(false);
  const [showBreakReminder, setShowBreakReminder] = useState(false);

  useEffect(() => {
    const check = () => {
      setShowWaterReminder(shouldShowWaterReminder());
      setShowFoodReminder(shouldShowFoodReminder());
      setShowBreakReminder(shouldShowBreakReminder());
    };

    check();
    const interval = setInterval(check, 60 * 1000);
    return () => clearInterval(interval);
  }, [shouldShowWaterReminder, shouldShowFoodReminder, shouldShowBreakReminder]);

  // Don't show in low bandwidth mode — respect user's energy
  if (currentState === "low_bandwidth") return null;
  if (!showWaterReminder && !showFoodReminder && !showBreakReminder)
    return null;

  return (
    <div className="fixed top-20 right-6 w-80 space-y-2 z-40">
      {/* Water Reminder */}
      {showWaterReminder && (
        <div className="bg-surface border-l-4 border-blue-500 rounded-r-lg p-4 shadow-lg">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                <p className="font-semibold text-sm">Hydration Check</p>
              </div>
              <p className="text-sm text-muted">
                {currentState === "hyperfocus"
                  ? "You've been focused for a while. Time for water."
                  : "Hydration reminder"}
              </p>
            </div>
            <button
              onClick={() => {
                recordWater();
                setShowWaterReminder(false);
              }}
              className="ml-3 px-3 py-1.5 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 rounded text-xs font-medium transition-colors"
            >
              Done
            </button>
          </div>
        </div>
      )}

      {/* Food Reminder */}
      {showFoodReminder && (
        <div className="bg-surface border-l-4 border-orange-500 rounded-r-lg p-4 shadow-lg">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse" />
                <p className="font-semibold text-sm">Nutrition Alert</p>
              </div>
              <p className="text-sm text-muted">
                {currentState === "hyperfocus"
                  ? "It's been a while. Let's get you some food."
                  : "Time for a meal"}
              </p>
            </div>
            <Link
              href="/food"
              className="ml-3 px-3 py-1.5 bg-orange-500/10 hover:bg-orange-500/20 text-orange-400 rounded text-xs font-medium transition-colors"
            >
              Plan Meal
            </Link>
          </div>
        </div>
      )}

      {/* Break Reminder (hyperfocus only) */}
      {showBreakReminder && currentState === "hyperfocus" && (
        <div className="bg-surface border-l-4 border-purple-500 rounded-r-lg p-4 shadow-lg">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" />
                <p className="font-semibold text-sm">Break Recommended</p>
              </div>
              <p className="text-sm text-muted">
                90+ minutes of focus. Consider a 5-minute break.
              </p>
            </div>
            <button
              onClick={() => {
                recordBreak();
                setShowBreakReminder(false);
              }}
              className="ml-3 px-3 py-1.5 bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 rounded text-xs font-medium transition-colors"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
