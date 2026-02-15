"use client";

import { useState } from "react";
import { usePresenceStore, PRESENCE_CONFIGS } from "@/stores/presence-store";
import { useAuth } from "@/components/shared/AuthProvider";
import type { PresenceState } from "@/types/database";
import {
  Circle,
  Zap,
  Flame,
  Battery,
  ListChecks,
  LogOut,
  ChevronUp,
} from "lucide-react";

const ICONS: Record<string, React.ComponentType<{ size?: number; className?: string; style?: React.CSSProperties }>> = {
  Circle,
  Zap,
  Flame,
  Battery,
  ListChecks,
  CircleOff: Circle,
};

const SELECTABLE_STATES: PresenceState[] = [
  "online",
  "hyperfocus",
  "high_energy",
  "low_bandwidth",
  "task_mode",
];

export function PresenceSelector() {
  const [open, setOpen] = useState(false);
  const currentState = usePresenceStore((s) => s.currentState);
  const config = usePresenceStore((s) => s.config);
  const setPresence = usePresenceStore((s) => s.setPresence);
  const { user, signOut } = useAuth();

  const Icon = ICONS[config.icon] || Circle;

  return (
    <div className="relative">
      {/* Dropdown */}
      {open && (
        <div className="absolute bottom-full left-0 right-0 mb-1 bg-surface border border-border rounded-lg overflow-hidden shadow-lg z-50">
          {SELECTABLE_STATES.map((state) => {
            const c = PRESENCE_CONFIGS[state];
            const StateIcon = ICONS[c.icon] || Circle;
            return (
              <button
                key={state}
                onClick={() => {
                  setPresence(state);
                  setOpen(false);
                }}
                className={`w-full flex items-center gap-3 px-3 py-2.5 text-sm transition-colors hover:bg-surface-hover ${
                  currentState === state ? "bg-primary/10" : ""
                }`}
              >
                <StateIcon size={16} className="shrink-0" style={{ color: c.color }} />
                <div className="text-left">
                  <div className="text-foreground font-medium">{c.label}</div>
                  <div className="text-xs text-muted">{c.description}</div>
                </div>
              </button>
            );
          })}
          <div className="border-t border-border">
            <button
              onClick={() => {
                signOut();
                setOpen(false);
              }}
              className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-danger hover:bg-surface-hover transition-colors"
            >
              <LogOut size={16} />
              <span>Sign out</span>
            </button>
          </div>
        </div>
      )}

      {/* User bar */}
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-2 px-3 py-2.5 hover:bg-surface-hover transition-colors rounded-md"
      >
        <div className="relative">
          <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-xs font-medium text-primary">
            {(user?.email || "?").charAt(0).toUpperCase()}
          </div>
          <div
            className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full border-2 border-surface flex items-center justify-center"
            style={{ backgroundColor: config.color }}
          >
            <Icon size={8} className="text-white" />
          </div>
        </div>
        <div className="flex-1 text-left min-w-0">
          <div className="text-sm font-medium text-foreground truncate">
            {user?.email?.split("@")[0] || "User"}
          </div>
          <div className="text-xs text-muted">{config.label}</div>
        </div>
        <ChevronUp
          size={14}
          className={`text-muted transition-transform ${open ? "" : "rotate-180"}`}
        />
      </button>
    </div>
  );
}
