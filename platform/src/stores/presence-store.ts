import { create } from "zustand";
import { persist } from "zustand/middleware";
import { supabase } from "@/lib/supabase/client";
import type { PresenceState } from "@/types/database";

// ═══════════════════════════════════════════════════════════════
// PRESENCE CONFIGS (existing — controls UI adaptation per state)
// Research: Brain 4, Section 6 — ADHD-optimized UI density
// ═══════════════════════════════════════════════════════════════

interface PresenceConfig {
  label: string;
  description: string;
  color: string;
  icon: string;
  uiDensity: "minimal" | "normal" | "compact";
  showAvatars: boolean;
  showTimestamps: boolean;
  animationsEnabled: boolean;
  notificationsEnabled: boolean;
  maxVisibleChannels: number | null;
}

export const PRESENCE_CONFIGS: Record<PresenceState, PresenceConfig> = {
  online: {
    label: "Online",
    description: "Default state",
    color: "#4ecdc4",
    icon: "Circle",
    uiDensity: "normal",
    showAvatars: true,
    showTimestamps: true,
    animationsEnabled: true,
    notificationsEnabled: true,
    maxVisibleChannels: null,
  },
  hyperfocus: {
    label: "Hyperfocus",
    description: "Deep work mode — minimal distractions",
    color: "#e74c8a",
    icon: "Zap",
    uiDensity: "minimal",
    showAvatars: false,
    showTimestamps: false,
    animationsEnabled: false,
    notificationsEnabled: false,
    maxVisibleChannels: 1,
  },
  high_energy: {
    label: "High Energy",
    description: "Social and engaged — full UI",
    color: "#f5a623",
    icon: "Flame",
    uiDensity: "normal",
    showAvatars: true,
    showTimestamps: true,
    animationsEnabled: true,
    notificationsEnabled: true,
    maxVisibleChannels: null,
  },
  low_bandwidth: {
    label: "Low Bandwidth",
    description: "Low energy — simplified view",
    color: "#6b6c80",
    icon: "Battery",
    uiDensity: "compact",
    showAvatars: false,
    showTimestamps: true,
    animationsEnabled: false,
    notificationsEnabled: false,
    maxVisibleChannels: 3,
  },
  task_mode: {
    label: "Task Mode",
    description: "Focused on tasks — thread-only view",
    color: "#4ecdc4",
    icon: "ListChecks",
    uiDensity: "compact",
    showAvatars: true,
    showTimestamps: true,
    animationsEnabled: false,
    notificationsEnabled: true,
    maxVisibleChannels: 3,
  },
  offline: {
    label: "Offline",
    description: "Away",
    color: "#3a3b50",
    icon: "CircleOff",
    uiDensity: "normal",
    showAvatars: true,
    showTimestamps: true,
    animationsEnabled: true,
    notificationsEnabled: false,
    maxVisibleChannels: null,
  },
};

// ═══════════════════════════════════════════════════════════════
// HEALTH MONITORING (Phase 1M — Hyperfocus Protection)
// Research: Brain 1, Section 3 — ADHD hyperfocus causes skipped meals
// Research: Brain 5, Section 4 — Celebrate attempts, never shame breaks
// ═══════════════════════════════════════════════════════════════

interface HealthReminder {
  type: "water" | "food" | "break" | "medication";
  message: string;
  timestamp: number;
  dismissed: boolean;
}

interface PresenceStoreState {
  // Existing
  currentState: PresenceState;
  config: PresenceConfig;
  setPresence: (state: PresenceState) => Promise<void>;

  // Health monitoring
  hyperfocusStartTime: number | null;
  lastMealTime: number | null;
  lastWaterTime: number | null;
  lastBreakTime: number | null;
  healthReminders: HealthReminder[];

  // Health actions
  recordMeal: () => void;
  recordWater: () => void;
  recordBreak: () => void;
  addHealthReminder: (
    reminder: Omit<HealthReminder, "timestamp" | "dismissed">
  ) => void;
  dismissReminder: (index: number) => void;

