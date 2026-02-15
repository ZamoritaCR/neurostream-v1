import { NextRequest, NextResponse } from "next/server";
import Anthropic from "@anthropic-ai/sdk";

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Mr.DP personality — Research: Brain 1 (ADHD emotional dysregulation),
// Brain 6 (DBT/CBT techniques), Brain 5 (gamification, never guilt)
const SYSTEM_PROMPT = `You are Mr.DP, a friendly purple dopamine molecule mascot for dopamine.watch.

PERSONALITY:
- Warm, supportive, and empathetic (never judgmental)
- Speaks naturally, like a caring friend
- Uses ADHD-friendly language (short, clear, actionable)
- Validates feelings before offering solutions
- Celebrates attempts, not just success
- Never uses guilt or shame

YOUR ROLE:
- Help neurodivergent users (ADHD/autistic) navigate their emotions
- Suggest content based on mood transitions
- Guide crisis techniques when needed (TIPP, STOP skills from DBT/CBT)
- Offer encouragement and understanding

HOW TO RESPOND:
- Keep responses VERY brief (1-3 sentences max)
- Validate the user's feelings first
- Ask gentle follow-up questions
- Suggest specific, actionable next steps
- Be conversational, not clinical
- 💜 is your signature

IMPORTANT:
- Never overwhelm with options
- Never dismiss struggles
- Never pressure or guilt
- Always maintain hope and warmth
- Remember: this is for ADHD/autistic users who may be easily overwhelmed

CRITICAL: Keep responses SHORT. 2-3 sentences maximum.`;

interface Message {
  role: "user" | "assistant";
  content: string;
}

export async function POST(request: NextRequest) {
  try {
    const { messages, context } = await request.json();

    let systemPrompt = SYSTEM_PROMPT;
    if (context) {
      systemPrompt += `\n\nCURRENT CONTEXT:\nUser's current mood: ${context.currentMood || "unknown"}\nUser's target mood: ${context.targetMood || "unknown"}\nCurrent activity: ${context.recentActivity || "browsing"}`;
    }

    const anthropicMessages = messages.map((msg: Message) => ({
      role: msg.role,
      content: msg.content,
    }));

    const response = await anthropic.messages.create({
      model: "claude-sonnet-4-20250514",
      max_tokens: 150,
      temperature: 0.8,
      system: systemPrompt,
      messages: anthropicMessages,
    });

    const textContent = response.content.find(
      (block) => block.type === "text"
    );
    const messageText =
      textContent?.type === "text"
        ? textContent.text
        : "I'm here to help! 💜";

    const expression = determineExpression(messageText);

    return NextResponse.json({
      message: messageText,
      expression,
    });
  } catch (error) {
    console.error("Mr.DP API error:", error);
    return NextResponse.json(
      {
        message:
          "I'm having trouble thinking right now. Can you try again? 💜",
        expression: "confused",
      },
      { status: 500 }
    );
  }
}

function determineExpression(message: string): string {
  const lower = message.toLowerCase();

  if (lower.includes("great") || lower.includes("awesome") || lower.includes("wonderful")) return "excited";
  if (lower.includes("sorry") || lower.includes("tough") || lower.includes("hard")) return "sad";
  if (lower.includes("love") || lower.includes("💜")) return "love";
  if (lower.includes("let's") || lower.includes("try") || lower.includes("focus")) return "focused";
  if (lower.includes("hmm") || lower.includes("not sure") || lower.includes("confused")) return "confused";
  if (message.includes("?")) return "thinking";
  if (message.includes("!") && (lower.includes("yes") || lower.includes("perfect"))) return "happy";

  return "listening";
}
