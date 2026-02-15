"use client";

import { useEffect, useMemo, useState, useCallback } from "react";
import { useServerStore } from "@/stores/server-store";
import { useChatStore } from "@/stores/chat-store";
import { usePresenceStore } from "@/stores/presence-store";
import { useKeyboardShortcuts } from "@/hooks/use-keyboard-shortcuts";
import { MessageList } from "./message-list";
import { MessageInput } from "./message-input";
import { ChannelSidebar } from "./channel-sidebar";
import { ServerSidebar } from "./server-sidebar";
import { MemberList } from "./member-list";
import { PresenceSelector } from "./presence-selector";
import { QuickSwitcher } from "./quick-switcher";
import { ShortcutsModal } from "./shortcuts-modal";
import { Hash, Volume2 } from "lucide-react";

export function ChatView() {
  const currentServerId = useServerStore((s) => s.currentServerId);
  const currentChannelId = useServerStore((s) => s.currentChannelId);
  const channels = useServerStore((s) => s.channels);
  const fetchServers = useServerStore((s) => s.fetchServers);
  const setCurrentServer = useServerStore((s) => s.setCurrentServer);
  const setCurrentChannel = useServerStore((s) => s.setCurrentChannel);
  const servers = useServerStore((s) => s.servers);
  const fetchMessages = useChatStore((s) => s.fetchMessages);
  const subscribeToChannel = useChatStore((s) => s.subscribeToChannel);
  const unsubscribe = useChatStore((s) => s.unsubscribe);
  const config = usePresenceStore((s) => s.config);

  const [quickSwitcherOpen, setQuickSwitcherOpen] = useState(false);
  const [shortcutsOpen, setShortcutsOpen] = useState(false);

  const toggleQuickSwitcher = useCallback(
    () => setQuickSwitcherOpen((v) => !v),
    []
  );
  const toggleShortcuts = useCallback(
    () => setShortcutsOpen((v) => !v),
    []
  );

  useKeyboardShortcuts({
    onQuickSwitcher: toggleQuickSwitcher,
    onShowShortcuts: toggleShortcuts,
  });

  const currentChannel = useMemo(
    () => channels.find((c) => c.id === currentChannelId),
    [channels, currentChannelId]
  );

  // Load servers on mount
  useEffect(() => {
    fetchServers();
  }, [fetchServers]);

  // Auto-select first server and channel
  useEffect(() => {
    if (servers.length > 0 && !currentServerId) {
      setCurrentServer(servers[0].id);
    }
  }, [servers, currentServerId, setCurrentServer]);

  useEffect(() => {
    if (channels.length > 0 && !currentChannelId) {
      setCurrentChannel(channels[0].id);
    }
  }, [channels, currentChannelId, setCurrentChannel]);

  const isVoiceChannel = currentChannel?.channel_type === "voice";

  // Subscribe to channel messages (text only)
  useEffect(() => {
    if (!currentChannelId || isVoiceChannel) return;
    fetchMessages(currentChannelId);
    subscribeToChannel(currentChannelId);
    return () => unsubscribe();
  }, [currentChannelId, isVoiceChannel, fetchMessages, subscribeToChannel, unsubscribe]);

  return (
    <div className="flex h-screen bg-background">
      {/* Server sidebar - hide in hyperfocus */}
      {config.uiDensity !== "minimal" && <ServerSidebar />}

      {/* Channel sidebar with presence at bottom */}
      {config.uiDensity !== "minimal" && (
        <div className="flex flex-col h-full">
          <ChannelSidebar />
          <div className="bg-surface border-r border-border border-t border-t-border px-2 py-2 w-60">
            <PresenceSelector />
          </div>
        </div>
      )}

      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Channel header */}
        <div className="h-12 border-b border-border flex items-center px-4 shrink-0">
          {currentChannel ? (
            <div className="flex items-center gap-2">
              {isVoiceChannel ? (
                <Volume2 size={18} className="text-muted" />
              ) : (
                <Hash size={18} className="text-muted" />
              )}
              <span className="font-semibold text-sm text-foreground">
                {currentChannel.name}
              </span>
              {currentChannel.description && (
                <>
                  <div className="w-px h-4 bg-border mx-1" />
                  <span className="text-xs text-muted truncate">
                    {currentChannel.description}
                  </span>
                </>
              )}
            </div>
          ) : (
            <span className="text-sm text-muted">Select a channel</span>
          )}

          {/* Minimal mode: show presence inline */}
          {config.uiDensity === "minimal" && (
            <div className="ml-auto">
              <PresenceSelector />
            </div>
          )}
        </div>

        {/* Messages or Voice */}
        {currentChannelId && isVoiceChannel ? (
          <div className="flex-1 flex items-center justify-center">
            <span className="text-muted">Voice channels coming soon</span>
          </div>
        ) : currentChannelId ? (
          <>
            <MessageList />
            <MessageInput
              channelId={currentChannelId}
              channelName={currentChannel?.name || ""}
            />
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center space-y-2">
              <p className="text-lg text-muted">Welcome to Dopamine Chat</p>
              <p className="text-sm text-muted/60">
                {servers.length === 0
                  ? "Create a server to get started"
                  : "Select a channel to start chatting"}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Member list - hide in minimal/compact */}
      <MemberList />

      {/* Modals */}
      <QuickSwitcher
        open={quickSwitcherOpen}
        onClose={() => setQuickSwitcherOpen(false)}
      />
      <ShortcutsModal
        open={shortcutsOpen}
        onClose={() => setShortcutsOpen(false)}
      />
    </div>
  );
}
