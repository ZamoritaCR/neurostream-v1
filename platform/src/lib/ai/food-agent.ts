import OpenAI from "openai";

// ═══════════════════════════════════════════════════════════════
// FOOD AGENT — ADHD-Friendly Meal Suggestions
// Research: Brain 1, Section 3 — Hyperfocus causes skipped meals
// Research: Brain 5, Section 4 — Celebrate attempts, never shame
// ═══════════════════════════════════════════════════════════════

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export interface MealSuggestion {
  name: string;
  timeMinutes: number;
  ingredients: string[];
  steps: string[];
  reason: string;
  nutritionNote: string;
}

export async function generateMealForState(params: {
  presenceState: string;
  timeSinceMeal: number;
  mood?: string;
  dietaryRestrictions?: string[];
}): Promise<MealSuggestion> {
  const {
    presenceState,
    timeSinceMeal,
    mood,
    dietaryRestrictions = [],
  } = params;

  const hoursWithoutFood = Math.floor(timeSinceMeal / (1000 * 60 * 60));
  const urgency =
    hoursWithoutFood >= 4
      ? "URGENT"
      : hoursWithoutFood >= 3
        ? "HIGH"
        : "MEDIUM";

  const prompt = `You are a nutrition assistant for neurodivergent users.

SITUATION:
- User state: ${presenceState}
- Time without food: ${hoursWithoutFood} hours
- Urgency: ${urgency}
- Current mood: ${mood || "neutral"}
- Dietary restrictions: ${dietaryRestrictions.join(", ") || "None"}

PRESENCE STATE GUIDE:
- hyperfocus: User is deep in work, won't want to break flow. ULTRA simple (2-3 min max)
- high_energy: Quick protein/energy boost
- low_bandwidth: Maximum comfort, minimal decisions, familiar foods
- task_mode: Efficient fuel, back to work fast

URGENCY GUIDE:
- URGENT (4+ hours): Push convenience over nutrition if needed
- HIGH (3+ hours): Balance speed with basic nutrition
- MEDIUM (<3 hours): Can suggest proper meal

REQUIREMENTS:
1. Time: ${presenceState === "hyperfocus" ? "2-5 minutes" : "5-15 minutes"} MAX
2. Steps: ${presenceState === "hyperfocus" ? "2-3" : "3-5"} steps maximum
3. Ingredients: ${presenceState === "hyperfocus" ? "2-4" : "5-8"} max
4. No cooking if hyperfocus and urgent
5. ADHD-friendly: Clear, numbered, no ambiguity

Respond ONLY with valid JSON:
{
  "name": "Meal name",
  "timeMinutes": 5,
  "ingredients": ["item1", "item2"],
  "steps": ["Step 1", "Step 2"],
  "reason": "Why this meal matches their state",
  "nutritionNote": "Quick nutrition benefit"
}`;

  try {
    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system",
          content:
            "You are a compassionate nutrition assistant for ADHD/autistic users. Prioritize simplicity and speed over perfection. Output only valid JSON.",
        },
        { role: "user", content: prompt },
      ],
      temperature: 0.7,
      max_tokens: 400,
      response_format: { type: "json_object" },
    });

    const result = JSON.parse(
      completion.choices[0]?.message?.content || "{}"
    );
    return result as MealSuggestion;
  } catch (error) {
    console.error("Food agent error:", error);

    // Fallback — always provide something
    return {
      name: "Quick PB&J",
      timeMinutes: 2,
      ingredients: ["Bread", "Peanut butter", "Jelly"],
      steps: [
        "Spread PB on one slice",
        "Spread jelly on other",
        "Combine and eat",
      ],
      reason: "Ultra-quick energy when you need it most",
      nutritionNote: "Protein + quick carbs for immediate fuel",
    };
  }
}
