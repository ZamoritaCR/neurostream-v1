"use client";

import Link from "next/link";

const agents = [
  {
    name: "Content Creator",
    description: "Generate blog posts, optimize SEO, create social content",
    href: "/admin/content",
    icon: "C",
    status: "active",
    actions: ["Generate Blog Post", "SEO Analysis"],
  },
  {
    name: "User Intelligence",
    description: "Analyze user patterns, generate personalized insights",
    href: "/admin/intelligence",
    icon: "I",
    status: "active",
    actions: ["Analyze Patterns", "Generate Insight"],
  },
  {
    name: "Engagement Engine",
    description:
      "Create re-engagement emails, celebrate streaks (never guilt)",
    href: "/admin/engagement",
    icon: "E",
    status: "active",
    actions: ["Draft Email", "Celebrate Streak"],
  },
  {
    name: "Search & Discovery",
    description: "Semantic search, similar content, ADHD-friendly summaries",
    href: "#",
    icon: "S",
    status: "coming-soon",
    actions: ["Semantic Search", "Find Similar"],
  },
  {
    name: "Meal Planner",
    description: "Mood-based recipes, ingredient substitutions",
    href: "#",
    icon: "M",
    status: "coming-soon",
    actions: ["Meal by Mood", "Substitutions"],
  },
];

export default function AdminDashboard() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">
          <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Agent Command Center
          </span>
        </h1>
        <p className="text-muted">
          Your AI-powered operating system for dopamine.watch
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        {[
          { label: "Active Agents", value: "3" },
          { label: "Coming Soon", value: "2" },
          { label: "API Routes", value: "5" },
          { label: "AI Functions", value: "12" },
        ].map((stat) => (
          <div
            key={stat.label}
            className="p-4 bg-surface border border-border rounded-lg text-center"
          >
            <p className="text-2xl font-bold text-primary">{stat.value}</p>
            <p className="text-xs text-muted mt-1">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Agent Cards */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent) => (
          <div
            key={agent.name}
            className={`p-6 bg-surface border rounded-lg transition-colors ${
              agent.status === "active"
                ? "border-border hover:border-primary"
                : "border-border opacity-60"
            }`}
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center text-white font-bold text-lg">
                {agent.icon}
              </div>
              <div>
                <h3 className="font-bold">{agent.name}</h3>
                <span
                  className={`text-xs px-2 py-0.5 rounded-full ${
                    agent.status === "active"
                      ? "bg-secondary/20 text-secondary"
                      : "bg-muted/20 text-muted"
                  }`}
                >
                  {agent.status === "active" ? "Active" : "Coming Soon"}
                </span>
              </div>
            </div>

            <p className="text-sm text-muted mb-4">{agent.description}</p>

            <div className="flex flex-wrap gap-2 mb-4">
              {agent.actions.map((action) => (
                <span
                  key={action}
                  className="text-xs px-2 py-1 bg-surface-hover rounded text-muted"
                >
                  {action}
                </span>
              ))}
            </div>

            {agent.status === "active" ? (
              <Link
                href={agent.href}
                className="block text-center py-2 px-4 bg-primary hover:bg-primary-hover text-white rounded-lg text-sm font-semibold transition-colors"
              >
                Open Agent
              </Link>
            ) : (
              <div className="text-center py-2 px-4 bg-surface-hover text-muted rounded-lg text-sm">
                In Development
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
