'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { Github } from 'lucide-react';
import { AnimatedBackground } from '@/components/landing/animated-background';
import { Logo } from '@/components/ui/logo';
import { GoogleIcon } from '@/components/ui/google-icon';

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
            <motion.div whileHover={{ scale: 1.05 }}>
              <Logo size={36} className="[&_[data-slot=wordmark]]:text-2xl" />
            </motion.div>
          </Link>
          <p className="text-white/50 mt-2 text-sm">Sign in to your account</p>
        </div>

        {/* Card */}
        <div className="relative rounded-3xl overflow-hidden backdrop-blur-2xl border border-white/10 bg-gradient-to-br from-white/[0.08] to-white/[0.02] shadow-2xl">
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 via-transparent to-purple-500/5 pointer-events-none" />

          <div className="relative p-8">
            {/* Social login */}
            <div className="space-y-3">
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
                <GoogleIcon className="w-5 h-5" />
                Continue with Google
              </motion.a>
            </div>
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
