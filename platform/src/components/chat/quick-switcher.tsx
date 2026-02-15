"use client";

import { useState, useEffect, useRef, useMemo, useCallback } from "react";
import { useServerStore } from "@/stores/server-store";
import { Hash, Volume2, Search } from "lucide-react";

interface QuickSwitcherProps {
  open: boolean;
  onClose: () => void;
}

export function QuickSwitcher({ open, onClose }: QuickSwitcherProps) {
  const [search, setSearch] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const channels = useServerStore((s) => s.channels);
  const setCurrentChannel = useServerStore((s) => s.setCurrentChannel);

  const filtered = useMemo(
    () =>
      channels.filter((c) =>
        c.name.toLowerCase().includes(search.toLowerCase())
      ),
    [channels, search]
  );

  // Reset state when opening
  useEffect(() => {
    if (open) {
      setSearch("");
      setSelectedIndex(0);
      // Focus after render
      requestAnimationFrame(() => inputRef.current?.focus());
    }
  }, [open]);

  // Keyboard navigation
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((i) => Math.min(i + 1, filtered.length - 1));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((i) => Math.max(i - 1, 0));
      } else if (e.key === "Enter" && filtered[selectedIndex]) {
        e.preventDefault();
        setCurrentChannel(filtered[selectedIndex].id);
        onClose();
      } else if (e.key === "Escape") {
        onClose();
      }
    },
    [filtered, selectedIndex, setCurrentChannel, onClose]
  );

  // Reset selection when search changes
  useEffect(() => {
    setSelectedIndex(0);
  }, [search]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-start justify-center pt-24 z-50"
      onClick={onClose}
    >
      <div
        className="bg-surface border border-border rounded-xl w-full max-w-lg shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-3 px-4 border-b border-border">
          <Search size={18} className="text-muted shrink-0" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Search channels..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={handleKeyDown}
            className="w-full py-4 bg-transparent text-foreground placeholder:text-muted text-sm focus:outline-none"
          />
          <kbd className="text-xs text-muted bg-background px-2 py-1 rounded border border-border shrink-0">
            esc
          </kbd>
        </div>
        <div className="max-h-72 overflow-y-auto py-1">
          {filtered.length === 0 ? (
            <div className="px-4 py-8 text-center text-sm text-muted">
              No channels found
            </div>
          ) : (
            filtered.map((channel, i) => (
              <button
                key={channel.id}
                onClick={() => {
                  setCurrentChannel(channel.id);
                  onClose();
                }}
                className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                  i === selectedIndex
                    ? "bg-primary/10 text-foreground"
                    : "text-muted hover:bg-surface-hover hover:text-foreground"
                }`}
              >
                {channel.channel_type === "voice" ? (
                  <Volume2 size={16} className="opacity-60 shrink-0" />
                ) : (
                  <Hash size={16} className="opacity-60 shrink-0" />
                )}
                <span className="truncate">{channel.name}</span>
                {channel.description && (
                  <span className="text-xs text-muted truncate ml-auto">
                    {channel.description}
                  </span>
                )}
              </button>
            ))
          )}
        </div>
        <div className="border-t border-border px-4 py-2 flex items-center gap-4 text-xs text-muted">
          <span>
            <kbd className="bg-background px-1.5 py-0.5 rounded border border-border mr-1">
              &uarr;&darr;
            </kbd>
            navigate
          </span>
          <span>
            <kbd className="bg-background px-1.5 py-0.5 rounded border border-border mr-1">
              enter
            </kbd>
            select
          </span>
          <span>
            <kbd className="bg-background px-1.5 py-0.5 rounded border border-border mr-1">
              esc
            </kbd>
            close
          </span>
        </div>
      </div>
    </div>
  );
}
