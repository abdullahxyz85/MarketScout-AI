'use client';

import { motion } from 'framer-motion';
import {
  Search, Users, BarChart3, TrendingUp, Target, Lightbulb,
  ShieldAlert, FileText, Heart,
} from 'lucide-react';

const features = [
  { icon: Search, title: 'AI Research Agent', description: 'Autonomous research agents that gather and synthesize market data from thousands of sources in minutes.', color: 'from-indigo-500 to-purple-600', glow: 'rgba(99,102,241,0.25)' },
  { icon: Users, title: 'Competitor Analysis', description: 'Deep dive into competitors with AI-powered analysis of their strengths, weaknesses, and market strategies.', color: 'from-purple-500 to-pink-500', glow: 'rgba(168,85,247,0.25)' },
  { icon: BarChart3, title: 'Market Intelligence', description: 'Comprehensive market sizing, segmentation, and growth potential analysis tailored to your sector.', color: 'from-cyan-500 to-blue-500', glow: 'rgba(6,182,212,0.25)' },
  { icon: TrendingUp, title: 'SWOT Analysis', description: 'Automated SWOT analysis with insights tailored to your specific market positioning and target audience.', color: 'from-emerald-500 to-teal-500', glow: 'rgba(16,185,129,0.25)' },
  { icon: Target, title: 'Trend Detection', description: 'Identify emerging trends and market shifts before they become mainstream using predictive AI.', color: 'from-orange-500 to-amber-500', glow: 'rgba(249,115,22,0.25)' },
  { icon: Lightbulb, title: 'Opportunity Discovery', description: 'Uncover hidden market whitespace and high-potential opportunities your competitors have missed.', color: 'from-yellow-500 to-orange-500', glow: 'rgba(234,179,8,0.25)' },
  { icon: ShieldAlert, title: 'Risk Assessment', description: 'AI-powered risk analysis covering market, competitive, regulatory, and operational risks.', color: 'from-red-500 to-rose-600', glow: 'rgba(239,68,68,0.25)' },
  { icon: FileText, title: 'Report Generator', description: 'Generate beautiful, comprehensive market intelligence reports automatically in minutes.', color: 'from-indigo-500 to-blue-500', glow: 'rgba(99,102,241,0.25)' },
  { icon: Heart, title: 'Healthcare Mode', description: 'Specialized analysis for healthcare startups including FDA pathways and regulatory insights.', color: 'from-pink-500 to-rose-500', glow: 'rgba(236,72,153,0.25)' },
];

export function FeaturesSection() {
  return (
    <section id="features" className="py-28 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <p className="text-xs uppercase tracking-widest text-indigo-400 mb-3 font-medium">Capabilities</p>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4">
            Everything You Need for<br />
            <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">Deep Market Insights</span>
          </h2>
          <p className="text-lg text-white/50 max-w-2xl mx-auto">
            Our AI agents work together to deliver comprehensive market intelligence in the time it takes to get a coffee.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.07, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
            >
              <motion.div
                whileHover={{ y: -6, scale: 1.01 }}
                transition={{ type: 'spring', stiffness: 400, damping: 20 }}
                className="group relative h-full p-6 rounded-2xl border border-white/[0.07] bg-gradient-to-br from-white/[0.04] to-transparent backdrop-blur-sm overflow-hidden"
              >
                {/* Hover glow */}
                <div
                  className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-2xl"
                  style={{ background: `radial-gradient(circle at 50% 0%, ${feature.glow}, transparent 70%)` }}
                />
                <div className="absolute inset-0 border border-transparent group-hover:border-white/10 rounded-2xl transition-colors duration-300" />

                <div className="relative z-10">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 shadow-lg`}>
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                  <p className="text-sm text-white/50 leading-relaxed">{feature.description}</p>
                </div>
              </motion.div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

const trustedCompanies = ['Quantum Labs', 'NexGen AI', 'DeepTech', 'Velocity', 'AlphaCore', 'Synapse'];

export function TrustedBySection() {
  return (
    <section className="py-14 border-y border-white/[0.05]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-center text-xs text-white/30 mb-8 uppercase tracking-widest"
        >
          Trusted by innovative founders worldwide
        </motion.p>
        <div className="flex flex-wrap justify-center items-center gap-8 md:gap-14">
          {trustedCompanies.map((company, i) => (
            <motion.div
              key={company}
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              className="text-xl font-bold text-white/15 hover:text-white/35 transition-colors cursor-default tracking-tight"
            >
              {company}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
