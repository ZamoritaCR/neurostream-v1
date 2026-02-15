"use client";

import { useState, useMemo, useCallback, memo } from "react";
import { useServerStore } from "@/stores/server-store";
import { usePresenceStore } from "@/stores/presence-store";
import { Hash, Plus, Volume2 } from "lucide-react";
import type { Channel } from "@/types/database";

interface ChannelItemProps {
  channel: Channel;
  isActive: boolean;
  onSelect: (id: string) => void;
  icon: "text" | "voice";
}

const ChannelItem = memo(function ChannelItem({
  channel,
  isActive,
  onSelect,
  icon,
}: ChannelItemProps) {
  return (
    <button
      onClick={() => onSelect(channel.id)}
      className={`w-full flex items-center gap-2 px-2 py-1.5 rounded-md text-sm transition-colors ${
        isActive
          ? "bg-primary/10 text-foreground"
          : "text-muted hover:text-foreground hover:bg-surface-hover"
      }`}
    >
      {icon === "voice" ? (
        <Volume2 size={16} className="shrink-0 opacity-60" />
      ) : (
        <Hash size={16} className="shrink-0 opacity-60" />
      )}
      <span className="truncate">{channel.name}</span>
    </button>
  );
});

function ChannelSkeleton() {
  return (
    <div className="py-3 px-2 space-y-4 animate-pulse">
      <div>
        <div className="h-3 w-24 bg-background/50 rounded mb-2 px-2" />
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="flex items-center gap-2 px-2 py-1.5">
            <div className="w-4 h-4 bg-background/50 rounded" />
            <div className="h-3 bg-background/50 rounded" style={{ width: `${50 + i * 10}%` }} />
          </div>
        ))}
      </div>
    </div>
  );
}

export function ChannelSidebar() {
  const channels = useServerStore((s) => s.channels);
  const currentChannelId = useServerStore((s) => s.currentChannelId);
  const currentServerId = useServerStore((s) => s.currentServerId);
  const setCurrentChannel = useServerStore((s) => s.setCurrentChannel);
  const createChannel = useServerStore((s) => s.createChannel);
  const config = usePresenceStore((s) => s.config);
  const servers = useServerStore((s) => s.servers);
  const loading = useServerStore((s) => s.loading);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");

  const currentServer = useMemo(
    () => servers.find((s) => s.id === currentServerId),
    [servers, currentServerId]
  );

  const { textChannels, voiceChannels } = useMemo(() => {
    const visible = config.maxVisibleChannels
      ? channels.slice(0, config.maxVisibleChannels)
      : channels;
    return {
      textChannels: visible.filter((c) => c.channel_type === "text"),
      voiceChannels: visible.filter((c) => c.channel_type === "voice"),
    };
  }, [channels, config.maxVisibleChannels]);

  const handleCreateChannel = useCallback(async () => {
    if (!newName.trim() || !currentServerId) return;
    await createChannel(currentServerId, newName);
    setNewName("");
    setShowCreate(false);
  }, [newName, currentServerId, createChannel]);

  return (
    <div className="w-60 bg-surface border-r border-border flex flex-col h-full">
      <div className="px-4 h-12 flex items-center border-b border-border shrink-0">
        <h2 className="font-semibold text-sm text-foreground truncate">
          {currentServer?.name || "Select a server"}
        </h2>
      </div>

      {loading && channels.length === 0 ? (
        <ChannelSkeleton />
      ) : (
      <div className="flex-1 overflow-y-auto py-3 px-2 space-y-4">
        {textChannels.length > 0 && (
          <div>
            <div className="flex items-center justify-between px-2 mb-1">
              <span className="text-xs font-semibold text-muted uppercase tracking-wider">
                Text Channels
              </span>
              <button
                onClick={() => setShowCreate(true)}
                className="text-muted hover:text-foreground transition-colors"
              >
                <Plus size={14} />
              </button>
            </div>
            {textChannels.map((channel) => (
              <ChannelItem
                key={channel.id}
                channel={channel}
                isActive={currentChannelId === channel.id}
                onSelect={setCurrentChannel}
                icon="text"
              />
            ))}
          </div>
        )}

        {voiceChannels.length > 0 && (
          <div>
            <span className="text-xs font-semibold text-muted uppercase tracking-wider px-2">
              Voice Channels
            </span>
            {voiceChannels.map((channel) => (
              <ChannelItem
                key={channel.id}
                channel={channel}
                isActive={currentChannelId === channel.id}
                onSelect={setCurrentChannel}
                icon="voice"
              />
            ))}
          </div>
        )}

        {showCreate && (
          <div className="px-2">
            <input
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleCreateChannel();
                if (e.key === "Escape") setShowCreate(false);
              }}
              placeholder="channel-name"
              autoFocus
              className="w-full bg-background border border-border rounded-md px-2 py-1.5 text-sm text-foreground placeholder:text-muted focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
        )}
      </div>
      )}
    </div>
  );
}
