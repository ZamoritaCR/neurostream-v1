import OpenAI from "openai";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// ═══════════════════════════════════════════════════════════════
// AGENT 1: CONTENT CREATOR
// Research: Brain 4 (ADHD-friendly content), Brain 1 (neurodivergent language)
// ═══════════════════════════════════════════════════════════════

export async function generateBlogPost(params: {
  topic: string;
  keywords?: string[];
  tone?: string;
  length?: "short" | "medium" | "long";
}) {
  const {
    topic,
    keywords = [],
    tone = "empathetic",
    length = "medium",
  } = params;

  const wordCount = {
    short: "500-700",
    medium: "1000-1500",
    long: "2000-3000",
  }[length];

  const prompt = `You are a content creator for dopamine.watch, a platform for neurodivergent users.

Write a blog post about: ${topic}

Requirements:
- Tone: ${tone}, supportive, ADHD-friendly
- Length: ${wordCount} words
- Keywords to include: ${keywords.join(", ") || "none specified"}
- Use short paragraphs (2-3 sentences max)
- Include specific examples
- End with actionable takeaway
- Write in markdown format

Structure:
# [Catchy Title]

[Compelling intro - 1-2 paragraphs]

## [Section 1]
[Content]

## [Section 2]
[Content]

## Key Takeaways
- Takeaway 1
- Takeaway 2

Focus on how this helps neurodivergent users specifically.`;

  const completion = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: prompt }],
    temperature: 0.8,
    max_tokens: 2000,
  });

  return completion.choices[0]?.message?.content || "";
}

export async function optimizeSEO(content: string) {
  const prompt = `Analyze this blog post and provide SEO optimizations:

${content}

Provide:
1. Recommended title (60 chars max)
2. Meta description (155 chars max)
3. 5-7 relevant keywords
4. Suggested headings improvements
5. Internal linking opportunities

Format as JSON:
{
  "title": "...",
  "metaDescription": "...",
  "keywords": ["...", "..."],
  "headingImprovements": ["...", "..."],
  "internalLinks": ["...", "..."]
}`;

  const completion = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: prompt }],
    temperature: 0.3,
    max_tokens: 500,
    response_format: { type: "json_object" },
  });

  return JSON.parse(completion.choices[0]?.message?.content || "{}");
}

// ═══════════════════════════════════════════════════════════════
// AGENT 2: SEARCH & DISCOVERY
// Research: Brain 2 (emotional mapping), Brain 8 (technical implementation)
// ═══════════════════════════════════════════════════════════════

export async function semanticSearch(query: string) {
  const embeddings = await openai.embeddings.create({
    model: "text-embedding-3-small",
    input: query,
  });

  // In production, use a vector database (Pinecone, Supabase pgvector)
  // For now, return the embedding for future integration
  return {
    query,
    embedding: embeddings.data[0].embedding,
    dimensions: embeddings.data[0].embedding.length,
    note: "Implement vector DB integration for semantic search",
  };
}

export async function findSimilarContent(description: string) {
  const prompt = `Based on this content: "${description}"

Suggest 5 similar pieces of content that would appeal to the same user.
Consider:
- Emotional tone
- Pacing
- Complexity
- Themes

Respond with JSON:
{
  "suggestions": [
    {
      "title": "Suggested content title",
      "reason": "Why this matches",
      "mood": "What mood it serves"
    }
  ]
}`;

  const completion = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: prompt }],
    temperature: 0.7,
    response_format: { type: "json_object" },
  });

  return JSON.parse(
    completion.choices[0]?.message?.content || '{"suggestions":[]}'
  );
}

export async function generateContentSummary(
  title: string,
  fullDescription: string
) {
  const prompt = `Create an ADHD-friendly summary of this show/movie:

Title: ${title}
Description: ${fullDescription}

Provide:
1. One-sentence hook (what makes it special)
2. 3-bullet "What to expect" summary
3. Pacing note (slow-burn, fast-paced, etc.)
4. Mood it creates

Keep it scannable and brief.`;

  const completion = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: prompt }],
    temperature: 0.7,
    max_tokens: 300,
  });

  return completion.choices[0]?.message?.content || "";
}

// ═══════════════════════════════════════════════════════════════
// AGENT 3: USER INTELLIGENCE
// Research: Brain 1 (ADHD patterns), Brain 5 (engagement without exploitation)
// ═══════════════════════════════════════════════════════════════

interface UserData {
  watchHistory: { title: string; mood: string; date: string }[];
  moodSelections: { current: string; target: string; date: string }[];
  timeOfDay: string[];
}

