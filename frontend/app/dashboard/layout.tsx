'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import {
  LayoutDashboard,
  Search,
  Users,
  FileText,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Menu,
  X,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Logo } from '@/components/ui/logo';
import { AnimatedBackground } from '@/components/landing/animated-background';
import { ResearchProvider, useResearch } from '@/lib/research-context';

const sidebarItems = [
  { icon: LayoutDashboard, label: 'Dashboard', href: '/dashboard' },
  { icon: Search, label: 'New Research', href: '/dashboard/research' },
  { icon: Users, label: 'Competitors', href: '/dashboard/competitors' },
  { icon: FileText, label: 'Reports', href: '/dashboard/reports' },
  { icon: Settings, label: 'Settings', href: '/dashboard/settings' },
];

type CurrentUser = {
  id: string;
  email: string;
  name: string | null;
  picture: string | null;
};

function SidebarContent({
  mobile = false,
  collapsed,
  isActive,
  onToggleCollapsed,
  onCloseMobile,
  onLogout,
}: {
  mobile?: boolean;
  collapsed: boolean;
  isActive: (href: string) => boolean;
  onToggleCollapsed: () => void;
  onCloseMobile: () => void;
  onLogout: () => void;
}) {
  return (
    <>
      <div className={cn(
        'flex items-center border-b border-white/10 transition-all duration-300',
        mobile ? 'p-4 gap-3' : collapsed ? 'p-4 justify-center' : 'p-4 justify-between'
      )}>
        {(!collapsed || mobile) && (
          <Link href="/" className="min-w-0">
            <Logo size={28} />
          </Link>
        )}
        {collapsed && !mobile && (
          <Link href="/">
            <Logo variant="icon" size={28} />
          </Link>
        )}
        {!mobile && (
          <button
            onClick={onToggleCollapsed}
            className="p-2 rounded-lg hover:bg-white/5 text-white/40 hover:text-white transition-colors flex-shrink-0"
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        )}
        {mobile && (
          <button onClick={onCloseMobile} className="p-1.5 rounded-lg hover:bg-white/5 text-white/40 hover:text-white ml-auto">
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
              onClick={onCloseMobile}
              className={cn(
                'flex items-center gap-3 rounded-xl transition-all duration-200 group relative',
                collapsed && !mobile ? 'px-2 py-3 justify-center' : 'px-3 py-2.5',
                active
                  ? 'bg-indigo-500/20 text-white border border-indigo-500/30'
                  : 'text-white/50 hover:text-white hover:bg-white/5'
              )}
            >
              {active && (
                <motion.div
                  layoutId={mobile ? 'active-mobile' : 'active-indicator'}
                  className="absolute inset-0 rounded-xl bg-indigo-500/10 border border-indigo-500/20"
                  transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                />
              )}
              <div className={cn('relative z-10 flex items-center gap-3', collapsed && !mobile ? '' : 'w-full')}>
                <item.icon className={cn('flex-shrink-0', collapsed && !mobile ? 'w-5 h-5' : 'w-4 h-4')} />
                {(!collapsed || mobile) && (
                  <span className="text-sm font-medium whitespace-nowrap">{item.label}</span>
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
          onClick={onLogout}
          className={cn(
            'flex items-center gap-3 rounded-xl text-white/40 hover:text-white hover:bg-white/5 transition-all w-full',
            collapsed && !mobile ? 'px-2 py-3 justify-center' : 'px-3 py-2.5'
          )}
        >
          <LogOut className="w-4 h-4 flex-shrink-0" />
          {(!collapsed || mobile) && <span className="text-sm font-medium">Log out</span>}
        </button>
      </div>
    </>
  );
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <ResearchProvider>
      <DashboardLayoutInner>{children}</DashboardLayoutInner>
    </ResearchProvider>
  );
}

function DashboardLayoutInner({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [user, setUser] = useState<CurrentUser | null>(null);
  const pathname = usePathname();
  const router = useRouter();
  const { stage, progress, activeAgentName } = useResearch();
  const showResearchBadge = stage === 'running' && pathname !== '/dashboard/research';

  useEffect(() => {
    fetch('/api/users/me', { credentials: 'include' })
      .then((res) => {
        if (!res.ok) throw new Error('unauthenticated');
        return res.json();
      })
      .then((data) =>
        setUser({ id: data.id, email: data.email, name: data.display_name, picture: data.avatar_url })
      )
      .catch(() => router.replace('/login'));
  }, [router]);

  const handleLogout = async () => {
    await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
    router.replace('/login');
  };

  const initials = (user?.name || user?.email || '?')
    .trim()
    .split(/\s+/)
    .map((p) => p[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  const isActive = (href: string) =>
    href === '/dashboard' ? pathname === '/dashboard' : pathname.startsWith(href);

  return (
    <div className="min-h-screen bg-[#050508]">
      <AnimatedBackground />
      <div className="flex h-screen overflow-hidden">
        {/* Desktop Sidebar */}
        <motion.aside
          animate={{ width: collapsed ? 64 : 240 }}
          transition={{ type: 'spring', stiffness: 400, damping: 35 }}
          className="hidden lg:flex flex-col border-r border-white/[0.06] bg-black/40 backdrop-blur-2xl overflow-hidden flex-shrink-0"
        >
          <SidebarContent
            collapsed={collapsed}
            isActive={isActive}
            onToggleCollapsed={() => setCollapsed((c) => !c)}
            onCloseMobile={() => setMobileOpen(false)}
            onLogout={handleLogout}
          />
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
                transition={{ type: 'spring', stiffness: 400, damping: 35 }}
                className="lg:hidden fixed left-0 top-0 bottom-0 w-60 flex flex-col bg-black/95 backdrop-blur-2xl z-50 border-r border-white/10"
              >
                <SidebarContent
                  mobile
                  collapsed={collapsed}
                  isActive={isActive}
                  onToggleCollapsed={() => setCollapsed((c) => !c)}
                  onCloseMobile={() => setMobileOpen(false)}
                  onLogout={handleLogout}
                />
              </motion.div>
            </>
          )}
        </AnimatePresence>

        {/* Main */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <header className="h-14 border-b border-white/[0.06] bg-black/30 backdrop-blur-2xl flex items-center justify-between px-4 lg:px-6 flex-shrink-0">
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

            <div className="flex items-center gap-3">
              {showResearchBadge && (
                <Link
                  href="/dashboard/research"
                  className="hidden sm:flex items-center gap-2 pl-2.5 pr-3 py-1.5 rounded-full bg-indigo-500/15 border border-indigo-500/30 hover:bg-indigo-500/25 transition-colors"
                >
                  <span className="relative flex w-2 h-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75" />
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-400" />
                  </span>
                  <span className="text-xs text-indigo-200 font-medium">
                    Research running{activeAgentName ? ` · ${activeAgentName}` : ''} · {progress}%
                  </span>
                </Link>
              )}
              <div className="flex items-center gap-1.5">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white text-xs font-bold cursor-pointer shadow-glow ml-1 overflow-hidden">
                  {user?.picture ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={user.picture} alt={user.name ?? user.email} className="w-full h-full object-cover" />
                  ) : (
                    initials
                  )}
                </div>
              </div>
            </div>
          </header>

          <main className="flex-1 overflow-auto p-4 lg:p-6">{children}</main>
        </div>
      </div>
    </div>
  );
}
