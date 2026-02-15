"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
  expression?: string;
}

interface MrDPChatProps {
  context?: {
    currentMood?: string;
    targetMood?: string;
    recentActivity?: string;
  };
}

const expressionEmojis: Record<string, string> = {
  happy: "\u{1F60A}",
  thinking: "\u{1F914}",
  excited: "\u{1F929}",
  listening: "\u{1F442}",
  sad: "\u{1F622}",
  love: "\u{1F49C}",
  surprised: "\u{1F632}",
  wink: "\u{1F609}",
  confused: "\u{1F615}",
  cool: "\u{1F60E}",
  focused: "\u{1F3AF}",
  sleeping: "\u{1F634}",
};

export function MrDPChat({ context }: MrDPChatProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hey there! \u{1F49C} I'm Mr.DP, your friendly dopamine molecule. How are you feeling today?",
      expression: "happy",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [currentExpression, setCurrentExpression] = useState("happy");

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("/api/mr-dp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [...messages, userMessage].map((m) => ({
            role: m.role,
            content: m.content,
          })),
          context,
        }),
      });

      const data = await response.json();

      setCurrentExpression(data.expression || "happy");
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.message,
          expression: data.expression,
        },
      ]);
    } catch (error) {
      console.error("Error chatting with Mr.DP:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Oops, I got a bit confused there. Can you try again? \u{1F49C}",
          expression: "confused",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      {/* Professional Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-br from-primary to-accent rounded-full shadow-lg hover:shadow-xl hover:scale-105 transition-all flex items-center justify-center z-50"
        aria-label="Assistant"
      >
        {isOpen ? (
          <svg
            className="w-5 h-5 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        ) : (
          <div className="w-3 h-3 bg-white/90 rounded-full animate-pulse" />
        )}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-96 h-[500px] bg-surface border border-border rounded-lg shadow-2xl flex flex-col z-50">
          {/* Header */}
          <div className="p-4 border-b border-border bg-gradient-to-r from-primary/20 to-accent/20">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary to-accent rounded-full flex items-center justify-center text-2xl">
                {expressionEmojis[currentExpression] || "\u{1F49C}"}
              </div>
              <div>
                <h3 className="font-bold">Mr.DP</h3>
                <p className="text-xs text-muted">
                  Your friendly dopamine molecule
                </p>
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-2 ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {message.role === "assistant" && (
                  <div className="w-8 h-8 bg-gradient-to-br from-primary to-accent rounded-full flex items-center justify-center text-lg flex-shrink-0">
                    {expressionEmojis[message.expression || "happy"] ||
                      "\u{1F49C}"}
                  </div>
                )}
                <div
                  className={`max-w-[75%] rounded-lg p-3 ${
                    message.role === "user"
                      ? "bg-primary text-white"
                      : "bg-surface-hover"
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex gap-2">
                <div className="w-8 h-8 bg-gradient-to-br from-primary to-accent rounded-full flex items-center justify-center text-lg">
                  {expressionEmojis.thinking}
                </div>
                <div className="bg-surface-hover rounded-lg p-3">
                  <div className="flex gap-1">
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

          {/* Input */}
          <div className="p-4 border-t border-border">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type a message..."
                className="flex-1 px-3 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:border-primary"
                disabled={loading}
              />
              <button
                onClick={sendMessage}
                disabled={loading || !input.trim()}
                className="px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded-lg text-sm font-semibold disabled:opacity-50 transition-colors"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
