"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/components/shared/AuthProvider";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

const navItems = [
  { href: "/admin", label: "Dashboard", icon: "~" },
  { href: "/admin/claude", label: "Talk to Claude", icon: "AI" },
  { href: "/admin/content", label: "Content Creator", icon: "C" },
  { href: "/admin/intelligence", label: "User Intelligence", icon: "I" },
  { href: "/admin/engagement", label: "Engagement", icon: "E" },
];

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
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
    <div className="min-h-screen bg-background flex">
      {/* Sidebar */}
      <aside className="w-64 bg-surface border-r border-border flex flex-col">
        <div className="p-6 border-b border-border">
          <Link href="/admin">
            <h1 className="text-xl font-bold">
              <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Admin Panel
              </span>
            </h1>
            <p className="text-xs text-muted mt-1">dopamine.watch agents</p>
          </Link>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => {
            const isActive =
              pathname === item.href ||
              (item.href !== "/admin" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-primary/20 text-primary"
                    : "text-muted hover:text-foreground hover:bg-surface-hover"
                }`}
              >
                <span className="w-8 h-8 bg-surface-hover rounded-lg flex items-center justify-center text-xs font-bold">
                  {item.icon}
                </span>
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-border">
          <div className="text-xs text-muted">
            <p>Signed in as</p>
            <p className="text-foreground truncate">{user.email}</p>
          </div>
          <Link
            href="/"
            className="mt-3 block text-xs text-primary hover:text-primary-hover"
          >
            &larr; Back to App
          </Link>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">{children}</main>
    </div>
  );
}