export async function analyzeUserPatterns(userData: UserData) {
  const prompt = `Analyze this user's behavior pattern:

Watch History: ${JSON.stringify(userData.watchHistory)}
Mood Selections: ${JSON.stringify(userData.moodSelections)}
Active Times: ${userData.timeOfDay.join(", ")}

Identify:
1. Most common emotional transitions
2. Content preferences
3. Time-of-day patterns
4. Potential triggers for anxiety/stress
5. Recommended content types

Respond as JSON:
{
  "emotionalPatterns": ["pattern1", "pattern2"],
  "preferences": ["pref1", "pref2"],
  "bestTimes": ["time1", "time2"],
  "triggers": ["trigger1"],
  "recommendations": ["rec1", "rec2"]
}`;

  const completion = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: prompt }],
    temperature: 0.5,
    response_format: { type: "json_object" },
  });

  return JSON.parse(completion.choices[0]?.message?.content || "{}");
}

export async function generatePersonalizedInsight(
  userName: string,
  analysis: Record<string, unknown>
) {
  const prompt = `Based on this user analysis, write a warm, personalized insight:

User: ${userName}
Analysis: ${JSON.stringify(analysis)}

Write a 2-3 sentence message that:
- Acknowledges their pattern
- Celebrates what they're doing well
- Offers gentle suggestion

Tone: Warm, supportive, Mr.DP-style
Keep it brief and actionable.`;

  const completion = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: prompt }],
    temperature: 0.8,
    max_tokens: 150,
  });

  return completion.choices[0]?.message?.content || "";
}

// ═══════════════════════════════════════════════════════════════
// AGENT 4: ENGAGEMENT ENGINE
// Research: Brain 5 (gamification without guilt), Brain 4 (notification rules)
// ═══════════════════════════════════════════════════════════════

export async function generateReEngagementEmail(
  userName: string,
  lastActive: string,
  userPreferences: Record<string, unknown>
) {
  const prompt = `Create a re-engagement email for an inactive user:

User: ${userName}
Last Active: ${lastActive}
Preferences: ${JSON.stringify(userPreferences)}

Requirements:
- Subject line (50 chars max)
- Warm, not pushy (NEVER guilt-inducing)
- Mention something specific to their interests
- Include ONE clear call-to-action
- Sign as "The dopamine.watch team"

CRITICAL: No guilt language like "You've been missing out" or "We miss you"
Instead use: "Whenever you're ready" or "Something new you might enjoy"

Format as JSON:
{
  "subject": "...",
  "body": "..."
}`;

  const completion = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: prompt }],
    temperature: 0.8,
    response_format: { type: "json_object" },
  });

  return JSON.parse(completion.choices[0]?.message?.content || "{}");
}

export async function generateStreakCelebration(
  userName: string,
  streakDays: number
) {
  // Research: Brain 5, Section 4 - Celebrate attempts, never guilt on breaks
  const prompt = `Create a celebration message for a user's streak:

User: ${userName}
Streak: ${streakDays} days

Make it:
- Enthusiastic but not overwhelming
- Specific to the number (milestone language)
- Encouraging to continue
- 2-3 sentences max

Milestone guidelines:
- 3 days: "Getting started!"
- 7 days: "One week strong!"
- 30 days: "A whole month!"
- 100 days: "Triple digits!"

CRITICAL: Never imply that breaking the streak is failure.`;

  const completion = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: prompt }],
    temperature: 0.9,
    max_tokens: 100,
  });

  return completion.choices[0]?.message?.content || "";
}

// ═══════════════════════════════════════════════════════════════
// AGENT 5: MEAL PLANNER (Future - food.dopamine.watch)
// Research: Brain 1 (executive function challenges), Brain 4 (simple instructions)
// ═══════════════════════════════════════════════════════════════

export async function generateMealByMood(
  mood: string,
  dietaryRestrictions: string[] = []
) {
  const prompt = `Suggest a meal for someone feeling: ${mood}

Dietary restrictions: ${dietaryRestrictions.join(", ") || "None"}

Provide:
1. Meal name
2. Why it matches the mood
3. ADHD-friendly cooking steps (max 5 steps, very clear)
4. Time estimate
5. Key ingredients (max 8)

Keep instructions VERY simple - assume executive function challenges.

Respond as JSON:
{
  "name": "...",
  "reason": "...",
  "steps": ["step1", "step2"],
  "timeMinutes": 30,
  "ingredients": ["ing1", "ing2"]
}`;

  const completion = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: prompt }],
    temperature: 0.7,
    response_format: { type: "json_object" },
  });

  return JSON.parse(completion.choices[0]?.message?.content || "{}");
}

export async function suggestIngredientSubstitution(
  original: string,
  reason: string
) {
  const prompt = `Suggest substitute for: ${original}

Reason for substitution: ${reason}

Provide 3 alternatives with:
- Substitute ingredient
- How to use it
- Taste/texture difference

Keep it simple and practical.`;

  const completion = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: prompt }],
    temperature: 0.6,
    max_tokens: 200,
  });

  return completion.choices[0]?.message?.content || "";
}
