'use client';

import { motion } from 'framer-motion';
import { ArrowRight, Play, Zap, BarChart3, Users, TrendingUp, Activity, CheckCircle2, Brain } from 'lucide-react';
import { AnimatedButton } from '@/components/ui/animated-button';
import { AnimatedBadge } from '@/components/ui/animated-badge';
import Link from 'next/link';

export function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center justify-center pt-20 pb-24 px-4 overflow-hidden">
      {/* Extra hero glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[900px] h-[500px] bg-indigo-600/10 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute top-20 left-1/4 w-72 h-72 bg-purple-500/15 blur-[100px] rounded-full pointer-events-none" />
      <div className="absolute top-40 right-1/4 w-64 h-64 bg-cyan-500/10 blur-[80px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto w-full">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
            className="space-y-8 text-center lg:text-left"
          >
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
              className="inline-flex items-center gap-2"
            >
              <AnimatedBadge variant="gradient">
                <Brain className="w-3 h-3" />
                Multi-Agent AI Platform
              </AnimatedBadge>
            </motion.div>

            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold leading-[1.05] tracking-tight">
              <motion.span
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="block text-white"
              >
                Autonomous AI
              </motion.span>
              <motion.span
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="block text-gradient bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent"
              >
                Market Intelligence
              </motion.span>
              <motion.span
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="block text-white"
              >
                Platform
              </motion.span>
            </h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.45 }}
              className="text-lg sm:text-xl text-white/55 max-w-xl mx-auto lg:mx-0 leading-relaxed"
            >
              Transform any startup idea into a complete market intelligence report using
              autonomous AI agents. Get insights in{' '}
              <span className="text-white/80 font-medium">minutes, not months.</span>
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.55 }}
              className="flex flex-wrap gap-4 justify-center lg:justify-start"
            >
              <Link href="/dashboard">
                <AnimatedButton size="lg" className="relative overflow-hidden group">
                  <span className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/10 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
                  Start Research
                  <ArrowRight className="w-5 h-5" />
                </AnimatedButton>
              </Link>
              <AnimatedButton variant="secondary" size="lg">
                <Play className="w-4 h-4 fill-current" />
                Watch Demo
              </AnimatedButton>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7 }}
              className="pt-4 border-t border-white/[0.08]"
            >
              <p className="text-xs text-white/35 mb-3 uppercase tracking-widest">Powered by</p>
              <div className="flex flex-wrap gap-3 items-center justify-center lg:justify-start">
                {['AMD Cloud', 'Fireworks AI', 'Llama', 'Qwen'].map((partner, i) => (
                  <motion.div
                    key={partner}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.7 + i * 0.08 }}
                    className="px-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white/50 text-xs font-medium hover:text-white/80 hover:bg-white/[0.07] transition-colors"
                  >
                    {partner}
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </motion.div>

          {/* Right - 3D Dashboard */}
          <motion.div
            initial={{ opacity: 0, x: 60, rotateY: 10 }}
            animate={{ opacity: 1, x: 0, rotateY: 0 }}
            transition={{ duration: 1, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
            className="relative perspective-1000"
          >
            <HeroDashboard />
          </motion.div>
        </div>

        {/* Stats Row */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
          className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-20 pt-12 border-t border-white/[0.06]"
        >
          {[
            { value: '10,000+', label: 'Reports Generated' },
            { value: '98%', label: 'Accuracy Rate' },
            { value: '9', label: 'AI Agents' },
            { value: '<15min', label: 'Average Time' },
          ].map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.95 + i * 0.08 }}
              className="text-center"
            >
              <div className="text-3xl font-bold text-gradient mb-1">{stat.value}</div>
              <div className="text-sm text-white/40">{stat.label}</div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

function HeroDashboard() {
  return (
    <div className="relative">
      {/* Glow behind card */}
      <div className="absolute -inset-8 bg-gradient-to-r from-indigo-500/20 via-purple-500/25 to-cyan-500/20 rounded-3xl blur-3xl" />

      {/* Floating elements */}
      <motion.div
        className="absolute -top-6 -left-6 z-20 px-4 py-2.5 rounded-2xl bg-black/60 backdrop-blur-xl border border-white/10 shadow-xl"
        animate={{ y: [0, -8, 0] }}
        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
      >
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
            <CheckCircle2 className="w-4 h-4 text-white" />
          </div>
          <div>
            <div className="text-xs font-semibold text-white">Research Complete</div>
            <div className="text-xs text-emerald-400">Score: 94.2</div>
          </div>
        </div>
      </motion.div>

      <motion.div
        className="absolute -bottom-6 -right-4 z-20 px-4 py-2.5 rounded-2xl bg-black/60 backdrop-blur-xl border border-white/10 shadow-xl"
        animate={{ y: [0, 8, 0] }}
        transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
      >
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
            <Zap className="w-4 h-4 text-white" />
          </div>
          <div>
            <div className="text-xs font-semibold text-white">8 Agents Running</div>
            <div className="text-xs text-indigo-400">78% Complete</div>
          </div>
        </div>
      </motion.div>

      {/* Main card */}
      <motion.div
        className="relative rounded-3xl overflow-hidden backdrop-blur-xl border border-white/[0.1] bg-gradient-to-br from-white/[0.07] to-white/[0.02] shadow-2xl"
        whileHover={{ scale: 1.01 }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      >
        {/* Browser chrome */}
        <div className="flex items-center gap-2 px-5 py-3 border-b border-white/[0.06] bg-white/[0.02]">
          <div className="w-3 h-3 rounded-full bg-white/10" />
          <div className="w-3 h-3 rounded-full bg-white/10" />
          <div className="w-3 h-3 rounded-full bg-white/10" />
          <div className="flex-1 mx-4 h-6 rounded-lg bg-white/5 border border-white/[0.08] flex items-center px-3">
            <span className="text-xs text-white/30">app.marketscout.ai/dashboard</span>
          </div>
        </div>

        <div className="p-5 space-y-4">
          {/* Score ring */}
          <div className="flex items-center gap-5 p-4 rounded-2xl bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-cyan-500/10 border border-white/[0.07]">
            <div className="relative w-20 h-20 flex-shrink-0">
              <svg className="w-20 h-20 -rotate-90" viewBox="0 0 80 80">
                <circle cx="40" cy="40" r="32" stroke="rgba(255,255,255,0.05)" strokeWidth="8" fill="none" />
                <motion.circle
                  cx="40" cy="40" r="32"
                  stroke="url(#scoreGrad)"
                  strokeWidth="8"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray={201}
                  initial={{ strokeDashoffset: 201 }}
                  animate={{ strokeDashoffset: 201 * (1 - 0.942) }}
                  transition={{ duration: 2, delay: 0.5, ease: 'easeOut' }}
                />
                <defs>
                  <linearGradient id="scoreGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#6366f1" />
                    <stop offset="100%" stopColor="#06b6d4" />
                  </linearGradient>
                </defs>
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-xl font-bold text-white">94</span>
                <span className="text-xs text-white/40">Score</span>
              </div>
            </div>
            <div className="flex-1">
              <div className="text-base font-bold text-white mb-1">Healthcare AI Platform</div>
              <div className="text-xs text-white/50 mb-3">Market research complete</div>
              <div className="flex gap-2 flex-wrap">
                <span className="px-2 py-0.5 rounded-full bg-emerald-500/15 border border-emerald-500/25 text-xs text-emerald-400">Low Risk</span>
                <span className="px-2 py-0.5 rounded-full bg-indigo-500/15 border border-indigo-500/25 text-xs text-indigo-400">High Opp.</span>
              </div>
            </div>
          </div>

          {/* Metrics grid */}
          <div className="grid grid-cols-2 gap-3">
            <MetricCard
              icon={<BarChart3 className="w-4 h-4 text-emerald-400" />}
              label="Market Score"
              value="94.2"
              change="+12.4%"
              color="emerald"
            />
            <MetricCard
              icon={<TrendingUp className="w-4 h-4 text-indigo-400" />}
              label="Opportunity"
              value="87.8"
              change="+8.2%"
              color="indigo"
            />
            <MetricCard
              icon={<Users className="w-4 h-4 text-purple-400" />}
              label="Competitors"
              value="24"
              change="Analyzed"
              color="purple"
            />
            <MetricCard
              icon={<Activity className="w-4 h-4 text-cyan-400" />}
              label="Risk Level"
              value="Low"
              change="Safe"
              color="cyan"
            />
          </div>

          {/* Agent strip */}
          <div className="p-3 rounded-xl bg-white/[0.04] border border-white/[0.07]">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-white/50">AI Agents</span>
              <span className="text-xs text-emerald-400 font-medium">8/9 Active</span>
            </div>
            <div className="flex gap-1.5">
              {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
                <motion.div
                  key={i}
                  className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500/80 to-purple-500/80 flex items-center justify-center"
                  animate={{ opacity: [0.6, 1, 0.6] }}
                  transition={{ duration: 2, repeat: Infinity, delay: i * 0.15 }}
                >
                  <Zap className="w-3 h-3 text-white" />
                </motion.div>
              ))}
              <div className="w-7 h-7 rounded-lg border border-dashed border-white/20" />
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

function MetricCard({
  icon, label, value, change, color,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  change: string;
  color: string;
}) {
  return (
    <motion.div
      className="p-3 rounded-xl bg-white/[0.04] border border-white/[0.07] hover:bg-white/[0.07] transition-colors"
      whileHover={{ y: -2 }}
    >
      <div className="flex items-start justify-between mb-1.5">
        {icon}
        <span className="text-xs text-white/35">{change}</span>
      </div>
      <div className="text-xl font-bold text-white">{value}</div>
      <div className="text-xs text-white/40">{label}</div>
    </motion.div>
  );
}
