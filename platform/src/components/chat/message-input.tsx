"use client";

import { useState, useCallback, KeyboardEvent, memo } from "react";
import { useChatStore } from "@/stores/chat-store";
import { Send } from "lucide-react";

interface MessageInputProps {
  channelId: string;
  channelName: string;
}

export const MessageInput = memo(function MessageInput({
  channelId,
  channelName,
}: MessageInputProps) {
  const [content, setContent] = useState("");
  const sendMessage = useChatStore((s) => s.sendMessage);

  const handleSend = useCallback(async () => {
    if (!content.trim()) return;
    const msg = content;
    setContent("");
    await sendMessage(channelId, msg);
  }, [content, channelId, sendMessage]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  return (
    <div className="px-4 pb-4">
      <div className="flex items-end gap-2 rounded-xl bg-surface border border-border px-4 py-3">
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`Message #${channelName}`}
          rows={1}
          className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted resize-none focus:outline-none max-h-32"
          style={{ minHeight: "24px" }}
        />
        <button
          onClick={handleSend}
          disabled={!content.trim()}
          className="text-muted hover:text-primary disabled:opacity-30 transition-colors shrink-0 pb-0.5"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
});
