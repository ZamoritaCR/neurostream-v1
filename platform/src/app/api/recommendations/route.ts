import { NextRequest, NextResponse } from "next/server";
import OpenAI from "openai";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(request: NextRequest) {
  try {
    const { currentMood, targetMood, preferences = [], context = "" } =
      await request.json();

    if (!currentMood || !targetMood) {
      return NextResponse.json(
        { error: "currentMood and targetMood are required" },
        { status: 400 }
      );
    }

    const prompt = `You are a content recommendation expert for neurodivergent minds (ADHD/autism).

Current emotional state: ${currentMood}
Desired emotional state: ${targetMood}
User preferences: ${preferences.join(", ") || "None specified"}
Additional context: ${context || "None"}

Based on this emotional bridge (${currentMood} → ${targetMood}), suggest 5 specific movie or TV show titles that would help this emotional transition.

Rules:
- Focus on well-known, accessible content
- Consider the emotional journey needed
- Be specific with titles (not genres)
- Brief explanation why each helps the transition

Respond with ONLY a JSON array of objects:
[
  {
    "title": "Movie/Show Title",
    "reason": "Brief explanation why this helps the emotional transition"
  }
]`;

    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system",
          content:
            "You are a compassionate content recommendation assistant for neurodivergent users. Respond only with valid JSON.",
        },
        { role: "user", content: prompt },
      ],
      temperature: 0.7,
      max_tokens: 500,
    });

    const content = completion.choices[0]?.message?.content || "[]";
    const recommendations = JSON.parse(content);

    return NextResponse.json({ recommendations });
  } catch (error) {
    console.error("AI recommendation error:", error);
    // Fallback recommendations
    return NextResponse.json({
      recommendations: [
        {
          title: "The Grand Budapest Hotel",
          reason: "Whimsical visuals and gentle humor",
        },
        {
          title: "Parks and Recreation",
          reason: "Uplifting ensemble comedy",
        },
        { title: "My Neighbor Totoro", reason: "Calming and heartwarming" },
        { title: "The Good Place", reason: "Light philosophical comedy" },
        { title: "Chef's Table", reason: "Beautiful and meditative" },
      ],
    });
  }
}
