import { supabase } from "./client";

export async function ensureUserInDefaultServer(userId: string) {
  const { data: existing } = await supabase
    .from("server_members")
    .select("id")
    .eq("server_id", "00000000-0000-0000-0000-000000000001")
    .eq("user_id", userId)
    .single();

  if (existing) return;

  await supabase.from("server_members").insert({
    server_id: "00000000-0000-0000-0000-000000000001",
    user_id: userId,
    role: "member",
  });
}
