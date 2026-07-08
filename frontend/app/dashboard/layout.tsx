"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Search,
  Users,
  FileText,
  Settings,
  HeartPulse,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Bell,
  Moon,
  Menu,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { AnimatedBackground } from "@/components/landing/animated-background";
import { Logo } from "@/components/ui/logo";

type CurrentUser = {
  id: string;
  email: string;
  display_name: string | null;
  avatar_url: string | null;
};

const sidebarItems = [
  { icon: LayoutDashboard, label: "Dashboard", href: "/dashboard" },
  { icon: Search, label: "New Research", href: "/dashboard/research" },
  { icon: HeartPulse, label: "Healthcare Mode", href: "/dashboard/healthcare" },
  { icon: Users, label: "Competitors", href: "/dashboard/competitors" },
  { icon: FileText, label: "Reports", href: "/dashboard/reports" },
  { icon: Settings, label: "Settings", href: "/dashboard/settings" },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [user, setUser] = useState<CurrentUser | null>(null);
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    let cancelled = false;
    fetch("/api/users/me", { credentials: "include" })
      .then((res) => {
        if (!res.ok) throw new Error("unauthenticated");
        return res.json();
      })
      .then((data) => {
        if (!cancelled) setUser(data);
      })
      .catch(() => {
        if (!cancelled) router.replace("/login");
      });
    return () => {
      cancelled = true;
    };
  }, [router]);

  const handleLogout = async () => {
    await fetch("/api/auth/logout", { method: "POST", credentials: "include" });
    router.replace("/login");
  };

  const initials = user?.display_name
    ? user.display_name
        .split(" ")
        .map((part) => part[0])
        .slice(0, 2)
        .join("")
        .toUpperCase()
    : (user?.email?.[0] ?? "").toUpperCase();

  const isActive = (href: string) =>
    href === "/dashboard"
      ? pathname === "/dashboard"
      : pathname.startsWith(href);

  const SidebarContent = ({ mobile = false }: { mobile?: boolean }) => (
    <>
      <div
        className={cn(
          "flex items-center border-b border-white/10 transition-all duration-300",
          mobile
            ? "p-4 gap-3"
            : collapsed
              ? "p-4 justify-center"
              : "p-4 gap-3 justify-between",
        )}
      >
        {(!collapsed || mobile) && (
          <Link href="/" className="flex items-center min-w-0">
            <Logo size={28} className="[&_[data-slot=wordmark]]:text-base" />
          </Link>
        )}
        {collapsed && !mobile && (
          <Link href="/">
            <Logo variant="icon" size={28} />
          </Link>
        )}
        {!mobile && (
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1.5 rounded-lg hover:bg-white/5 text-white/40 hover:text-white transition-colors flex-shrink-0"
          >
            {collapsed ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <ChevronLeft className="w-4 h-4" />
            )}
          </button>
        )}
        {mobile && (
          <button
            onClick={() => setMobileOpen(false)}
            className="p-1.5 rounded-lg hover:bg-white/5 text-white/40 hover:text-white ml-auto"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      <nav className="flex-1 p-3 space-y-0.5 overflow-y-auto">
        {sidebarItems.map((item) => {
          const active = isActive(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setMobileOpen(false)}
              className={cn(
                "flex items-center gap-3 rounded-xl transition-all duration-200 group relative",
                collapsed && !mobile
                  ? "px-2 py-3 justify-center"
                  : "px-3 py-2.5",
                active
                  ? "bg-indigo-500/20 text-white border border-indigo-500/30"
                  : "text-white/50 hover:text-white hover:bg-white/5",
              )}
            >
              {active && (
                <motion.div
                  layoutId={mobile ? "active-mobile" : "active-indicator"}
                  className="absolute inset-0 rounded-xl bg-indigo-500/10 border border-indigo-500/20"
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                />
              )}
              <div
                className={cn(
                  "relative z-10 flex items-center gap-3",
                  collapsed && !mobile ? "" : "w-full",
                )}
              >
                <item.icon
                  className={cn(
                    "flex-shrink-0",
                    collapsed && !mobile ? "w-5 h-5" : "w-4 h-4",
                  )}
                />
                {(!collapsed || mobile) && (
                  <span className="text-sm font-medium whitespace-nowrap">
                    {item.label}
                  </span>
                )}
                {active && !collapsed && !mobile && (
                  <div className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-400" />
                )}
              </div>
            </Link>
          );
        })}
      </nav>

      <div className="p-3 border-t border-white/10">
        <button
          onClick={handleLogout}
          className={cn(
            "w-full flex items-center gap-3 rounded-xl text-white/40 hover:text-white hover:bg-white/5 transition-all",
            collapsed && !mobile ? "px-2 py-3 justify-center" : "px-3 py-2.5",
          )}
        >
          <LogOut className="w-4 h-4 flex-shrink-0" />
          {(!collapsed || mobile) && (
            <span className="text-sm font-medium">Log out</span>
          )}
        </button>
      </div>
    </>
  );

  return (
    <div className="min-h-screen relative">
      <AnimatedBackground />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_18%_12%,rgba(99,102,241,0.18),transparent_36%),radial-gradient(circle_at_86%_76%,rgba(6,182,212,0.14),transparent_34%)]" />
      <div className="relative flex h-screen overflow-hidden">
        {/* Desktop Sidebar */}
        <motion.aside
          animate={{ width: collapsed ? 64 : 240 }}
          transition={{ type: "spring", stiffness: 400, damping: 35 }}
          className="hidden lg:flex flex-col border-r border-white/[0.06] bg-gradient-to-b from-black/20 via-black/10 to-transparent backdrop-blur-3xl overflow-hidden flex-shrink-0"
        >
          <SidebarContent />
        </motion.aside>

        {/* Mobile Sidebar */}
        <AnimatePresence>
          {mobileOpen && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
                onClick={() => setMobileOpen(false)}
              />
              <motion.div
                initial={{ x: -240 }}
                animate={{ x: 0 }}
                exit={{ x: -240 }}
                transition={{ type: "spring", stiffness: 400, damping: 35 }}
                className="lg:hidden fixed left-0 top-0 bottom-0 w-60 flex flex-col bg-gradient-to-b from-black/85 to-black/65 backdrop-blur-3xl z-50 border-r border-white/10"
              >
                <SidebarContent mobile />
              </motion.div>
            </>
          )}
        </AnimatePresence>

        {/* Main */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <header className="h-14 border-b border-white/[0.06] bg-gradient-to-r from-black/20 via-black/10 to-transparent backdrop-blur-3xl flex items-center justify-between px-4 lg:px-6 flex-shrink-0">
            <div className="flex items-center gap-3">
              <button
                className="lg:hidden p-2 rounded-lg hover:bg-white/5 text-white/50 hover:text-white transition-colors"
                onClick={() => setMobileOpen(true)}
              >
                <Menu className="w-5 h-5" />
              </button>
              <div className="relative hidden sm:block">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                <input
                  type="text"
                  placeholder="Search anything..."
                  className="pl-9 pr-4 py-2 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white text-sm placeholder:text-white/25 focus:outline-none focus:border-indigo-500/40 w-56 transition-colors"
                />
              </div>
            </div>

            <div className="flex items-center gap-1.5">
              {user?.avatar_url ? (
                <img
                  src={user.avatar_url}
                  alt={user.display_name ?? user.email}
                  className="w-8 h-8 rounded-full object-cover cursor-pointer shadow-glow ml-1"
                />
              ) : (
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white text-xs font-bold cursor-pointer shadow-glow ml-1">
                  {initials || "?"}
                </div>
              )}
            </div>
          </header>

          <main className="flex-1 overflow-auto p-4 lg:p-6">
            <div className="min-h-full rounded-3xl border border-white/[0.08] bg-gradient-to-br from-white/[0.05] via-white/[0.03] to-transparent backdrop-blur-2xl shadow-2xl shadow-black/20 p-4 lg:p-6 relative overflow-hidden">
              <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_18%_12%,rgba(99,102,241,0.08),transparent_34%),radial-gradient(circle_at_82%_78%,rgba(6,182,212,0.06),transparent_30%)]" />
              <div className="relative">{children}</div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
