'use client';

import { motion } from 'framer-motion';
import { Lightbulb, Search, Users, BarChart3, TrendingUp, Target, Zap, ShieldAlert, FileText, ArrowDown } from 'lucide-react';

const agents = [
  { name: 'Your Idea', icon: Lightbulb, color: 'from-yellow-400 to-orange-500', desc: 'Describe your startup concept' },
  { name: 'Research Agent', icon: Search, color: 'from-indigo-500 to-violet-600', desc: 'Gathers data from 1000s of sources' },
  { name: 'Competitor Agent', icon: Users, color: 'from-purple-500 to-pink-500', desc: 'Identifies and profiles competitors' },
  { name: 'Market Agent', icon: BarChart3, color: 'from-cyan-500 to-blue-600', desc: 'Calculates market size & growth' },
  { name: 'Trend Agent', icon: TrendingUp, color: 'from-emerald-500 to-teal-500', desc: 'Detects emerging market shifts' },
  { name: 'SWOT Agent', icon: Target, color: 'from-orange-500 to-red-500', desc: 'Generates SWOT framework' },
  { name: 'Opportunity Agent', icon: Zap, color: 'from-blue-500 to-indigo-600', desc: 'Uncovers hidden opportunities' },
  { name: 'Risk Agent', icon: ShieldAlert, color: 'from-red-500 to-rose-600', desc: 'Assesses threats and risks' },
  { name: 'Report Generator', icon: FileText, color: 'from-indigo-500 to-purple-600', desc: 'Compiles final intelligence report' },
];

export function WorkflowSection() {
  return (
    <section id="workflow" className="py-28 relative overflow-hidden">
      {/* Section glow */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[600px] bg-indigo-500/5 rounded-full blur-3xl" />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <p className="text-xs uppercase tracking-widest text-indigo-400 mb-3 font-medium">How It Works</p>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4">
            Multi-Agent <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">AI Workflow</span>
          </h2>
          <p className="text-lg text-white/50 max-w-2xl mx-auto">
            9 specialized agents work in sequence to build a complete market intelligence report from your idea.
          </p>
        </motion.div>

        {/* Mobile: vertical list */}
        <div className="lg:hidden space-y-3">
          {agents.map((agent, i) => (
            <motion.div
              key={agent.name}
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.07 }}
              className="flex items-center gap-4 p-4 rounded-2xl border border-white/[0.07] bg-white/[0.03] backdrop-blur-sm"
            >
              <motion.div
                className={`w-11 h-11 rounded-xl bg-gradient-to-br ${agent.color} flex items-center justify-center flex-shrink-0 shadow-lg`}
                whileHover={{ rotate: 8, scale: 1.1 }}
                animate={{ boxShadow: ['0 0 0px rgba(99,102,241,0)', '0 0 20px rgba(99,102,241,0.3)', '0 0 0px rgba(99,102,241,0)'] }}
                transition={{ duration: 3, repeat: Infinity, delay: i * 0.3 }}
              >
                <agent.icon className="w-5 h-5 text-white" />
              </motion.div>
              <div>
                <div className="text-sm font-semibold text-white">{agent.name}</div>
                <div className="text-xs text-white/40">{agent.desc}</div>
              </div>
              <div className="ml-auto text-xs text-white/25 font-mono">{String(i + 1).padStart(2, '0')}</div>
            </motion.div>
          ))}
        </div>

        {/* Desktop: 3-column grid with flow */}
        <div className="hidden lg:block">
          <div className="grid grid-cols-3 gap-6 relative">
            {/* Vertical connector center */}
            <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-indigo-500/0 via-indigo-500/30 to-indigo-500/0 -translate-x-1/2" />

            {agents.map((agent, i) => {
              const col = i % 3;
              const isCenter = col === 1;
              return (
                <motion.div
                  key={agent.name}
                  initial={{ opacity: 0, y: 30, scale: 0.95 }}
                  whileInView={{ opacity: 1, y: 0, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.08, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
                  style={{ gridColumn: col + 1 }}
                >
                  <motion.div
                    whileHover={{ y: -8, scale: 1.03 }}
                    transition={{ type: 'spring', stiffness: 400, damping: 20 }}
                    className={`group relative p-5 rounded-2xl border backdrop-blur-sm overflow-hidden h-full ${
                      isCenter
                        ? 'border-indigo-500/30 bg-gradient-to-br from-indigo-500/10 to-purple-500/5'
                        : 'border-white/[0.07] bg-white/[0.03] hover:border-white/[0.14]'
                    }`}
                  >
                    <div className="absolute top-3 right-3 text-xs font-mono text-white/20">
                      {String(i + 1).padStart(2, '0')}
                    </div>

                    <motion.div
                      className={`w-12 h-12 rounded-xl bg-gradient-to-br ${agent.color} flex items-center justify-center mb-3 shadow-lg`}
                      animate={{
                        boxShadow: [
                          '0 0 0px rgba(99,102,241,0)',
                          '0 0 25px rgba(99,102,241,0.4)',
                          '0 0 0px rgba(99,102,241,0)',
                        ],
                      }}
                      transition={{ duration: 3.5, repeat: Infinity, delay: i * 0.35 }}
                    >
                      <agent.icon className="w-6 h-6 text-white" />
                    </motion.div>

                    <h3 className="text-base font-semibold text-white mb-1">{agent.name}</h3>
                    <p className="text-xs text-white/45 leading-relaxed">{agent.desc}</p>

                    {i < agents.length - 1 && isCenter && (
                      <div className="absolute -bottom-3 left-1/2 -translate-x-1/2 z-10">
                        <motion.div
                          className="w-6 h-6 rounded-full bg-indigo-500/30 border border-indigo-500/50 flex items-center justify-center"
                          animate={{ y: [0, 4, 0] }}
                          transition={{ duration: 1.5, repeat: Infinity }}
                        >
                          <ArrowDown className="w-3 h-3 text-indigo-400" />
                        </motion.div>
                      </div>
                    )}
                  </motion.div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
