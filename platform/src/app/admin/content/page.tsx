"use client";

import { useState } from "react";

export default function ContentAgentPage() {
  const [topic, setTopic] = useState("");
  const [keywords, setKeywords] = useState("");
  const [tone, setTone] = useState("empathetic");
  const [length, setLength] = useState<"short" | "medium" | "long">("medium");
  const [generatedContent, setGeneratedContent] = useState("");
  const [seoData, setSeoData] = useState<{
    title?: string;
    metaDescription?: string;
    keywords?: string[];
    headingImprovements?: string[];
    internalLinks?: string[];
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"generate" | "seo">("generate");

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    setLoading(true);
    setSeoData(null);

    try {
      const res = await fetch("/api/admin/agents/content", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "generateBlog",
          params: {
            topic,
            keywords: keywords
              .split(",")
              .map((k) => k.trim())
              .filter(Boolean),
            tone,
            length,
          },
        }),
      });
      const data = await res.json();
      setGeneratedContent(data.content || "No content generated");
    } catch (error) {
      console.error("Generation error:", error);
      setGeneratedContent("Error generating content. Check console.");
    } finally {
      setLoading(false);
    }
  };

  const handleSEO = async () => {
    if (!generatedContent) return;
    setLoading(true);

    try {
      const res = await fetch("/api/admin/agents/content", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "optimizeSEO",
          params: { content: generatedContent },
        }),
      });
      const data = await res.json();
      setSeoData(data);
    } catch (error) {
      console.error("SEO error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Content Creator Agent</h1>
        <p className="text-muted">
          Generate blog posts and optimize for SEO
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {(["generate", "seo"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === tab
                ? "bg-primary text-white"
                : "bg-surface-hover text-muted hover:text-foreground"
            }`}
          >
            {tab === "generate" ? "Generate Blog Post" : "SEO Optimization"}
          </button>
        ))}
      </div>

      {activeTab === "generate" && (
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Input Panel */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Topic</label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., Why ADHD users need privacy-first platforms"
                className="w-full px-4 py-3 bg-surface border border-border rounded-lg text-sm focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Keywords (comma-separated)
              </label>
              <input
                type="text"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="e.g., ADHD, privacy, neurodivergent, dopamine"
                className="w-full px-4 py-3 bg-surface border border-border rounded-lg text-sm focus:outline-none focus:border-primary"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Tone</label>
                <select
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                  className="w-full px-4 py-3 bg-surface border border-border rounded-lg text-sm focus:outline-none focus:border-primary"
                >
                  <option value="empathetic">Empathetic</option>
                  <option value="informative">Informative</option>
                  <option value="casual">Casual</option>
                  <option value="professional">Professional</option>
                  <option value="passionate">Passionate</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Length
                </label>
                <select
                  value={length}
                  onChange={(e) =>
                    setLength(e.target.value as "short" | "medium" | "long")
                  }
                  className="w-full px-4 py-3 bg-surface border border-border rounded-lg text-sm focus:outline-none focus:border-primary"
                >
                  <option value="short">Short (500-700 words)</option>
                  <option value="medium">Medium (1000-1500 words)</option>
                  <option value="long">Long (2000-3000 words)</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleGenerate}
              disabled={loading || !topic.trim()}
              className="w-full py-3 bg-primary hover:bg-primary-hover text-white rounded-lg font-semibold disabled:opacity-50 transition-colors"
            >
              {loading ? "Generating..." : "Generate Blog Post"}
            </button>
          </div>

          {/* Output Panel */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium">
                Generated Content
              </label>
              {generatedContent && (
                <button
                  onClick={() => navigator.clipboard.writeText(generatedContent)}
                  className="text-xs text-primary hover:text-primary-hover"
                >
                  Copy to Clipboard
                </button>
              )}
            </div>
            <div className="h-[500px] overflow-y-auto p-4 bg-surface border border-border rounded-lg">
              {generatedContent ? (
                <pre className="whitespace-pre-wrap text-sm text-foreground/90 leading-relaxed font-sans">
                  {generatedContent}
                </pre>
              ) : (
                <p className="text-muted text-sm">
                  Generated content will appear here...
                </p>
              )}
            </div>

            {generatedContent && (
              <button
                onClick={handleSEO}
                disabled={loading}
                className="mt-4 w-full py-2 bg-surface-hover hover:bg-border text-foreground rounded-lg text-sm font-medium transition-colors"
              >
                {loading ? "Analyzing..." : "Run SEO Analysis"}
              </button>
            )}
          </div>
        </div>
      )}

      {activeTab === "seo" && (
        <div className="max-w-2xl">
          {seoData ? (
            <div className="space-y-6">
              {seoData.title && (
                <div className="p-4 bg-surface border border-border rounded-lg">
                  <h3 className="text-sm font-medium text-muted mb-1">
                    Recommended Title
                  </h3>
                  <p className="font-semibold">{seoData.title}</p>
                </div>
              )}

              {seoData.metaDescription && (
                <div className="p-4 bg-surface border border-border rounded-lg">
                  <h3 className="text-sm font-medium text-muted mb-1">
                    Meta Description
                  </h3>
                  <p className="text-sm">{seoData.metaDescription}</p>
                </div>
              )}

              {Array.isArray(seoData.keywords) && (
                <div className="p-4 bg-surface border border-border rounded-lg">
                  <h3 className="text-sm font-medium text-muted mb-2">
                    Keywords
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {seoData.keywords.map((kw) => (
                      <span
                        key={kw}
                        className="px-3 py-1 bg-primary/20 text-primary rounded-full text-xs"
                      >
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {Array.isArray(seoData.headingImprovements) && (
                <div className="p-4 bg-surface border border-border rounded-lg">
                  <h3 className="text-sm font-medium text-muted mb-2">
                    Heading Improvements
                  </h3>
                  <ul className="space-y-1">
                    {seoData.headingImprovements.map(
                      (h, i) => (
                        <li key={i} className="text-sm">
                          {h}
                        </li>
                      )
                    )}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="p-8 bg-surface border border-border rounded-lg text-center">
              <p className="text-muted">
                Generate a blog post first, then run SEO analysis
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
