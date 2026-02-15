import { create } from "zustand";
import { supabase } from "@/lib/supabase/client";
import type { Server, Channel, ServerMember } from "@/types/database";

const SERVER_SELECT = "id, name, description, icon_url, owner_id, created_at";
const CHANNEL_SELECT = "id, server_id, name, description, channel_type, position, created_at";
const MEMBER_SELECT = "id, server_id, user_id, role, joined_at, profile:profiles(id, username, display_name, avatar_url, presence_state)";

interface ServerState {
  servers: Server[];
  currentServerId: string | null;
  channels: Channel[];
  currentChannelId: string | null;
  members: ServerMember[];
  loading: boolean;
  fetchServers: () => Promise<void>;
  fetchChannels: (serverId: string) => Promise<void>;
  fetchMembers: (serverId: string) => Promise<void>;
  setCurrentServer: (serverId: string) => void;
  setCurrentChannel: (channelId: string) => void;
  createServer: (name: string, description?: string) => Promise<Server | null>;
  createChannel: (serverId: string, name: string) => Promise<Channel | null>;
}

export const useServerStore = create<ServerState>((set, get) => ({
  servers: [],
  currentServerId: null,
  channels: [],
  currentChannelId: null,
  members: [],
  loading: false,

  fetchServers: async () => {
    set({ loading: true });
    const { data } = await supabase
      .from("servers")
      .select(SERVER_SELECT)
      .order("created_at", { ascending: true });
    set({ servers: (data as Server[]) || [], loading: false });
  },

  fetchChannels: async (serverId) => {
    const { data } = await supabase
      .from("channels")
      .select(CHANNEL_SELECT)
      .eq("server_id", serverId)
      .order("position", { ascending: true });
    set({ channels: (data as Channel[]) || [] });
  },

  fetchMembers: async (serverId) => {
    const { data } = await supabase
      .from("server_members")
      .select(MEMBER_SELECT)
      .eq("server_id", serverId);
    set({ members: (data as unknown as ServerMember[]) || [] });
  },

  setCurrentServer: (serverId) => {
    set({ currentServerId: serverId, currentChannelId: null, channels: [], members: [] });
    // Fetch channels and members in parallel
    Promise.all([get().fetchChannels(serverId), get().fetchMembers(serverId)]);
  },

  setCurrentChannel: (channelId) => {
    set({ currentChannelId: channelId });
  },

  createServer: async (name, description) => {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return null;

    const { data: server, error } = await supabase
      .from("servers")
      .insert({ name, description, owner_id: user.id })
      .select()
      .single();

    if (error || !server) return null;

    // Add owner as member
    await supabase.from("server_members").insert({
      server_id: server.id,
      user_id: user.id,
      role: "owner",
    });

    // Create default #general channel
    await supabase.from("channels").insert({
      server_id: server.id,
      name: "general",
      position: 0,
    });

    await get().fetchServers();
    return server as Server;
  },

  createChannel: async (serverId, name) => {
    const channels = get().channels;
    const { data, error } = await supabase
      .from("channels")
      .insert({
        server_id: serverId,
        name: name.toLowerCase().replace(/\s+/g, "-"),
        position: channels.length,
      })
      .select()
      .single();

    if (error || !data) return null;
    await get().fetchChannels(serverId);
    return data as Channel;
  },
}));
