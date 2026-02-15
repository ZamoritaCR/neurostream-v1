import { NextRequest, NextResponse } from "next/server";
import { generateMealForState } from "@/lib/ai/food-agent";

// POST /api/food — Generate meal suggestion based on presence state
// Research: Brain 1, Section 3 — Hyperfocus causes skipped meals
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { presenceState, timeSinceMeal, mood, dietaryRestrictions } = body;

    const meal = await generateMealForState({
      presenceState: presenceState || "online",
      timeSinceMeal: timeSinceMeal || 0,
      mood,
      dietaryRestrictions,
    });

    return NextResponse.json({ meal });
  } catch (error) {
    console.error("Food API error:", error);
    return NextResponse.json(
      { error: "Failed to generate meal suggestion" },
      { status: 500 }
    );
  }
}
