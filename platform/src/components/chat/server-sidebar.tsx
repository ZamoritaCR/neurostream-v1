"use client";

import { useState } from "react";
import { useServerStore } from "@/stores/server-store";
import { Plus } from "lucide-react";

export function ServerSidebar() {
  const servers = useServerStore((s) => s.servers);
  const currentServerId = useServerStore((s) => s.currentServerId);
  const setCurrentServer = useServerStore((s) => s.setCurrentServer);
  const createServer = useServerStore((s) => s.createServer);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");

  const handleCreate = async () => {
    if (!newName.trim()) return;
    const server = await createServer(newName);
    if (server) {
      setCurrentServer(server.id);
    }
    setNewName("");
    setShowCreate(false);
  };

  return (
    <div className="w-[72px] bg-background border-r border-border flex flex-col items-center py-3 gap-2 h-full shrink-0">
      {servers.map((server) => (
        <button
          key={server.id}
          onClick={() => setCurrentServer(server.id)}
          className={`w-12 h-12 rounded-2xl flex items-center justify-center text-sm font-semibold transition-all ${
            currentServerId === server.id
              ? "bg-primary text-white rounded-xl"
              : "bg-surface text-muted hover:bg-surface-hover hover:text-foreground hover:rounded-xl"
          }`}
          title={server.name}
        >
          {server.name.charAt(0).toUpperCase()}
        </button>
      ))}

      {/* Divider */}
      <div className="w-8 h-px bg-border" />

      {/* Create server */}
      {showCreate ? (
        <input
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleCreate();
            if (e.key === "Escape") setShowCreate(false);
          }}
          placeholder="Name"
          autoFocus
          className="w-12 h-12 bg-surface border border-border rounded-2xl text-center text-xs text-foreground placeholder:text-muted focus:outline-none focus:ring-1 focus:ring-primary"
        />
      ) : (
        <button
          onClick={() => setShowCreate(true)}
          className="w-12 h-12 rounded-2xl bg-surface text-accent hover:bg-accent hover:text-white flex items-center justify-center transition-all hover:rounded-xl"
          title="Create Server"
        >
          <Plus size={20} />
        </button>
      )}
    </div>
  );
}
