"use client";

import { X } from "lucide-react";

const SHORTCUTS = [
  { keys: ["Cmd", "K"], description: "Quick channel switcher" },
  { keys: ["Cmd", "/"], description: "Show keyboard shortcuts" },
  { keys: ["Enter"], description: "Send message" },
  { keys: ["Shift", "Enter"], description: "New line in message" },
  { keys: ["Esc"], description: "Close modal / cancel" },
];

interface ShortcutsModalProps {
  open: boolean;
  onClose: () => void;
}

export function ShortcutsModal({ open, onClose }: ShortcutsModalProps) {
  if (!open) return null;

  const isMac =
    typeof navigator !== "undefined" && navigator.platform.includes("Mac");

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-surface border border-border rounded-xl w-full max-w-md shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <h2 className="font-semibold text-foreground">Keyboard Shortcuts</h2>
          <button
            onClick={onClose}
            className="text-muted hover:text-foreground transition-colors"
          >
            <X size={18} />
          </button>
        </div>
        <div className="px-6 py-4 space-y-3">
          {SHORTCUTS.map((shortcut, i) => (
            <div
              key={i}
              className="flex items-center justify-between text-sm"
            >
              <span className="text-muted">{shortcut.description}</span>
              <div className="flex items-center gap-1">
                {shortcut.keys.map((key, j) => (
                  <span key={j}>
                    {j > 0 && (
                      <span className="text-muted mx-0.5">+</span>
                    )}
                    <kbd className="bg-background text-foreground px-2 py-1 rounded border border-border text-xs min-w-[28px] text-center inline-block">
                      {key === "Cmd" ? (isMac ? "\u2318" : "Ctrl") : key}
                    </kbd>
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
