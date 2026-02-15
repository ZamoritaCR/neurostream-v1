"use client";

import { useEffect, useRef, useMemo, memo, useCallback } from "react";
import { useChatStore } from "@/stores/chat-store";
import { usePresenceStore } from "@/stores/presence-store";
import { useVirtualizer } from "@tanstack/react-virtual";
import { formatDistanceToNow } from "date-fns";
import type { Message } from "@/types/database";

interface PresenceConfig {
  uiDensity: "minimal" | "normal" | "compact";
  showAvatars: boolean;
  showTimestamps: boolean;
}

interface MessageItemProps {
  message: Message;
  showHeader: boolean;
  config: PresenceConfig;
}

const MessageItem = memo(function MessageItem({
  message,
  showHeader,
  config,
}: MessageItemProps) {
  const paddingLeft =
    config.showAvatars && showHeader
      ? "pl-10"
      : showHeader
        ? "pl-0"
        : config.showAvatars
          ? "pl-10"
          : "pl-0";

  return (
    <div
      className={`group ${showHeader ? "mt-4 first:mt-0" : ""} ${
        config.uiDensity === "compact" ? "py-0.5" : "py-1"
      }`}
    >
      {showHeader && (
        <div className="flex items-center gap-2 mb-0.5">
          {config.showAvatars && (
            <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-xs font-medium text-primary shrink-0">
              {(
                message.author?.display_name ||
                message.author?.username ||
                "?"
              )
                .charAt(0)
                .toUpperCase()}
            </div>
          )}
          <span className="text-sm font-medium text-foreground">
            {message.author?.display_name ||
              message.author?.username ||
              "Unknown"}
          </span>
          {config.showTimestamps && (
            <span className="text-xs text-muted">
              {formatDistanceToNow(new Date(message.created_at), {
                addSuffix: true,
              })}
            </span>
          )}
        </div>
      )}
      <div className={`text-sm text-foreground/90 ${paddingLeft}`}>
        {message.content}
      </div>
    </div>
  );
});

export function MessageList() {
  const messages = useChatStore((s) => s.messages);
  const loading = useChatStore((s) => s.loading);
  const config = usePresenceStore((s) => s.config);
  const parentRef = useRef<HTMLDivElement>(null);
  const prevCountRef = useRef(0);

  // Pre-compute which messages show headers
  const showHeaders = useMemo(() => {
    return messages.map((message, i) => {
      const prev = messages[i - 1];
      return (
        !prev ||
        prev.author_id !== message.author_id ||
        new Date(message.created_at).getTime() -
          new Date(prev.created_at).getTime() >
          300000
      );
    });
  }, [messages]);

  const estimateSize = useCallback(
    (index: number) => {
      // Header messages are taller than continuation messages
      if (showHeaders[index]) {
        return config.uiDensity === "compact" ? 52 : 60;
      }
      return config.uiDensity === "compact" ? 24 : 28;
    },
    [showHeaders, config.uiDensity]
  );

  const virtualizer = useVirtualizer({
    count: messages.length,
    getScrollElement: () => parentRef.current,
    estimateSize,
    overscan: 10,
  });

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messages.length > prevCountRef.current && messages.length > 0) {
      virtualizer.scrollToIndex(messages.length - 1, { align: "end" });
    }
    prevCountRef.current = messages.length;
  }, [messages.length, virtualizer]);

  if (loading) {
    return (
      <div className="flex-1 px-4 py-3 space-y-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="flex items-center gap-2 mb-1">
              <div className="w-8 h-8 rounded-full bg-surface" />
              <div className="h-3 w-24 bg-surface rounded" />
              <div className="h-2 w-12 bg-surface rounded" />
            </div>
            <div className="pl-10 space-y-1">
              <div className="h-3 bg-surface rounded" style={{ width: `${60 + Math.random() * 30}%` }} />
              {i % 2 === 0 && <div className="h-3 bg-surface rounded w-2/5" />}
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <span className="text-muted">
          No messages yet. Start the conversation!
        </span>
      </div>
    );
  }

  return (
    <div ref={parentRef} className="flex-1 overflow-y-auto px-4 py-3">
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: "100%",
          position: "relative",
        }}
      >
        {virtualizer.getVirtualItems().map((virtualRow) => (
          <div
            key={messages[virtualRow.index].id}
            data-index={virtualRow.index}
            ref={virtualizer.measureElement}
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              transform: `translateY(${virtualRow.start}px)`,
            }}
          >
            <MessageItem
              message={messages[virtualRow.index]}
              showHeader={showHeaders[virtualRow.index]}
              config={config}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
