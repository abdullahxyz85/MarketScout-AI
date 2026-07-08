'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X, LogOut } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { AnimatedButton } from '@/components/ui/animated-button';
import { Logo } from '@/components/ui/logo';
import { cn } from '@/lib/utils';

type CurrentUser = {
  id: string;
  email: string;
  display_name: string | null;
  avatar_url: string | null;
};

const baseNavLinks = [
  { href: '#features', label: 'Features' },
  { href: '#agents', label: 'Agents' },
  { href: '#workflow', label: 'How It Works' },
];

export function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [authChecked, setAuthChecked] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    let cancelled = false;
    fetch('/api/users/me', { credentials: 'include' })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (!cancelled) setUser(data);
      })
      .finally(() => {
        if (!cancelled) setAuthChecked(true);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const handleDashboardClick = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsMobileMenuOpen(false);
    router.push(authChecked && !user ? '/login' : '/dashboard');
  };

  const handleLogout = async () => {
    await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
    setUser(null);
    router.push('/');
  };

  const initials = user?.display_name
    ? user.display_name.split(' ').map((p) => p[0]).slice(0, 2).join('').toUpperCase()
    : (user?.email?.[0] ?? '').toUpperCase();

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className={cn(
        'fixed top-0 left-0 right-0 z-50 transition-all duration-500',
        isScrolled
          ? 'h-14 bg-[#030306]/80 backdrop-blur-2xl border-b border-white/[0.06]'
          : 'h-20 bg-transparent'
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-full flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center group">
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Logo size={28} className="text-white" />
          </motion.div>
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-0.5">
          {baseNavLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="px-4 py-2 text-sm text-white/55 hover:text-white transition-colors rounded-lg hover:bg-white/[0.05]"
            >
              {link.label}
            </Link>
          ))}
          <a
            href="/dashboard"
            onClick={handleDashboardClick}
            className="px-4 py-2 text-sm text-white/55 hover:text-white transition-colors rounded-lg hover:bg-white/[0.05]"
          >
            Dashboard
          </a>
        </nav>

        {/* CTA */}
        <div className="hidden md:flex items-center gap-3">
          {user ? (
            <>
              {user.avatar_url ? (
                <img
                  src={user.avatar_url}
                  alt={user.display_name ?? user.email}
                  className="w-8 h-8 rounded-full object-cover"
                />
              ) : (
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white text-xs font-bold">
                  {initials || '?'}
                </div>
              )}
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm text-white/60 hover:text-white transition-colors rounded-lg hover:bg-white/[0.05] flex items-center gap-1.5"
              >
                <LogOut className="w-4 h-4" />
                Log out
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="px-4 py-2 text-sm text-white/60 hover:text-white transition-colors rounded-lg hover:bg-white/[0.05]">
                Login
              </Link>
              <Link href="/signup">
                <AnimatedButton size="sm">Get Started Free</AnimatedButton>
              </Link>
            </>
          )}
        </div>

        {/* Mobile hamburger */}
        <button
          className="md:hidden p-2 text-white/60 hover:text-white transition-colors"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        >
          {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-[#030306]/95 backdrop-blur-2xl border-t border-white/[0.06]"
          >
            <div className="px-4 py-4 space-y-1">
              {baseNavLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="block px-4 py-2.5 text-white/70 hover:text-white hover:bg-white/[0.05] rounded-xl transition-colors text-sm"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {link.label}
                </Link>
              ))}
              <a
                href="/dashboard"
                onClick={handleDashboardClick}
                className="block px-4 py-2.5 text-white/70 hover:text-white hover:bg-white/[0.05] rounded-xl transition-colors text-sm"
              >
                Dashboard
              </a>
              <div className="pt-3 border-t border-white/[0.08] flex flex-col gap-2">
                {user ? (
                  <>
                    <div className="flex items-center gap-2 px-4 py-2">
                      {user.avatar_url ? (
                        <img
                          src={user.avatar_url}
                          alt={user.display_name ?? user.email}
                          className="w-7 h-7 rounded-full object-cover"
                        />
                      ) : (
                        <div className="w-7 h-7 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white text-xs font-bold">
                          {initials || '?'}
                        </div>
                      )}
                      <span className="text-sm text-white/70">{user.display_name ?? user.email}</span>
                    </div>
                    <button
                      onClick={() => {
                        setIsMobileMenuOpen(false);
                        handleLogout();
                      }}
                      className="px-4 py-2.5 text-white/70 hover:text-white text-sm text-center flex items-center justify-center gap-1.5"
                    >
                      <LogOut className="w-4 h-4" />
                      Log out
                    </button>
                  </>
                ) : (
                  <>
                    <Link href="/login" className="px-4 py-2.5 text-white/70 hover:text-white text-sm text-center" onClick={() => setIsMobileMenuOpen(false)}>
                      Login
                    </Link>
                    <Link href="/signup" onClick={() => setIsMobileMenuOpen(false)}>
                      <AnimatedButton size="sm" className="w-full">Get Started Free</AnimatedButton>
                    </Link>
                  </>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
}
