import { useEffect } from "react";

interface ShortcutHandlers {
  onQuickSwitcher?: () => void;
  onShowShortcuts?: () => void;
}

export function useKeyboardShortcuts({ onQuickSwitcher, onShowShortcuts }: ShortcutHandlers) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger when typing in inputs/textareas
      const target = e.target as HTMLElement;
      if (target.tagName === "INPUT" || target.tagName === "TEXTAREA") return;

      // Cmd/Ctrl + K: Quick channel switcher
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        onQuickSwitcher?.();
      }

      // Cmd/Ctrl + /: Show shortcuts help
      if ((e.metaKey || e.ctrlKey) && e.key === "/") {
        e.preventDefault();
        onShowShortcuts?.();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onQuickSwitcher, onShowShortcuts]);
}
