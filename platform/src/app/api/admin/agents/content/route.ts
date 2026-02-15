import { NextRequest, NextResponse } from "next/server";
import { generateBlogPost, optimizeSEO } from "@/lib/ai/agents";

export async function POST(request: NextRequest) {
  try {
    const { action, params } = await request.json();

    switch (action) {
      case "generateBlog": {
        const blogPost = await generateBlogPost(params);
        return NextResponse.json({ content: blogPost });
      }

      case "optimizeSEO": {
        const seoData = await optimizeSEO(params.content);
        return NextResponse.json(seoData);
      }

      default:
        return NextResponse.json(
          { error: "Unknown action" },
          { status: 400 }
        );
    }
  } catch (error) {
    console.error("Content agent error:", error);
    return NextResponse.json({ error: "Agent failed" }, { status: 500 });
  }
}
