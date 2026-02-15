"use client";

import { useAuth } from "@/components/shared/AuthProvider";
import Link from "next/link";
import { usePathname } from "next/navigation";

export function Navigation() {
  const { user, signOut } = useAuth();
  const pathname = usePathname();

  // Don't show navigation on auth page
  if (pathname === "/auth") return null;

  const ADMIN_EMAILS = ["johan@focuschat.com", "johanzamora@gmail.com"];
  const isAdmin = user?.email && ADMIN_EMAILS.includes(user.email);

  const navLinks = [
    { href: "/watch", label: "Discover" },
    { href: "/chat", label: "Chat" },
    { href: "/food", label: "Meal Planner" },
    { href: "/blog", label: "Blog" },
  ];

  const isActive = (href: string) => pathname === href;

  return (
    <nav className="sticky top-0 z-50 bg-background/80 backdrop-blur-lg border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center">
              <div className="w-4 h-4 bg-white/90 rounded-full" />
            </div>
            <span className="font-bold text-lg bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              dopamine.watch
            </span>
          </Link>

          {/* Main Navigation */}
          {user && (
            <div className="hidden md:flex items-center gap-1">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive(link.href)
                      ? "bg-primary/10 text-primary"
                      : "text-muted hover:text-foreground hover:bg-surface"
                  }`}
                >
                  {link.label}
                </Link>
              ))}
            </div>
          )}

          {/* Right Side Actions */}
          <div className="flex items-center gap-3">
            {user ? (
              <>
                {/* Admin Link (only for admin email) */}
                {isAdmin && (
                  <Link
                    href="/admin"
                    className="hidden md:block px-3 py-1.5 text-xs font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/30 rounded-lg hover:bg-purple-500/20 transition-colors"
                  >
                    Admin
                  </Link>
                )}

                {/* User Menu */}
                <div className="flex items-center gap-3">
                  <span className="hidden sm:block text-sm text-muted">
                    {user.email}
                  </span>
                  <button
                    onClick={() => signOut()}
                    className="px-4 py-2 text-sm font-medium text-muted hover:text-foreground transition-colors"
                  >
                    Sign Out
                  </button>
                </div>
              </>
            ) : (
              <Link
                href="/auth"
                className="px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded-lg text-sm font-semibold transition-colors"
              >
                Sign In
              </Link>
            )}
          </div>
        </div>

        {/* Mobile Navigation */}
        {user && (
          <div className="md:hidden pb-3 flex gap-2 overflow-x-auto">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                  isActive(link.href)
                    ? "bg-primary/10 text-primary"
                    : "text-muted hover:text-foreground hover:bg-surface"
                }`}
              >
                {link.label}
              </Link>
            ))}
            {isAdmin && (
              <Link
                href="/admin"
                className="px-4 py-2 text-sm font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/30 rounded-lg hover:bg-purple-500/20 transition-colors whitespace-nowrap"
              >
                Admin
              </Link>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
