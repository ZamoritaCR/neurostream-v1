export type PresenceState = "online" | "hyperfocus" | "high_energy" | "low_bandwidth" | "task_mode" | "offline";

export interface Profile {
  id: string;
  username: string;
  display_name: string | null;
  avatar_url: string | null;
  presence_state: PresenceState;
  created_at: string;
  updated_at: string;
}

export interface Server {
  id: string;
  name: string;
  description: string | null;
  icon_url: string | null;
  owner_id: string;
  created_at: string;
}

export interface Channel {
  id: string;
  server_id: string;
  name: string;
  description: string | null;
  channel_type: "text" | "voice";
  position: number;
  created_at: string;
}

export interface Message {
  id: string;
  channel_id: string;
  author_id: string;
  content: string;
  edited_at: string | null;
  created_at: string;
  author?: Profile;
}

export interface ServerMember {
  id: string;
  server_id: string;
  user_id: string;
  role: "owner" | "admin" | "member";
  joined_at: string;
  profile?: Profile;
}