  // Health queries
  getTimeSinceLastMeal: () => number | null;
  getTimeSinceLastWater: () => number | null;
  shouldShowFoodReminder: () => boolean;
  shouldShowWaterReminder: () => boolean;
  shouldShowBreakReminder: () => boolean;
}

export const usePresenceStore = create<PresenceStoreState>()(
  persist(
    (set, get) => ({
      // ── Existing state ──
      currentState: "online" as PresenceState,
      config: PRESENCE_CONFIGS.online,

      setPresence: async (state) => {
        // Update UI immediately
        set({ currentState: state, config: PRESENCE_CONFIGS[state] });

        // Start/end hyperfocus monitoring
        if (state === "hyperfocus") {
          const now = Date.now();
          set({ hyperfocusStartTime: now, lastBreakTime: now });
        } else if (get().hyperfocusStartTime) {
          set({ hyperfocusStartTime: null });
        }

        // Persist to DB in background
        const {
          data: { session },
        } = await supabase.auth.getSession();
        if (session?.user) {
          supabase
            .from("profiles")
            .update({ presence_state: state })
            .eq("id", session.user.id)
            .then();
        }
      },

      // ── Health monitoring state ──
      hyperfocusStartTime: null,
      lastMealTime: null,
      lastWaterTime: null,
      lastBreakTime: null,
      healthReminders: [],

      // ── Health actions ──
      recordMeal: () => set({ lastMealTime: Date.now() }),
      recordWater: () => set({ lastWaterTime: Date.now() }),
      recordBreak: () => set({ lastBreakTime: Date.now() }),

      addHealthReminder: (reminder) => {
        set((state) => ({
          healthReminders: [
            ...state.healthReminders,
            { ...reminder, timestamp: Date.now(), dismissed: false },
          ],
        }));
      },

      dismissReminder: (index) => {
        set((state) => ({
          healthReminders: state.healthReminders.map((r, i) =>
            i === index ? { ...r, dismissed: true } : r
          ),
        }));
      },

      // ── Health queries ──
      getTimeSinceLastMeal: () => {
        const { lastMealTime } = get();
        return lastMealTime ? Date.now() - lastMealTime : null;
      },

      getTimeSinceLastWater: () => {
        const { lastWaterTime } = get();
        return lastWaterTime ? Date.now() - lastWaterTime : null;
      },

      // Hyperfocus: remind after 3 hours | Normal: after 5 hours
      shouldShowFoodReminder: () => {
        const timeSinceMeal = get().getTimeSinceLastMeal();
        if (!timeSinceMeal) return false;
        const isHyperfocus = get().currentState === "hyperfocus";
        const threshold = isHyperfocus
          ? 3 * 60 * 60 * 1000
          : 5 * 60 * 60 * 1000;
        return timeSinceMeal > threshold;
      },

      // Hyperfocus: remind after 90 min | Normal: after 2 hours
      shouldShowWaterReminder: () => {
        const timeSinceWater = get().getTimeSinceLastWater();
        if (!timeSinceWater) return false;
        const isHyperfocus = get().currentState === "hyperfocus";
        const threshold = isHyperfocus
          ? 90 * 60 * 1000
          : 2 * 60 * 60 * 1000;
        return timeSinceWater > threshold;
      },

      // Hyperfocus only: remind every 90 min to take a break
      shouldShowBreakReminder: () => {
        const { lastBreakTime, currentState } = get();
        if (!lastBreakTime || currentState !== "hyperfocus") return false;
        return Date.now() - lastBreakTime > 90 * 60 * 1000;
      },
    }),
    {
      name: "presence-storage",
      partialize: (state) => ({
        currentState: state.currentState,
        hyperfocusStartTime: state.hyperfocusStartTime,
        lastMealTime: state.lastMealTime,
        lastWaterTime: state.lastWaterTime,
        lastBreakTime: state.lastBreakTime,
      }),
    }
  )
);
