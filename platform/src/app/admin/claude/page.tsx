"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: number;
}

interface AgentExecution {
  agent: string;
  action: string;
  status: "running" | "success" | "error";
  error?: string;
}

export default function ClaudeAdminPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello Johan. I'm your admin interface to the dopamine.watch platform. I can help you:\n\n- Generate blog posts and content\n- Analyze user patterns\n- Send engagement emails\n- Create social media posts\n- Review platform analytics\n\nWhat would you like to do?",
      timestamp: Date.now(),
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [executions, setExecutions] = useState<AgentExecution[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || sending) return;

    const userMessage: Message = {
      role: "user",
      content: input,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setSending(true);

    try {
      const response = await fetch("/api/admin/claude", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [...messages, userMessage],
        }),
      });

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
          timestamp: Date.now(),
        },
      ]);

      if (data.executions) {
        setExecutions((prev) => [...prev, ...data.executions]);
      }
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "I encountered an error. Please try again.",
          timestamp: Date.now(),
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex h-[calc(100vh-1px)] overflow-hidden">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="border-b border-border p-6 flex-shrink-0">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Claude Admin Interface
          </h1>
          <p className="text-sm text-muted mt-1">
            Natural language control over the entire platform
          </p>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-4 ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {message.role === "assistant" && (
                  <div className="w-10 h-10 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center flex-shrink-0">
                    <div className="w-3 h-3 bg-white/90 rounded-full" />
                  </div>
                )}
                <div
                  className={`max-w-[70%] rounded-lg p-4 ${
                    message.role === "user"
                      ? "bg-primary text-white"
                      : "bg-surface border border-border"
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">
                    {message.content}
                  </p>
                  <p className="text-xs mt-2 opacity-60">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </p>
                </div>
                {message.role === "user" && (
                  <div className="w-10 h-10 bg-surface border border-border rounded-lg flex items-center justify-center flex-shrink-0">
                    <span className="text-sm font-semibold">J</span>
                  </div>
                )}
              </div>
            ))}
            {sending && (
              <div className="flex gap-4">
                <div className="w-10 h-10 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center">
                  <div className="w-3 h-3 bg-white/90 rounded-full animate-pulse" />
                </div>
                <div className="bg-surface border border-border rounded-lg p-4">
                  <div className="flex gap-2">
                    <div
                      className="w-2 h-2 bg-muted rounded-full animate-bounce"
                      style={{ animationDelay: "0ms" }}
                    />
                    <div
                      className="w-2 h-2 bg-muted rounded-full animate-bounce"
                      style={{ animationDelay: "150ms" }}
                    />
                    <div
                      className="w-2 h-2 bg-muted rounded-full animate-bounce"
                      style={{ animationDelay: "300ms" }}
                    />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input */}
        <div className="border-t border-border p-6 flex-shrink-0">
          <div className="max-w-3xl mx-auto">
            <div className="flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask Claude to help with platform tasks..."
                className="flex-1 px-4 py-3 bg-surface border border-border rounded-lg focus:outline-none focus:border-primary"
                disabled={sending}
              />
              <button
                onClick={sendMessage}
                disabled={sending || !input.trim()}
                className="px-6 py-3 bg-primary hover:bg-primary-hover text-white rounded-lg font-semibold disabled:opacity-50 transition-colors"
              >
                Send
              </button>
            </div>
            <p className="text-xs text-muted mt-2">
              Example: &quot;Generate a blog post about ADHD productivity
              tips&quot;
            </p>
          </div>
        </div>
      </div>

      {/* Right Sidebar - Agent Activity */}
      <div className="w-72 border-l border-border p-6 overflow-y-auto flex-shrink-0 hidden lg:block">
        <h2 className="text-lg font-bold mb-4">Agent Activity</h2>

        <div className="space-y-3">
          {executions.length === 0 ? (
            <p className="text-sm text-muted">No agent executions yet</p>
          ) : (
            executions
              .slice(-10)
              .reverse()
              .map((exec, i) => (
                <div
                  key={i}
                  className={`p-3 rounded-lg border ${
                    exec.status === "success"
                      ? "border-green-500/50 bg-green-500/5"
                      : exec.status === "error"
                        ? "border-red-500/50 bg-red-500/5"
                        : "border-yellow-500/50 bg-yellow-500/5"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        exec.status === "success"
                          ? "bg-green-500"
                          : exec.status === "error"
                            ? "bg-red-500"
                            : "bg-yellow-500 animate-pulse"
                      }`}
                    />
                    <p className="text-sm font-semibold capitalize">
                      {exec.agent}
                    </p>
                  </div>
                  <p className="text-xs text-muted">{exec.action}</p>
                  {exec.error && (
                    <p className="text-xs text-red-400 mt-1">{exec.error}</p>
                  )}
                </div>
              ))
          )}
        </div>
      </div>
    </div>
  );
}
