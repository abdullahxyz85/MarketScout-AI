'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { Github } from 'lucide-react';
import { AnimatedBackground } from '@/components/landing/animated-background';
import { Logo } from '@/components/ui/logo';

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative">
      <AnimatedBackground />

      {/* Glow orbs behind card */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-96 h-96 rounded-full bg-indigo-500/20 blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 40, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className="w-full max-w-md relative z-10"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center group">
            <Logo size={40} />
          </Link>
          <p className="text-white/50 mt-2 text-sm">Sign in to your account</p>
        </div>

        {/* Card */}
        <div className="relative rounded-3xl overflow-hidden backdrop-blur-2xl border border-white/10 bg-gradient-to-br from-white/[0.08] to-white/[0.02] shadow-2xl">
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 via-transparent to-purple-500/5 pointer-events-none" />

          <div className="relative p-8 space-y-3">
            <motion.a
              href="/api/auth/github/login"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full flex items-center justify-center gap-3 py-3 rounded-xl bg-white/5 border border-white/10 text-white/80 hover:bg-white/10 hover:text-white transition-all text-sm font-medium"
            >
              <Github className="w-5 h-5" />
              Continue with GitHub
            </motion.a>

            <motion.a
              href="/api/auth/google/login"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full flex items-center justify-center gap-3 py-3 rounded-xl bg-white/5 border border-white/10 text-white/80 hover:bg-white/10 hover:text-white transition-all text-sm font-medium"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.99.66-2.26 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.85A11 11 0 0 0 12 23z" />
                <path fill="#FBBC05" d="M5.84 14.1a6.6 6.6 0 0 1 0-4.2V7.05H2.18a11 11 0 0 0 0 9.9z" />
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1a11 11 0 0 0-9.82 6.05l3.66 2.85c.87-2.6 3.3-4.52 6.16-4.52z" />
              </svg>
              Continue with Google
            </motion.a>
          </div>
        </div>

        {/* Bottom trust */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="text-center text-xs text-white/25 mt-6"
        >
          Secured with enterprise-grade encryption
        </motion.p>
      </motion.div>
    </div>
  );
}
