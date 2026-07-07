'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  Sparkles,
  ArrowRight,
  Zap,
  BarChart3,
  Users,
  TrendingUp,
  Target,
  ShieldAlert,
  FileText,
  Lightbulb,
  Clock,
  ChevronDown,
} from 'lucide-react';
import { GlassCard, GlassCardContent, GlassCardHeader } from '@/components/ui/glass-card';
import { AnimatedButton } from '@/components/ui/animated-button';
import { AnimatedBadge, StatusBadge } from '@/components/ui/animated-badge';
import { AnimatedProgress } from '@/components/ui/animated-progress';

const industries = [
  'Healthcare',
  'FinTech',
  'EdTech',
  'SaaS',
  'E-commerce',
  'AI/ML',
  'CleanTech',
  'Logistics',
];

const agents = [
  { name: 'Research Agent', icon: Search, color: 'from-indigo-500 to-purple-500', time: '~2 min' },
  { name: 'Competitor Agent', icon: Users, color: 'from-purple-500 to-pink-500', time: '~3 min' },
  { name: 'Market Agent', icon: BarChart3, color: 'from-cyan-500 to-blue-500', time: '~2 min' },
  { name: 'Trend Agent', icon: TrendingUp, color: 'from-emerald-500 to-teal-500', time: '~2 min' },
  { name: 'SWOT Agent', icon: Target, color: 'from-orange-500 to-red-500', time: '~1 min' },
  { name: 'Opportunity Agent', icon: Lightbulb, color: 'from-yellow-500 to-orange-500', time: '~2 min' },
  { name: 'Risk Agent', icon: ShieldAlert, color: 'from-red-500 to-rose-500', time: '~1 min' },
  { name: 'Report Generator', icon: FileText, color: 'from-indigo-500 to-blue-500', time: '~1 min' },
];

type Stage = 'input' | 'running' | 'done';

