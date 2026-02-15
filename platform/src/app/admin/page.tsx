"use client";

import Link from "next/link";

const agents = [
  {
    name: "Content Creator",
    description: "Generate blog posts, optimize SEO, create social content",
    href: "/admin/content",
    gradient: "from-blue-500 to-blue-600",
    status: "active" as const,
    actions: ["Generate Blog Post", "SEO Analysis"],
    icon: (
      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
      </svg>
    ),
  },
  {
    name: "User Intelligence",
    description: "Analyze user patterns, generate personalized insights",
    href: "/admin/intelligence",
    gradient: "from-purple-500 to-purple-600",
    status: "active" as const,
    actions: ["Analyze Patterns", "Generate Insight"],
    icon: (
      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
  },
  {
    name: "Engagement Engine",
    description:
      "Create re-engagement emails, celebrate streaks (never guilt)",
    href: "/admin/engagement",
    gradient: "from-green-500 to-green-600",
    status: "active" as const,
    actions: ["Draft Email", "Celebrate Streak"],
    icon: (
      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
  },
  {
    name: "Search & Discovery",
    description: "Semantic search, similar content, ADHD-friendly summaries",
    href: "#",
    gradient: "from-orange-500 to-orange-600",
    status: "coming-soon" as const,
    actions: ["Semantic Search", "Find Similar"],
    icon: (
      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    ),
  },
  {
    name: "Meal Planner",
    description: "Mood-based recipes, ingredient substitutions",
    href: "#",
    gradient: "from-amber-500 to-amber-600",
    status: "coming-soon" as const,
    actions: ["Meal by Mood", "Substitutions"],
    icon: (
      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
    ),
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
          { label: "API Routes", value: "6" },
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
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
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
              <div className={`w-12 h-12 bg-gradient-to-br ${agent.gradient} rounded-lg flex items-center justify-center`}>
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

      {/* Quick Actions */}
      <div className="bg-surface border border-border rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <Link
            href="/admin/claude"
            className="p-4 bg-background border border-border rounded-lg hover:border-primary transition-colors flex items-center gap-3"
          >
            <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
              <div className="w-3 h-3 bg-primary rounded-full animate-pulse" />
            </div>
            <div>
              <p className="font-semibold">Talk to Claude</p>
              <p className="text-xs text-muted">Admin command interface</p>
            </div>
          </Link>

          <button
            className="p-4 bg-background border border-border rounded-lg hover:border-primary transition-colors flex items-center gap-3 text-left"
            onClick={() => alert("Coming soon: User database browser")}
          >
            <div className="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <div>
              <p className="font-semibold">Browse Users</p>
              <p className="text-xs text-muted">View all registered users</p>
            </div>
          </button>

          <button
            className="p-4 bg-background border border-border rounded-lg hover:border-primary transition-colors flex items-center gap-3 text-left"
            onClick={() => alert("Coming soon: Analytics dashboard")}
          >
            <div className="w-10 h-10 bg-green-500/10 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <p className="font-semibold">Analytics</p>
              <p className="text-xs text-muted">Platform metrics & insights</p>
            </div>
          </button>

          <button
            className="p-4 bg-background border border-border rounded-lg hover:border-primary transition-colors flex items-center gap-3 text-left"
            onClick={() => alert("Coming soon: System logs")}
          >
            <div className="w-10 h-10 bg-orange-500/10 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <p className="font-semibold">System Logs</p>
              <p className="text-xs text-muted">Error tracking & monitoring</p>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}
