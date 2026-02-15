import { NextRequest, NextResponse } from "next/server";
import Anthropic from "@anthropic-ai/sdk";
import {
  generateBlogPost,
  analyzeUserPatterns,
  generateReEngagementEmail,
} from "@/lib/ai/agents";

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

const SYSTEM_PROMPT = `You are Claude, the admin interface for the dopamine.watch platform.

You can control the entire platform through OpenAI-powered agents. When the admin asks you to do something, you:
1. Understand their intent
2. Call the appropriate agent(s)
3. Return results in a clear, professional manner

AVAILABLE AGENTS:

**Content Creator Agent (OpenAI):**
- generateBlogPost(topic, keywords, tone, length)
- optimizeSEO(content)

**User Intelligence Agent (OpenAI):**
- analyzeUserPatterns(watchHistory, moodSelections, timeOfDay)
- generatePersonalizedInsight(userName, analysis)

**Engagement Engine Agent (OpenAI):**
- generateReEngagementEmail(userName, lastActive, preferences)
- generateStreakCelebration(userName, streakDays)

HOW TO RESPOND:
1. If admin asks for content generation → Confirm the content agent ran
2. If admin asks about users → Confirm the intelligence agent ran
3. If admin asks about engagement → Confirm the engagement agent ran
4. If admin asks general questions → Answer directly
5. Always be professional and concise
6. Show results clearly and suggest next steps

You are NOT just a chatbot - you are the CONTROL INTERFACE for the platform.
If agent results are provided, summarize them and ask if there's anything else.`;

interface Message {
  role: "user" | "assistant";
  content: string;
}

export async function POST(request: NextRequest) {
  try {
    const { messages } = await request.json();

    const lastUserMessage =
      messages[messages.length - 1]?.content.toLowerCase() || "";
    const originalMessage = messages[messages.length - 1]?.content || "";
    const executions: {
      agent: string;
      action: string;
      status: "running" | "success" | "error";
      error?: string;
    }[] = [];

    // Intent detection
    const wantsBlog =
      lastUserMessage.includes("blog") ||
      lastUserMessage.includes("post") ||
      lastUserMessage.includes("write") ||
      lastUserMessage.includes("article");
    const wantsAnalysis =
      lastUserMessage.includes("analyze") ||
      lastUserMessage.includes("pattern") ||
      lastUserMessage.includes("insight");
    const wantsEmail =
      lastUserMessage.includes("email") ||
      lastUserMessage.includes("engage") ||
      lastUserMessage.includes("inactive") ||
      lastUserMessage.includes("re-engage");

    let agentResults = "";

    // Execute content agent
    if (wantsBlog) {
      executions.push({
        agent: "content",
        action: "Generating blog post",
        status: "running",
      });

      try {
        // Extract topic from the message (remove common prefixes)
        const topic = originalMessage
          .replace(
            /^(generate|write|create|draft)\s+(a\s+)?(blog\s+)?(post\s+)?(about\s+)?/i,
            ""
          )
          .trim() || "ADHD productivity tips";

        const result = await generateBlogPost({
          topic,
          keywords: ["ADHD", "neurodivergent", "dopamine"],
          tone: "empathetic",
          length: "medium",
        });

        const preview =
          typeof result === "string"
            ? result.substring(0, 800)
            : JSON.stringify(result).substring(0, 800);

        agentResults += `\n\n**Content Agent Result:**\n${preview}...`;
        executions[executions.length - 1].status = "success";
      } catch (error: unknown) {
        const msg =
          error instanceof Error ? error.message : "Unknown error";
        executions[executions.length - 1].status = "error";
        executions[executions.length - 1].error = msg;
        agentResults += "\n\nContent agent encountered an error.";
      }
    }

    // Execute intelligence agent
    if (wantsAnalysis) {
      executions.push({
        agent: "intelligence",
        action: "Analyzing user patterns",
        status: "running",
      });

      try {
        const result = await analyzeUserPatterns({
          watchHistory: [
            { title: "Sample Movie", mood: "calm", date: "2026-02-14" },
          ],
          moodSelections: [
            { current: "anxious", target: "calm", date: "2026-02-14" },
          ],
          timeOfDay: ["evening", "night"],
        });

        agentResults += `\n\n**Intelligence Agent Result:**\n${JSON.stringify(result, null, 2)}`;
        executions[executions.length - 1].status = "success";
      } catch (error: unknown) {
        const msg =
          error instanceof Error ? error.message : "Unknown error";
        executions[executions.length - 1].status = "error";
        executions[executions.length - 1].error = msg;
        agentResults += "\n\nIntelligence agent encountered an error.";
      }
    }

    // Execute engagement agent
    if (wantsEmail) {
      executions.push({
        agent: "engagement",
        action: "Generating re-engagement email",
        status: "running",
      });

      try {
        const result = await generateReEngagementEmail(
          "User",
          "3 days ago",
          { preferredContent: "movies", mood: "calm" }
        );

        agentResults += `\n\n**Engagement Agent Result:**\n${JSON.stringify(result, null, 2)}`;
        executions[executions.length - 1].status = "success";
      } catch (error: unknown) {
        const msg =
          error instanceof Error ? error.message : "Unknown error";
        executions[executions.length - 1].status = "error";
        executions[executions.length - 1].error = msg;
        agentResults += "\n\nEngagement agent encountered an error.";
      }
    }

    // Build messages for Claude
    const anthropicMessages = messages.map((msg: Message) => ({
      role: msg.role as "user" | "assistant",
      content: msg.content,
    }));

    // Append agent results if any
    if (agentResults) {
      anthropicMessages.push({
        role: "user" as const,
        content: `Agent execution results:${agentResults}\n\nPlease summarize what was done and ask if there's anything else I need.`,
      });
    }

    const response = await anthropic.messages.create({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1000,
      system: SYSTEM_PROMPT,
      messages: anthropicMessages,
    });

    const textContent = response.content.find(
      (block) => block.type === "text"
    );
    const responseText =
      textContent?.type === "text" ? textContent.text : "I'm here to help!";

    return NextResponse.json({
      response: responseText,
      executions,
    });
  } catch (error) {
    console.error("Claude admin error:", error);
    return NextResponse.json(
      {
        response: "I encountered an error. Please try again.",
        executions: [],
      },
      { status: 500 }
    );
  }
}