export default function ResearchPage() {
  const [idea, setIdea] = useState('');
  const [selectedIndustry, setSelectedIndustry] = useState('');
  const [stage, setStage] = useState<Stage>('input');
  const [activeAgent, setActiveAgent] = useState(0);
  const [progress, setProgress] = useState(0);

  const startResearch = () => {
    if (!idea.trim()) return;
    setStage('running');
    let agentIdx = 0;
    let pct = 0;

    const tick = setInterval(() => {
      pct += 2;
      setProgress(pct);
      if (pct % 14 === 0) {
        agentIdx = Math.min(agentIdx + 1, agents.length - 1);
        setActiveAgent(agentIdx);
      }
      if (pct >= 100) {
        clearInterval(tick);
        setStage('done');
      }
    }, 120);
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">
          New <span className="text-gradient">Research</span>
        </h1>
        <p className="text-white/50">Enter your startup idea and our AI agents will analyze the market</p>
      </div>

      <AnimatePresence mode="wait">
        {stage === 'input' && (
          <motion.div
            key="input"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Idea Input */}
            <GlassCard>
              <GlassCardHeader>
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-indigo-400" />
                  <h2 className="text-lg font-semibold text-white">Describe Your Startup Idea</h2>
                </div>
              </GlassCardHeader>
              <GlassCardContent>
                <textarea
                  value={idea}
                  onChange={(e) => setIdea(e.target.value)}
                  placeholder="e.g. An AI platform that helps hospitals reduce patient wait times by automating triage and resource allocation..."
                  className="w-full h-36 px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/30 focus:outline-none focus:border-indigo-500/60 resize-none text-sm leading-relaxed transition-colors"
                />
                <div className="mt-4">
                  <label className="text-sm text-white/60 mb-3 block">Select Industry</label>
                  <div className="flex flex-wrap gap-2">
                    {industries.map((ind) => (
                      <motion.button
                        key={ind}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setSelectedIndustry(ind)}
                        className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-all ${
                          selectedIndustry === ind
                            ? 'bg-indigo-500/30 border-indigo-500/60 text-indigo-300'
                            : 'bg-white/5 border-white/10 text-white/60 hover:text-white hover:border-white/30'
                        }`}
                      >
                        {ind}
                      </motion.button>
                    ))}
                  </div>
                </div>
              </GlassCardContent>
            </GlassCard>

            {/* Agents Preview */}
            <GlassCard>
              <GlassCardHeader>
                <h2 className="text-lg font-semibold text-white">AI Agents That Will Run</h2>
              </GlassCardHeader>
              <GlassCardContent>
                <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
                  {agents.map((agent, i) => (
                    <motion.div
                      key={agent.name}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: i * 0.05 }}
                      className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/10"
                    >
                      <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${agent.color} flex items-center justify-center flex-shrink-0`}>
                        <agent.icon className="w-4 h-4 text-white" />
                      </div>
                      <div>
                        <div className="text-xs font-medium text-white">{agent.name}</div>
                        <div className="text-xs text-white/40 flex items-center gap-1">
                          <Clock className="w-3 h-3" />{agent.time}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
                <div className="mt-4 flex items-center justify-between">
                  <p className="text-sm text-white/40">Total estimated time: ~14 minutes</p>
                  <AnimatedButton size="md" onClick={startResearch} disabled={!idea.trim()}>
                    Start Research <ArrowRight className="w-4 h-4" />
                  </AnimatedButton>
                </div>
              </GlassCardContent>
            </GlassCard>
          </motion.div>
        )}

        {stage === 'running' && (
          <motion.div
            key="running"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <GlassCard>
              <GlassCardContent className="text-center py-8">
                <motion.div
                  className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-cyan-500 flex items-center justify-center mb-6 shadow-glow"
                  animate={{ rotate: [0, 360] }}
                  transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
                >
                  <Zap className="w-10 h-10 text-white" />
                </motion.div>
                <h2 className="text-2xl font-bold text-white mb-2">Analyzing Your Idea</h2>
                <p className="text-white/50 mb-6 max-w-md mx-auto text-sm">
                  Our AI agents are working together to generate comprehensive market intelligence.
                </p>
                <div className="max-w-md mx-auto mb-6">
                  <div className="flex justify-between text-sm text-white/60 mb-2">
                    <span>Overall Progress</span>
                    <span>{progress}%</span>
                  </div>
                  <AnimatedProgress value={progress} variant="glow" />
                </div>
              </GlassCardContent>
            </GlassCard>

            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {agents.map((agent, i) => {
                const done = i < activeAgent;
                const active = i === activeAgent;
                return (
                  <motion.div
                    key={agent.name}
                    animate={active ? { scale: [1, 1.03, 1] } : {}}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  >
                    <GlassCard className={active ? 'border-indigo-500/40' : ''}>
                      <GlassCardContent className="py-4">
                        <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${agent.color} flex items-center justify-center mb-3 ${active ? 'shadow-glow' : ''}`}>
                          <agent.icon className="w-5 h-5 text-white" />
                        </div>
                        <div className="text-sm font-medium text-white mb-2">{agent.name}</div>
                        <StatusBadge status={done ? 'completed' : active ? 'running' : 'pending'} />
                      </GlassCardContent>
                    </GlassCard>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        )}

        {stage === 'done' && (
          <motion.div
            key="done"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="space-y-6"
          >
            <GlassCard className="border-emerald-500/30">
              <GlassCardContent className="text-center py-8">
                <motion.div
                  className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center mb-6"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                >
                  <FileText className="w-10 h-10 text-white" />
                </motion.div>
                <h2 className="text-2xl font-bold text-white mb-2">Research Complete!</h2>
                <p className="text-white/50 mb-6 text-sm">
                  Your market intelligence report is ready. Overall market score: <span className="text-emerald-400 font-bold">94.2</span>
                </p>
                <div className="flex gap-3 justify-center flex-wrap">
                  <AnimatedButton size="md">
                    <FileText className="w-4 h-4" /> View Report
                  </AnimatedButton>
                  <AnimatedButton variant="secondary" size="md" onClick={() => { setStage('input'); setIdea(''); setProgress(0); setActiveAgent(0); }}>
                    Start New Research
                  </AnimatedButton>
                </div>
              </GlassCardContent>
            </GlassCard>

            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { label: 'Market Score', value: '94.2', color: 'text-emerald-400' },
                { label: 'Opportunity', value: '87.8', color: 'text-indigo-400' },
                { label: 'Competitors', value: '24', color: 'text-purple-400' },
                { label: 'Risk Level', value: 'Low', color: 'text-cyan-400' },
              ].map((m, i) => (
                <motion.div
                  key={m.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                >
                  <GlassCard>
                    <GlassCardContent className="text-center py-4">
                      <div className={`text-3xl font-bold ${m.color} mb-1`}>{m.value}</div>
                      <div className="text-sm text-white/50">{m.label}</div>
                    </GlassCardContent>
                  </GlassCard>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
