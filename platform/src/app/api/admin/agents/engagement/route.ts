import { NextRequest, NextResponse } from "next/server";
import {
  generateReEngagementEmail,
  generateStreakCelebration,
} from "@/lib/ai/agents";

export async function POST(request: NextRequest) {
  try {
    const { action, params } = await request.json();

    switch (action) {
      case "generateEmail": {
        const email = await generateReEngagementEmail(
          params.userName,
          params.lastActive,
          params.userPreferences
        );
        return NextResponse.json({ email });
      }

      case "celebrateStreak": {
        const celebration = await generateStreakCelebration(
          params.userName,
          params.streakDays
        );
        return NextResponse.json({ celebration });
      }

      default:
        return NextResponse.json(
          { error: "Unknown action" },
          { status: 400 }
        );
    }
  } catch (error) {
    console.error("Engagement agent error:", error);
    return NextResponse.json({ error: "Agent failed" }, { status: 500 });
  }
}
