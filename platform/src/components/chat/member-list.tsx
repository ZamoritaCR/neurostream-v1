"use client";

import { memo } from "react";
import { useServerStore } from "@/stores/server-store";
import { usePresenceStore, PRESENCE_CONFIGS } from "@/stores/presence-store";
import type { PresenceState, ServerMember } from "@/types/database";
import { Circle } from "lucide-react";

interface MemberItemProps {
  member: ServerMember;
}

const MemberItem = memo(function MemberItem({ member }: MemberItemProps) {
  const profile = member.profile;
  const presenceState = (profile?.presence_state || "offline") as PresenceState;
  const presenceConfig = PRESENCE_CONFIGS[presenceState];

  return (
    <div className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-surface-hover transition-colors">
      <div className="relative">
        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-xs font-medium text-primary">
          {(profile?.display_name || profile?.username || "?")
            .charAt(0)
            .toUpperCase()}
        </div>
        <Circle
          size={10}
          fill={presenceConfig.color}
          className="absolute -bottom-0.5 -right-0.5 border border-surface rounded-full"
          style={{ color: presenceConfig.color }}
        />
      </div>
      <div className="min-w-0">
        <div className="text-sm text-foreground truncate">
          {profile?.display_name || profile?.username || "Unknown"}
        </div>
        <div className="text-xs text-muted">{presenceConfig.label}</div>
      </div>
    </div>
  );
});

export function MemberList() {
  const members = useServerStore((s) => s.members);
  const config = usePresenceStore((s) => s.config);

  if (config.uiDensity === "minimal") return null;

  return (
    <div className="w-60 bg-surface border-l border-border h-full overflow-y-auto py-3 px-3 hidden lg:block">
      <h3 className="text-xs font-semibold text-muted uppercase tracking-wider px-2 mb-2">
        Members{members.length > 0 ? ` — ${members.length}` : ""}
      </h3>
      {members.length === 0 ? (
        <div className="space-y-2 animate-pulse">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex items-center gap-2 px-2 py-1.5">
              <div className="w-8 h-8 rounded-full bg-background/50" />
              <div className="flex-1 space-y-1">
                <div className="h-3 w-20 bg-background/50 rounded" />
                <div className="h-2 w-12 bg-background/50 rounded" />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-0.5">
          {members.map((member) => (
            <MemberItem key={member.id} member={member} />
          ))}
        </div>
      )}
    </div>
  );
}
