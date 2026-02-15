import { create } from "zustand";
import { supabase } from "@/lib/supabase/client";
import type { Message, Profile } from "@/types/database";
import type { RealtimeChannel } from "@supabase/supabase-js";

const MESSAGE_LIMIT = 50;
const PROFILE_SELECT = "id, username, display_name, avatar_url, presence_state";
const MESSAGE_SELECT = `id, content, created_at, edited_at, channel_id, author_id, author:profiles(${PROFILE_SELECT})`;

// Cache author profiles to avoid re-fetching on every realtime INSERT
const profileCache = new Map<string, Profile>();

// Cache current user ID to avoid calling getUser() on every message send
let cachedUserId: string | null = null;
async function getCurrentUserId(): Promise<string | null> {
  if (cachedUserId) return cachedUserId;
  const { data: { user } } = await supabase.auth.getUser();
  cachedUserId = user?.id ?? null;
  return cachedUserId;
}
// Clear cache on auth state change
supabase.auth.onAuthStateChange((_event, session) => {
  cachedUserId = session?.user?.id ?? null;
});

interface ChatState {
  messages: Message[];
  loading: boolean;
  subscription: RealtimeChannel | null;
  fetchMessages: (channelId: string) => Promise<void>;
  sendMessage: (channelId: string, content: string) => Promise<void>;
  subscribeToChannel: (channelId: string) => void;
  unsubscribe: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  loading: false,
  subscription: null,

  fetchMessages: async (channelId) => {
    set({ loading: true });
    const { data } = await supabase
      .from("messages")
      .select(MESSAGE_SELECT)
      .eq("channel_id", channelId)
      .order("created_at", { ascending: false })
      .limit(MESSAGE_LIMIT);

    // Reverse since we fetch desc for the LIMIT to get the *latest* 50
    const messages = ((data as unknown as Message[]) || []).reverse();

    // Populate profile cache from fetched messages
    for (const msg of messages) {
      if (msg.author) {
        profileCache.set(msg.author_id, msg.author);
      }
    }

    set({ messages, loading: false });
  },

  sendMessage: async (channelId, content) => {
    const userId = await getCurrentUserId();
    if (!userId || !content.trim()) return;

    const trimmed = content.trim();

    // Optimistic update: show message immediately
    const optimisticId = `optimistic-${Date.now()}`;
    const cachedProfile = profileCache.get(userId);
    const optimisticMessage: Message = {
      id: optimisticId,
      channel_id: channelId,
      author_id: userId,
      content: trimmed,
      edited_at: null,
      created_at: new Date().toISOString(),
      author: cachedProfile,
    };

    set((state) => ({
      messages: [...state.messages, optimisticMessage],
    }));

    const { data, error } = await supabase
      .from("messages")
      .insert({
        channel_id: channelId,
        author_id: userId,
        content: trimmed,
      })
      .select("id")
      .single();

    if (error) {
      // Remove optimistic message on failure
      set((state) => ({
        messages: state.messages.filter((m) => m.id !== optimisticId),
      }));
      return;
    }

    // Replace optimistic ID with real ID
    if (data) {
      set((state) => ({
        messages: state.messages.map((m) =>
          m.id === optimisticId ? { ...m, id: data.id } : m
        ),
      }));
    }
  },

  subscribeToChannel: (channelId) => {
    get().unsubscribe();

    const subscription = supabase
      .channel(`messages:${channelId}`)
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "public",
          table: "messages",
          filter: `channel_id=eq.${channelId}`,
        },
        async (payload) => {
          const newMsg = payload.new as Message;

          // Skip if we already have this message (from optimistic update)
          const existing = get().messages;
          if (existing.some((m) => m.id === newMsg.id)) return;

          // Use cached profile if available, otherwise fetch just the profile
          let author = profileCache.get(newMsg.author_id);
          if (!author) {
            const { data } = await supabase
              .from("profiles")
              .select(PROFILE_SELECT)
              .eq("id", newMsg.author_id)
              .single();
            if (data) {
              author = data as Profile;
              profileCache.set(newMsg.author_id, author);
            }
          }

          set((state) => ({
            messages: [...state.messages, { ...newMsg, author }],
          }));
        }
      )
      .on(
        "postgres_changes",
        {
          event: "DELETE",
          schema: "public",
          table: "messages",
          filter: `channel_id=eq.${channelId}`,
        },
        (payload) => {
          set((state) => ({
            messages: state.messages.filter((m) => m.id !== payload.old.id),
          }));
        }
      )
      .on(
        "postgres_changes",
        {
          event: "UPDATE",
          schema: "public",
          table: "messages",
          filter: `channel_id=eq.${channelId}`,
        },
        (payload) => {
          const updated = payload.new as Message;
          set((state) => ({
            messages: state.messages.map((m) =>
              m.id === updated.id ? { ...m, ...updated } : m
            ),
          }));
        }
      )
      .subscribe();

    set({ subscription });
  },

  unsubscribe: () => {
    const { subscription } = get();
    if (subscription) {
      supabase.removeChannel(subscription);
      set({ subscription: null });
    }
  },
}));
