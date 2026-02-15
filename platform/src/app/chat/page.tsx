"use client";

import { useAuth } from "@/components/shared/AuthProvider";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { ChatView } from "@/components/chat/chat-view";
import { MrDPChat } from "@/components/app/MrDPChat";
import { HealthMonitor } from "@/components/app/HealthMonitor";

export default function ChatPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push("/auth");
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted">Loading...</p>
      </div>
    );
  }

  if (!user) return null;

  return (
    <>
      <ChatView />
      {/* Health Monitor - Research: Brain 1, Section 3 (hyperfocus protection) */}
      <HealthMonitor />
      {/* Mr.DP Floating Chat - Research: Brain 1 (ADHD emotional dysregulation), Brain 6 (DBT/CBT) */}
      <MrDPChat context={{ recentActivity: "chatting" }} />
    </>
  );
}
