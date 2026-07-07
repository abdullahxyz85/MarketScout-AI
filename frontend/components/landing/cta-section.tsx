'use client';

import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, Zap } from 'lucide-react';
import Link from 'next/link';
import { AnimatedButton } from '@/components/ui/animated-button';

export function CTASection() {
  return (
    <section className="py-32 relative overflow-hidden">
      {/* Full-width gradient backdrop */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-indigo-900/20 to-transparent" />
        <motion.div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] rounded-full bg-indigo-600/20 blur-3xl"
          animate={{ scale: [1, 1.15, 1] }}
          transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[300px] rounded-full bg-purple-600/15 blur-3xl"
          animate={{ scale: [1.1, 1, 1.1] }}
          transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' }}
        />
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="text-center"
        >
          <motion.div
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.06] border border-white/[0.1] text-white/70 text-sm mb-8"
            whileHover={{ scale: 1.03 }}
          >
            <Zap className="w-4 h-4 text-indigo-400" />
            Start in 60 seconds
          </motion.div>

          <h2 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold text-white mb-6 leading-tight">
            Ready to Validate Your
            <br />
            <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
              Next Big Idea?
            </span>
          </h2>

          <p className="text-lg sm:text-xl text-white/45 max-w-2xl mx-auto mb-12">
            Join thousands of founders using AI-powered market intelligence to
            make data-driven decisions and reduce risk.
          </p>

          <div className="flex flex-wrap gap-4 justify-center mb-8">
            <Link href="/signup">
              <AnimatedButton size="lg" className="min-w-48">
                Start Free Research
                <ArrowRight className="w-5 h-5" />
              </AnimatedButton>
            </Link>
            <Link href="/login">
              <AnimatedButton variant="secondary" size="lg" className="min-w-36">
                Sign In
              </AnimatedButton>
            </Link>
          </div>

          <p className="text-sm text-white/30">No credit card required • Free to start • Cancel anytime</p>
        </motion.div>
      </div>
    </section>
  );
}
