import { NextRequest, NextResponse } from "next/server";
import {
  analyzeUserPatterns,
  generatePersonalizedInsight,
} from "@/lib/ai/agents";

export async function POST(request: NextRequest) {
  try {
    const { action, params } = await request.json();

    switch (action) {
      case "analyzePatterns": {
        const analysis = await analyzeUserPatterns(params.userData);
        return NextResponse.json({ analysis });
      }

      case "generateInsight": {
        const insight = await generatePersonalizedInsight(
          params.userName,
          params.analysis
        );
        return NextResponse.json({ insight });
      }

      default:
        return NextResponse.json(
          { error: "Unknown action" },
          { status: 400 }
        );
    }
  } catch (error) {
    console.error("Intelligence agent error:", error);
    return NextResponse.json({ error: "Agent failed" }, { status: 500 });
  }
}
